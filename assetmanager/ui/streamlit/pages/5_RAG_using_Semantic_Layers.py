import streamlit as st
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache
from rag_semantic_layer import get_results
import streamlit as st

set_llm_cache(InMemoryCache())

st.set_page_config(
    page_title="RAG using Semantic Layers",
    page_icon="images/logo-mark-fullcolor-RGB-transBG.svg",
    layout="wide",
)

st.title("RAG using Semantic Layers")

def rag_sl(question):
  res = get_results(question)
  st.markdown(res['result'])
  with st.expander("Context:"):
    st.json(res['context'])

question = st.text_input("Ask question on the SEC Filings", value="")

if question:
  with st.spinner('Running RAG using Semantic Layers ...'):
      rag_sl(question)
      st.success('Done!')

st.markdown("---")

st.markdown("""
<style>
  table {
    width: 100%;
    border-collapse: collapse;
    border: none !important;
    font-family: "Source Sans Pro", sans-serif;
    color: rgba(49, 51, 63, 0.6);
    font-size: 0.9rem;
  }

  tr {
    border: none !important;
  }
  
  th {
    text-align: center;
    colspan: 3;
    border: none !important;
    color: #0F9D58;
  }
  
  th, td {
    padding: 2px;
    border: none !important;
  }
</style>

<table>
  <tr>
    <th colspan="3">Sample Questions to try out</th>
  </tr>
  <tr>
    <td>Tell me about Arbor Capital</td>
    <td>Who owns Nvidia?</td>
    <td>Which asset managers have investments in companies that have businesses outside USA?</td>
  </tr>
  <tr>
    <td>What is the shortest path between Amazon and Pubmatic?</td>
    <td>Which wealth managers are vulnerable to lithium shortage?</td>
    <td>If I have to invest in all of FAANG, which asset manager can I invest?</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
  </tr>
</table>
""", unsafe_allow_html=True)