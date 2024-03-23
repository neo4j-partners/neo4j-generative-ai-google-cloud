from langchain.chains import GraphCypherQAChain
from langchain_community.graphs import Neo4jGraph
from langchain.prompts.prompt import PromptTemplate
from langchain_google_vertexai import VertexAI
from retry import retry
from timeit import default_timer as timer
import streamlit as st
import ingestion.llm_util as llm_util

llm_util.init()

host = st.secrets["NEO4J_HOST"]+":"+st.secrets["NEO4J_PORT"]
user = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASSWORD"]
db = st.secrets["NEO4J_DB"]

code_model_name = st.secrets["CYPHER_MODEL"]
    

CYPHER_GENERATION_TEMPLATE = """You are an expert Neo4j Cypher translator who understands the question in english and convert to Cypher strictly based on the Neo4j Schema provided and following the instructions below:
1. Generate Cypher query compatible ONLY for Neo4j Version 5
2. Do not use EXISTS, SIZE keywords in the cypher. Use alias when using the WITH keyword
3. Please do not use same variable names for different nodes and relationships in the query.
4. Use only Nodes and relationships mentioned in the schema
5. Always enclose the Cypher output inside 3 backticks
6. Always do a case-insensitive and fuzzy search for any properties related search. Eg: to search for a Company name use `toLower(c.name) contains 'neo4j'`
7. Candidate node is synonymous to Manager
8. Always use aliases to refer the node in the query
9. 'Answer' is NOT a Cypher keyword. Answer should never be used in a query.
10. Please generate only one Cypher query per question. 
11. Cypher is NOT SQL. So, do not mix and match the syntaxes.
12. Every Cypher query always starts with a MATCH keyword.

Schema:
{schema}
Samples:
Question: Which fund manager owns most shares? What is the total portfolio value?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) RETURN m.managerName as manager, sum(distinct o.shares) as ownedShares, sum(o.value) as portfolioValue ORDER BY ownedShares DESC LIMIT 10

Question: Which fund manager owns most companies? How many shares?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) RETURN m.managerName as manager, count(distinct c) as ownedCompanies, sum(distinct o.shares) as ownedShares ORDER BY ownedCompanies DESC LIMIT 10

Question: What are the top 10 investments for Vanguard?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE toLower(m.managerName) contains "vanguard" RETURN c.companyName as Investment, sum(DISTINCT o.shares) as totalShares, sum(DISTINCT o.value) as investmentValue order by investmentValue desc limit 10

Question: What other fund managers are investing in same companies as Vanguard?
Answer: MATCH (m1:Manager) -[:OWNS]-> (c1:Company) <-[o:OWNS]- (m2:Manager) WHERE toLower(m1.managerName) contains "vanguard" AND elementId(m1) <> elementId(m2) RETURN m2.managerName as manager, sum(DISTINCT o.shares) as investedShares, sum(DISTINCT o.value) as investmentValue ORDER BY investmentValue LIMIT 10

Question: What are the top investors for Apple?
Answer: MATCH (m1:Manager) -[o:OWNS]-> (c1:Company) WHERE toLower(c1.companyName) contains "apple" RETURN distinct m1.managerName as manager, sum(o.value) as totalInvested ORDER BY totalInvested DESC LIMIT 10

Question: What are the other top investments for fund managers investing in Apple?
Answer: MATCH (c1:Company) <-[:OWNS]- (m1:Manager) -[o:OWNS]-> (c2:Company) WHERE toLower(c1.companyName) contains "apple" AND elementId(c1) <> elementId(c2) RETURN DISTINCT c2.companyName as company, sum(o.value) as totalInvested, sum(o.shares) as totalShares ORDER BY totalInvested DESC LIMIT 10

Question: What are the top investors in the last 3 months?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE date() > o.reportCalendarOrQuarter > o.reportCalendarOrQuarter - duration({{months:3}}) RETURN distinct m.managerName as manager, sum(o.value) as totalInvested, sum(o.shares) as totalShares ORDER BY totalInvested DESC LIMIT 10

Question: What are top investments in last 6 months for Vanguard?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE toLower(m.managerName) contains "vanguard" AND date() > o.reportCalendarOrQuarter > date() - duration({{months:6}}) RETURN distinct c.companyName as company, sum(o.value) as totalInvested, sum(o.shares) as totalShares ORDER BY totalInvested DESC LIMIT 10

Question: Who are Apple's top investors in last 3 months?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE toLower(c.companyName) contains "apple" AND date() > o.reportCalendarOrQuarter > date() - duration({{months:3}}) RETURN distinct m.managerName as investor, sum(o.value) as totalInvested, sum(o.shares) as totalShares ORDER BY totalInvested DESC LIMIT 10

Question: Which fund manager under 200 million has similar investment strategy as Vanguard?
Answer: MATCH (m1:Manager) -[o1:OWNS]-> (:Company) <-[o2:OWNS]- (m2:Manager) WHERE toLower(m1.managerName) CONTAINS "vanguard" AND elementId(m1) <> elementId(m2) WITH distinct m2 AS m2, sum(distinct o2.value) AS totalVal WHERE totalVal < 200000000 RETURN m2.managerName AS manager, totalVal*0.000001 AS totalVal ORDER BY totalVal DESC LIMIT 10

Question: Who are common investors in Apple and Amazon?
Answer: MATCH (c1:Company) <-[:OWNS]- (m:Manager) -[:OWNS]-> (c2:Company) WHERE toLower(c1.companyName) contains "apple" AND toLower(c2.companyName) CONTAINS "amazon" RETURN DISTINCT m.managerName LIMIT 50

Question: What are Vanguard's top investments by shares for 2023?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE toLower(m.managerName) CONTAINS "vanguard" AND date({{year:2023}}) = date.truncate('year',o.reportCalendarOrQuarter) RETURN c.companyName AS investment, sum(o.value) AS totalValue ORDER BY totalValue DESC LIMIT 10

Question: What are Vanguard's top investments by value for 2023?
Answer: MATCH (m:Manager) -[o:OWNS]-> (c:Company) WHERE toLower(m.managerName) CONTAINS "vanguard" AND date({{year:2023}}) = date.truncate('year',o.reportCalendarOrQuarter) RETURN c.companyName AS investment, sum(o.shares) AS totalShares ORDER BY totalShares DESC LIMIT 10

Question: What is the shortest path between Amazon and Pubmatic? Go until 2 hops
Answer: MATCH p=shortestPath((a:Company)-[*1..2]-(b:Company)) WHERE toLower(a.companyName) CONTAINS 'amazon' AND toLower(b.companyName) CONTAINS 'pubmatic' RETURN p

Question: {question}
Answer:"""
CYPHER_GENERATION_PROMPT = PromptTemplate(
    input_variables=["schema","question"], template=CYPHER_GENERATION_TEMPLATE
)

