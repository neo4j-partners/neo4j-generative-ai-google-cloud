from graphdatascience import GraphDataScience

import streamlit as st

host = st.secrets["NEO4J_HOST"]+":"+st.secrets["NEO4J_PORT"]
user = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASSWORD"]
db = st.secrets["NEO4J_DB"]

gds = GraphDataScience(
    st.secrets["NEO4J_HOST"],
    auth=(user, password),
    aura_ds=True)

gds.set_database("neo4j")

def run_query(query, params = {}):
    return gds.run_cypher(query, params)
