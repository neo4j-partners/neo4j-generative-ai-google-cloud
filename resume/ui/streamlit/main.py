import streamlit as st
import vertexai
from streamlit_chat import message

from english2results import get_results
from timeit import default_timer as timer

vertexai.init(project=st.secrets["GCP_PROJECT"], 
              location=st.secrets["GCP_LOCATION"])

# Hardcoded UserID
USER_ID = "bot"

st.set_page_config(layout="wide")
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Roboto&display=swap');
    </style>
    <div style='text-align: center; font-size: 2.5rem; font-weight: 600; font-family: "Roboto"; color: #018BFF; line-height:1; '>Talent Finder Bot</div>
    <div style='text-align: center; font-size: 1.5rem; font-weight: 300; font-family: "Roboto"; color: rgb(179 185 182); line-height:0; '>
        Powered by <svg width="80" height="60" xmlns="http://www.w3.org/2000/svg" id="Layer_1" data-name="Layer 1" viewBox="0 0 200 75"><path d="M39.23,19c-10.58,0-17.68,6.16-17.68,18.11v8.52A8,8,0,0,1,25,44.81a7.89,7.89,0,0,1,3.46.8V37.07c0-7.75,4.28-11.73,10.8-11.73S50,29.32,50,37.07V55.69h6.89V37.07C56.91,25.05,49.81,19,39.23,19Z"/><path d="M60.66,37.8c0-10.87,8-18.84,19.27-18.84s19.13,8,19.13,18.84v2.53H67.9c1,6.38,5.8,9.93,12,9.93,4.64,0,7.9-1.45,10-4.56h7.6c-2.75,6.66-9.27,10.94-17.6,10.94C68.63,56.64,60.66,48.67,60.66,37.8Zm31.15-3.62c-1.38-5.73-6.08-8.84-11.88-8.84S69.5,28.53,68.12,34.18Z"/><path d="M102.74,37.8c0-10.86,8-18.83,19.27-18.83s19.27,8,19.27,18.83-8,18.84-19.27,18.84S102.74,48.67,102.74,37.8Zm31.59,0c0-7.24-4.93-12.46-12.32-12.46S109.7,30.56,109.7,37.8,114.62,50.26,122,50.26,134.33,45.05,134.33,37.8Z"/><path d="M180.64,62.82h.8c4.42,0,6.08-2,6.08-7V20.16h6.89v35.2c0,8.84-3.48,13.4-12.32,13.4h-1.45Z"/><path d="M177.2,59.14h-6.89V50.65H152.86A8.64,8.64,0,0,1,145,46.2a7.72,7.72,0,0,1,.94-8.16L161.6,17.49a8.65,8.65,0,0,1,15.6,5.13V44.54h5.17v6.11H177.2ZM151.67,41.8a1.76,1.76,0,0,0-.32,1,1.72,1.72,0,0,0,1.73,1.73h17.23V22.45a1.7,1.7,0,0,0-1.19-1.68,2.36,2.36,0,0,0-.63-.09,1.63,1.63,0,0,0-1.36.73L151.67,41.8Z"/><path d="M191,5.53a5.9,5.9,0,1,0,5.89,5.9A5.9,5.9,0,0,0,191,5.53Z" fill="#018bff"/><path d="M24.7,47a5.84,5.84,0,0,0-3.54,1.2l-6.48-4.43a6,6,0,0,0,.22-1.59A5.89,5.89,0,1,0,9,48a5.81,5.81,0,0,0,3.54-1.2L19,51.26a5.89,5.89,0,0,0,0,3.19l-6.48,4.43A5.81,5.81,0,0,0,9,57.68a5.9,5.9,0,1,0,5.89,5.89A6,6,0,0,0,14.68,62l6.48-4.43a5.84,5.84,0,0,0,3.54,1.2A5.9,5.9,0,0,0,24.7,47Z" fill="#018bff"/></svg> | 
        <svg height="60" width="120" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"><path d="M32.377 26.446h-12.52v3.715h8.88c-.44 5.2-4.773 7.432-8.865 7.432a9.76 9.76 0 0 1-9.802-9.891c0-5.624 4.354-9.954 9.814-9.954 4.212 0 6.694 2.685 6.694 2.685l2.6-2.694s-3.34-3.717-9.43-3.717c-7.755 0-13.754 6.545-13.754 13.614 0 6.927 5.643 13.682 13.95 13.682 7.307 0 12.656-5.006 12.656-12.408 0-1.562-.227-2.464-.227-2.464z" fill="#4885ed"/><use xlink:href="#A" fill="#db3236"/><use xlink:href="#A" x="19.181" fill="#f4c20d"/><path d="M80.628 23.765c-4.716 0-8.422 4.13-8.422 8.766 0 5.28 4.297 8.782 8.34 8.782 2.5 0 3.83-.993 4.8-2.132v1.73c0 3.027-1.838 4.84-4.612 4.84-2.68 0-4.024-1.993-4.5-3.123l-3.372 1.4c1.196 2.53 3.604 5.167 7.9 5.167 4.7 0 8.262-2.953 8.262-9.147V24.292H85.36v1.486c-1.13-1.22-2.678-2.013-4.73-2.013zm.34 3.44c2.312 0 4.686 1.974 4.686 5.345 0 3.427-2.37 5.315-4.737 5.315-2.514 0-4.853-2.04-4.853-5.283 0-3.368 2.43-5.378 4.904-5.378z" fill="#4885ed"/><path d="M105.4 23.744c-4.448 0-8.183 3.54-8.183 8.76 0 5.526 4.163 8.803 8.6 8.803 3.712 0 6-2.03 7.35-3.85l-3.033-2.018c-.787 1.22-2.103 2.415-4.298 2.415-2.466 0-3.6-1.35-4.303-2.66l11.763-4.88-.6-1.43c-1.136-2.8-3.787-5.14-7.295-5.14zm.153 3.374c1.603 0 2.756.852 3.246 1.874l-7.856 3.283c-.34-2.542 2.07-5.157 4.6-5.157z" fill="#db3236"/><path d="M91.6 40.787h3.864V14.93H91.6z" fill="#3cba54"/><defs><path id="A" d="M42.634 23.755c-5.138 0-8.82 4.017-8.82 8.7 0 4.754 3.57 8.845 8.88 8.845 4.806 0 8.743-3.673 8.743-8.743 0-5.8-4.58-8.803-8.803-8.803zm.05 3.446c2.526 0 4.92 2.043 4.92 5.334 0 3.22-2.384 5.322-4.932 5.322-2.8 0-5-2.242-5-5.348 0-3.04 2.18-5.308 5.02-5.308z"/></defs></svg> GenAI
    </div>
""", unsafe_allow_html=True)


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
    results = get_results(generate_context(user_input, 'database_results'))
    try:
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
