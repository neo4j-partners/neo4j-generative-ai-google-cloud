from langchain.prompts.prompt import PromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_google_vertexai import ChatVertexAI
from vertexai.language_models import TextEmbeddingModel
from retry import retry
from timeit import default_timer as timer
import streamlit as st
import json
import ingestion.llm_util as llm_util
from graphdatascience import GraphDataScience

llm_util.init()

host = st.secrets["NEO4J_HOST"]+":"+st.secrets["NEO4J_PORT"]
user = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASSWORD"]
db = st.secrets["NEO4J_DB"]

gds = GraphDataScience(
    st.secrets["NEO4J_HOST"],
    auth=(user, password),
    aura_ds=True)

gds.set_database(db)

model_name = st.secrets["SUMMARY_MODEL"]
if model_name == '':
    model_name = 'gemini-1.0-pro-001'

emb_model_name = st.secrets["EMBEDDING_MODEL"]
if emb_model_name == '':
    emb_model_name = 'textembedding-gecko@002'
    

SYSTEM_PROMPT = """You are an expert with Aviation Industry who can answer questions only based on the context below.
* Answer the question STRICTLY based on the context provided in JSON below.
* The context is a part of the DAG flow. So consider the sequence as well before answering
* Do NOT ASSUME or go beyond and retrieve any information outside of the context
* Think step by step before answering. Add explanation section at the end of your answer and explain clearly why you arrived at the conclusion
* When you see a date in the relationship label property, use it to compare against the relevant Human input
* Do not return helpful or extra text or apologies
* List the results in rich text format if there are more than one results
* Please do not expose relationship id or node id or any field in JSON that is not human readable
* Provide the step text description instead of saying as say 'Step 5'
* Provide clear answers. Do not answer asking the Human `to proceed to any step`. Assume the human will not be able to look at the process flow themselves.
* Provide direct answers and avoid using the phrase 'proceed to step', 'follow the step' or similar
"""

PROMPT_TEMPLATE = """
Question: {input}

Here is the related context of the process flow DAG in JSON:
{context}
"""
PROMPT = PromptTemplate(
    input_variables=["input","context"], template=PROMPT_TEMPLATE
)

EMBEDDING_MODEL = TextEmbeddingModel.from_pretrained(emb_model_name)

def vector_graph_qa(query):
    query_vector = EMBEDDING_MODEL.get_embeddings([query])
    return gds.run_cypher("""
    CALL db.index.vector.queryNodes('process-flow-emb', 2, $queryVector)
    YIELD node AS startNode, score
    WHERE NOT startNode:Start
    CALL apoc.path.subgraphAll(startNode, {
        minLevel: 0,
        maxLevel: 20,
        bfs: false
    })
    YIELD nodes, relationships
    RETURN nodes, relationships, score
    ORDER BY score DESC LIMIT 100
    """, params =  {'queryVector': query_vector[0].values})

def df_to_context(df):
    result = df.to_json(orient="records")
    parsed = json.loads(result)
    return json.dumps(parsed)

@retry(tries=5, delay=5)
def get_results(question):
    start = timer()
    try:
        llm = ChatVertexAI(
            model_name=model_name,
            model_kwargs = {
                "temperature":0,
                "top_k":1, "top_p":0.1,
                "max_tokens": 50000
            },
            convert_system_message_to_human = True
        )
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

def reset_db():
    try:
        c = gds.run_cypher("MATCH (n:Step) WHERE n.seed IS NULL DETACH DELETE n")
        print(c)
    except Exception as e:
        print(e)
    finally:
        print('DB Cleared')



