import streamlit as st

st.set_page_config(
    page_title="SEC EDGAR Filings - Neo4j Bloom",
    page_icon="images/logo-mark-fullcolor-RGB-transBG.svg",
    layout="wide",
)

placeholder = st.empty()

with placeholder.container():
    st.markdown("""
        <style>
            iframe {
                position: fixed;
                background: #000;
                border: none;
                top: 10; right: 0;
                bottom: 0; left: 0;
                width: 100%;
                height: 100%;
            }
        </style>
        <iframe 
            src="https://workspace-preview.neo4j.io/workspace/explore" 
            frameborder="10" style="overflow:hidden;height:92%;width:100%" 
            height="100%" width="100%" title="Bloom">
        </iframe>
    """, unsafe_allow_html=True)
