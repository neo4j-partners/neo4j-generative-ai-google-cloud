import streamlit as st
from streamlit_chat import message
from streamlit.components.v1 import html
from english2results import get_results
from timeit import default_timer as timer
from ui_utils import render_header_svg
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache

set_llm_cache(InMemoryCache())

# Hardcoded UserID
USER_ID = "bot"

st.set_page_config(page_icon="images/logo-mark-fullcolor-RGB-transBG.svg", layout="wide")

render_header_svg("images/cypher-top-header.svg", 350)

render_header_svg("images/bottom-header.svg", 200)

def generate_context(prompt, context_data='generated'):
    context = []
    # If any history exists
    if st.session_state['generated']:
        # Add the last three exchanges
        size = len(st.session_state['generated'])
        for i in range(max(size-3, 0), size):
            context.append(st.session_state['user_input'][i])
            if len(st.session_state[context_data]) > i:
                context.append(st.session_state[context_data][i])
    # Add the latest user prompt
    context.append(str(prompt))
    return context


# Generated natural language
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
# Neo4j database results
if 'database_results' not in st.session_state:
    st.session_state['database_results'] = []
# User input
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = []
# Generated Cypher statements
if 'cypher' not in st.session_state:
    st.session_state['cypher'] = []


def get_text():
    input_text = st.text_input(
        "Ask away", "", key="input")
    return input_text


# Define columns
col1, col2 = st.columns([2, 1])

with col2:
    another_placeholder = st.empty()
with col1:
    placeholder = st.empty()
user_input = get_text()


if user_input:
    start = timer()
    try:
        results = get_results(generate_context(user_input, 'database_results'))
        cypher_step = results['intermediate_steps']
        print('Total Time : {}'.format(timer() - start))
        if len(cypher_step) > 0 and 'query' in cypher_step[0]:
            st.session_state.cypher.append(cypher_step[0]['query'])
        else :
            st.session_state.cypher.append('')
        if len(cypher_step) > 1 and 'context' in cypher_step[1] and len(cypher_step[1]['context']) > 0:
            st.session_state.database_results.append(cypher_step[1]['context'][0])
        else:
            st.session_state.database_results.append('')
        st.session_state.user_input.append(user_input)
        st.session_state.generated.append(results['result'])
    except Exception as ex:
        print(ex)
        st.session_state.user_input.append(user_input)
        st.session_state.generated.append("Could not generate result due to an error or LLM Quota exceeded")
        st.session_state.cypher.append("")
        st.session_state.database_results.append('{}')


# Message placeholder
with placeholder.container():
    if st.session_state['generated']:
        size = len(st.session_state['generated'])
        # Display only the last three exchanges
        for i in range(max(size-3, 0), size):
            message(st.session_state['user_input'][i],
                    is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))


# Generated Cypher statements
with another_placeholder.container():
    if st.session_state['cypher']:
        st.text_area("Latest generated Cypher statement",
                     st.session_state['cypher'][-1], height=240)
        

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
    <td>Which of the managers own Nvidia?</td>
    <td>If a manager owns Apple, do they also buy Nvidia?</td>
    <td>how many managers own more than 100 companies and who are they?</td>
  </tr>
  <tr>
    <td>Which manager own any FAANG stocks?</td>
    <td>What is the shortest path between Amazon and Pubmatic?</td>
    <td>What is the shortest path between Apple and Boeing? Go until 2 hops</td>
  </tr>
  <tr>
    <td></td>
    <td></td>
  </tr>
</table>
""", unsafe_allow_html=True)
