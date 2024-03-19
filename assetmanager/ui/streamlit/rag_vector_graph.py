from langchain.prompts.prompt import PromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_google_vertexai import VertexAI
from retry import retry
from timeit import default_timer as timer
import streamlit as st
import ingestion.llm_util as llm_util
from vertexai.language_models import TextEmbeddingModel
from neo4j_driver import run_query
from json import loads, dumps

llm_util.init()

model_name = st.secrets["SUMMARY_MODEL"]
if model_name == '':
    model_name = 'text-bison@002'


emb_model_name = st.secrets["EMBEDDING_MODEL"]
if emb_model_name == '':
    emb_model_name = 'textembedding-gecko@002'


SYSTEM_PROMPT = """You are a Financial expert with SEC filings who can answer questions only based on the context below.
* Answer the question STRICTLY based on the context provided in JSON below.
* Do not assume or retrieve any information outside of the context 
* Use three sentences maximum and keep the answer concise
* List the results in rich text format if there are more than one results
* If the context is empty, just respond None
* Do NOT assume. So no extraneous information in the response
"""

PROMPT_TEMPLATE = """
Question: {input}

Here is the fact in JSON format:
{context}
"""
PROMPT = PromptTemplate(
    input_variables=["input","context"], template=PROMPT_TEMPLATE
)

EMBEDDING_MODEL = TextEmbeddingModel.from_pretrained(emb_model_name)
def vector_graph_qa(query):
    query_vector = EMBEDDING_MODEL.get_embeddings([query])
    return run_query("""
    CALL db.index.vector.queryNodes('document-embeddings', 50, $queryVector)
    YIELD node AS doc, score
    OPTIONAL MATCH (doc)<-[:HAS]-(company:Company), (company)<-[:OWNS]-(manager:Manager)
    RETURN company.companyName AS company, doc.text as annual_report_text_chunk, manager.managerName as owning_asset_manager, avg(score) AS score
    ORDER BY score DESC LIMIT 50
    """, params =  {'queryVector': query_vector[0].values})

def df_to_context(df):
    result = df.to_json(orient="records")
    parsed = loads(result)
    return dumps(parsed)

@retry(tries=5, delay=5)
def get_results(question):
    start = timer()
    try:
        llm = VertexAI(
            model_name=model_name, 
            max_output_tokens=8000, temperature=0.0)
        df = vector_graph_qa(question)
        ctx = df_to_context(df)
        ans = PROMPT.format(input=question, context=ctx)
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=ans
            )
        ]
        result = llm.invoke(messages)
        r = {}
        r['context'] = ans
        r['result'] = result
        return r
    finally:
        print('Cypher Generation Time : {}'.format(timer() - start))


