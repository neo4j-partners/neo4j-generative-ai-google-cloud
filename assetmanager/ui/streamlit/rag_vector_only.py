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
    
SYSTEM_PROMPT = """You are a Financial expert with SEC filings who can answer questions only based on the context below.
* Answer the question based on the context provided in JSON below.
* Do not assume or retrieve any information outside of the context 
* List the results in rich text format if there are more than one results
* If the context is empty, just respond None

"""
PROMPT_TEMPLATE = """
<question>
{input}
</question>

Here is the context in YAML format:
<context>
{context}
</context>
"""

PROMPT = PromptTemplate(
    input_variables=["input","context"], template=PROMPT_TEMPLATE
)

EMBEDDING_MODEL = TextEmbeddingModel.from_pretrained(emb_model_name)
def vector_only_qa(query):
    query_vector = EMBEDDING_MODEL.get_embeddings([query])
    return run_query("""
    CALL db.index.vector.queryNodes('document-embeddings', 50, $queryVector)
    YIELD node AS doc, score
    RETURN doc.text as text
    ORDER BY score DESC LIMIT 10
    """, params =  {'queryVector': query_vector[0].values})

def df_to_context(df):
    result = df.to_json(orient="records")
    parsed = loads(result)
    text = yaml.dump(
    parsed,
    sort_keys=False, indent=1,
    default_flow_style=None)
    return text

@retry(tries=1)
def get_results(question):
    start = timer()
    try:
        df = vector_only_qa(question)
        ctx = df_to_context(df)
        ans = PROMPT.format(input=question, context=ctx)
        result = llm_util.call_text_model(ans, SYSTEM_PROMPT)
        r = {}
        r['context'] = ans
        r['result'] = result
        return r
    finally:
        print('Generation Time : {}'.format(timer() - start))
