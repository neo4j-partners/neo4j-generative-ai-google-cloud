import os
from neo4j import GraphDatabase
import streamlit as st

host = st.secrets["NEO4J_HOST"]+":"+st.secrets["NEO4J_PORT"]
user = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASSWORD"]
db = st.secrets["NEO4J_DB"]
driver = GraphDatabase.driver(host, auth=(user, password))

def run_query(query, params={}):
    with driver.session(database=db) as session:
        try:
            result = session.run(query, params)
            response = [r.values()[0] for r in result]
            return response
        except Exception as e:
            print(e)
            return ["Something wrong with the Cypher or LLM token limit exceeded. Please try again!"]



if __name__ == '__main__':
    print(run_query("""
    MATCH (a:Case {name:$title}) RETURN a.bodyContent as response
    """))
