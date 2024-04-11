import json

from langchain.prompts.prompt import PromptTemplate
from retry import retry
from timeit import default_timer as timer
import streamlit as st
import ingestion.llm_util as llm_util
from vertexai.language_models import TextEmbeddingModel
from neo4j_driver import run_query
from json import loads
import yaml

llm_util.init()

emb_model_name = st.secrets["EMBEDDING_MODEL"]

SYSTEM_PROMPT = """You are a Financial expert with SEC filings who can answer questions only based on the context below."""
PROMPT_TEMPLATE = """< Instructions >
< Question >
{input}

< Constraints >
1. Answer the question based on the context provided in JSON below.
2. Do not assume or retrieve any information outside of the context 
3. List the results in rich text format if there are more than one results
4. If the context is empty, just respond None

Here is the context in JSON format. Note that company's are not considered asset managers in this dataset, 
and form10ks don't include asset manager information. Where asset manager info is made explicitly available, 
you can assume the mentioned asset managers are impacted by the same things as the companies. 

< Context >
{context} 
"""

PROMPT = PromptTemplate(
    input_variables=["input", "context"], template=PROMPT_TEMPLATE
)

EMBEDDING_MODEL = TextEmbeddingModel.from_pretrained(emb_model_name)


def vector_only_qa(query):
    query_vector = EMBEDDING_MODEL.get_embeddings([query])
    return run_query("""
    CALL db.index.vector.queryNodes('document-embeddings', 50, $queryVector)
    YIELD node AS doc, score
    MATCH(doc)<-[:HAS]-(c:Company)
    RETURN c.companyName AS companyName, doc.text AS company10kInfo, score
    ORDER BY score DESC LIMIT 10
    """, params={'queryVector': query_vector[0].values})


def df_to_context(df):
    result = df.to_json(orient="records")
    parsed = loads(result)
    text = json.dumps(parsed, indent=1)
    return text


@retry(tries=1)
def get_results(question):
    start = timer()
    try:
        df = vector_only_qa(question)
        ctx = df_to_context(df)
        ans = PROMPT.format(input=question, context=ctx)
        result = llm_util.call_text_model(ans, SYSTEM_PROMPT)
        r = {'context': ctx, 'result': result}
        return r
    finally:
        print('Generation Time : {}'.format(timer() - start))