SYSTEM_PROMPT = """You are a Financial expert with SEC filings who can answer questions only based on the context below.
"""

@retry(tries=5, delay=5)
def get_results(messages):
    start = timer()
    try:
        graph = Neo4jGraph(
            url=host, 
            username=user, 
            password=password
        )
        code_llm = VertexAI(
            model_name=code_model_name, cache=False, 
            max_output_tokens=2048, temperature=0.0,
            top_k=1, top_p=0.1)
        chain = GraphCypherQAChain.from_llm(
            code_llm, 
            graph=graph, verbose=True,
            return_intermediate_steps=True,
            cypher_prompt=CYPHER_GENERATION_PROMPT,
            return_direct=True
        )
        if messages:
            question = messages.pop()
        else: 
            question = ''
        r = chain(question)
        prompt = f"""Human: 
            Fact: {r['result']}

            * Summarise the above fact as if you are answering this question "{r['query']}"
            * When the fact is not empty, assume the question is valid and the answer is true
            * Do not return helpful or extra text or apologies
            * Just return summary to the user. DO NOT start with Here is a summary
            * List the results in rich text format if there are more than one results
            * If the facts are empty, just respond None
            Assistant:
        """
        result = llm_util.call_text_model(prompt)
        r['context'] = r['result']
        r['result'] = result
        return r
    # except Exception as ex:
    #     print(ex)
    #     return "LLM Quota Exceeded. Please try again"
    finally:
        print('Cypher Generation Time : {}'.format(timer() - start))


