from vertexai.generative_models import (
    FunctionDeclaration,
    Tool,
)
from neo4j_driver import run_query
from vertexai.language_models import TextEmbeddingModel
import streamlit as st
from semantic_layer.utils import get_candidates

emb_model_name = st.secrets["EMBEDDING_MODEL"]
EMBEDDING_MODEL = TextEmbeddingModel.from_pretrained(emb_model_name)

get_company_or_asset_manager_name = FunctionDeclaration(
    name="get_company_or_asset_manager_name",
    description="Get the Company or Asset Manager Name mentioned in the text",
    parameters={
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Company or Asset Manager name mentioned in the text"}
        },
    },
)

get_shortest_path_between_two_companies = FunctionDeclaration(
    name="get_shortest_path_between_two_companies",
    description="Get the Shortest Path between 2 companies mentioned in the text",
    parameters={
        "type": "object",
        "properties": {
            "company1": {"type": "string", "description": "Company 1 Name"},
            "company2": {"type": "string", "description": "Company 2 Name"}
        },
    },
)

get_common_investors_for_multiple_companies = FunctionDeclaration(
    name="get_common_investors_for_multiple_companies",
    description="Get the common investors for more than one companies mentioned in the text",
    parameters={
        "type": "object",
        "properties": {
            "companies": {"type": "array", "description": "List of company names"}
        },
    },
)

def run_vector_search(query):
    query_vector = EMBEDDING_MODEL.get_embeddings([query])
    return run_query(f"""
        CALL db.index.vector.queryNodes('document-embeddings', 50, $queryVector)
            YIELD node AS doc, score
        OPTIONAL MATCH (doc)<-[:HAS]-(c:Company)<-[o:OWNS]-(manager:Manager)
        RETURN c.companyName AS company, 
            collect('Asset Manager: ' + manager.managerName + '\nNo. of Shares: ' + toString(o.shares) 
                             + '\nReport Date: ' + toString(o.reportCalendarOrQuarter)) AS assetManagerInfo, 
            doc.text AS companyAnnualReportChunk, score
        ORDER BY score DESC LIMIT 10
    """, params={'queryVector':query_vector[0].values})


def get_company_or_asset_manager_name_fn(query, args):
    candidates = get_candidates(args['name'], 'company')
    if len(candidates) == 0:
        candidates = get_candidates(args['name'], 'manager')
    if len(candidates) == 0:
        return run_vector_search(query)
    name = candidates['candidate'][0]
    return run_query(f"""
        MATCH (c:Company|Manager)
        WHERE toLower(c.companyName) CONTAINS toLower("{name}") OR 
        toLower(c.managerName) CONTAINS toLower("{name}")
        MATCH (c)-[r:OWNS|HAS|HAS_ADDRESS]-(t)
        WITH c, CASE
             WHEN type(r) = 'OWNS' AND coalesce(t.managerName, '') <> '' THEN 'OWNED_BY_ASSET_MANAGERS'
             ELSE 'OWNS_COMPANIES'
         END AS type, collect(coalesce(t.companyName, t.managerName)) as names
        WITH c, type+": "+reduce(s="", n IN names | s + n + ", ") as types
        WITH c, collect(types) as contexts
        WITH c, "type:" + labels(c)[0] + "\nname: "+ coalesce(c.companyName, c.managerName)
               + "\nannual_report_chunk: "+coalesce(c.text,"") +"\n" +
               reduce(s="", c in contexts | s + substring(c, 0, size(c)-2) +"\n") as context
        RETURN context LIMIT 1
    """)


def get_shortest_path_between_two_companies_fn(query, args):
    company1 = args['company1']
    company2 = args['company2']
    company1_candidates = get_candidates(company1, 'company')
    if len(company1_candidates) > 0:
        company2_candidates = get_candidates(company2, 'company')
    if len(company2_candidates) == 0:
        return 'None'
    company1_name = company1_candidates['candidate'][0]
    company2_name = company2_candidates['candidate'][0]
    return run_query(f"""
        MATCH p=shortestPath((a:Company|Manager)-[*1..30]-(b:Company|Manager)) 
        WHERE toLower(coalesce(a.companyName, a.managerName)) = toLower("{company1_name}") AND 
        toLower(coalesce(b.companyName, b.managerName)) = toLower("{company2_name}") 
        RETURN "type:" + labels(a)[0] + "\npath: " + 
        reduce(s=coalesce(head(nodes(p)).companyName, head(nodes(p)).managerName), 
            n in tail(nodes(p)) | s+" -> "+coalesce(n.companyName, n.managerName)) as context
    """)


def get_common_investors_for_multiple_companies_fn(query, args):
    companies = args['companies']
    candidates = []
    for c in companies:
        _candidates = get_candidates(c, 'company')
        if len(_candidates) > 0:
            candidates.append(_candidates['candidate'][0])
    if len(candidates) < 2:
        return 'None'
    return run_query(f"""
        MATCH (m:Manager)-[:OWNS]->(c:Company)
        WHERE c.companyName IN $companies
        WITH m, COLLECT(c.companyName) AS companies_invested
        WHERE ALL(company IN $companies WHERE company IN companies_invested)
        RETURN "Asset Manager: "+ m.managerName + "\nCompanies Owned: " + $companies as context
        LIMIT 1
    """, params={'companies':candidates})

sec_tool = Tool(
    function_declarations=[
        get_company_or_asset_manager_name,
        get_shortest_path_between_two_companies,
        get_common_investors_for_multiple_companies
    ],
)
tpl_fn = {
    "get_company_or_asset_manager_name": get_company_or_asset_manager_name_fn,
    "get_shortest_path_between_two_companies": get_shortest_path_between_two_companies_fn,
    "get_common_investors_for_multiple_companies": get_common_investors_for_multiple_companies_fn
}