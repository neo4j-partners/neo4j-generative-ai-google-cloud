from langchain.text_splitter import RecursiveCharacterTextSplitter
import ingestion.llm_util as llm_util
from vertexai.language_models import TextEmbeddingModel
import json
import pandas as pd
import streamlit as st
from graphdatascience import GraphDataScience
import traceback

llm_util.init()

emb_model_name = st.secrets["EMBEDDING_MODEL"]
if emb_model_name == '':
    emb_model_name = 'textembedding-gecko@002'

EMBEDDING_MODEL = TextEmbeddingModel.from_pretrained(emb_model_name)

host = st.secrets["NEO4J_HOST"]+":"+st.secrets["NEO4J_PORT"]
user = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASSWORD"]
db = st.secrets["NEO4J_DB"]

gds = GraphDataScience(
    st.secrets["NEO4J_HOST"],
    auth=(user, password),
    aura_ds=True)

gds.set_database("neo4j")

def chunks(xs, n=3):
    n = max(1, n)
    return [xs[i:i + n] for i in range(0, len(xs), n)]

def create_text_embedding_entries(input_text:str, company_name: str, cusip: str):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size = 2000,
        chunk_overlap  = 15,
        length_function = len,
    )
    docs = text_splitter.split_text(input_text)
    res = []
    seq_id = -1
    for d in chunks(docs):
        embeddings = EMBEDDING_MODEL.get_embeddings(d)
        for i in range(len(d)):
            seq_id += 1
            res.append({'companyName': company_name, 'cusip': cusip, 'seqId': seq_id, 'contextId': company_name + str(seq_id), 'textEmbedding': embeddings[i].values, 'text': d[i]})
    return res

def run_pipeline(edgar_text):
    try:
        f10_k = json.loads(edgar_text)
        emb = []
        emb.extend(create_text_embedding_entries(f10_k['item1'], f10_k['companyName'], f10_k['cusip']))
        edf = pd.DataFrame(emb)
        emb_entries = edf.to_dict(orient='records')
        count = 0
        for d in chunks(emb_entries, 100):
            recs = json.loads(json.dumps(d))
            done = gds.run_cypher("""UNWIND $records AS record
            MATCH(c:Company {cusip: record.cusip})
            MERGE(b:Document {documentId: record.contextId})
            ON CREATE SET
              b.documentId = record.contextId,
              b.documentType = 'FORM_10K_ITEM1', b.seqId = record.seqId, 
              b.textEmbedding = record.textEmbedding, b.text = record.text
            MERGE(c)-[r:HAS]->(b)
            RETURN count(b) as cnt
            """, params = {'records': recs})['cnt'][0]
            count += done
        return f'Ingested the Document as {count} chunks'
    except Exception as e:
        traceback.print_exc()
        return None
        
    
