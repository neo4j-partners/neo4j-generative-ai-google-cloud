import streamlit as st
import ingestion.process_flow as ingestion
from PIL import Image
from io import BytesIO
import base64
from langchain.globals import set_llm_cache
from langchain.cache import InMemoryCache
import rag_over_media
import streamlit as st

set_llm_cache(InMemoryCache())

st.set_page_config(
    page_title="RAG over Media",
    page_icon="images/logo-mark-fullcolor-RGB-transBG.svg",
    layout="wide",
)

st.title("RAG over Media")

with st.expander("Process Ingestion:"):
   with st.form("ingestion_form"):
      uploaded_file = st.file_uploader('Upload a Process Flow Image', type=['jpg', 'jpeg', 'png'])
      # Every form must have a submit button.
      submitted = st.form_submit_button("Submit")
      if submitted:
         with st.spinner('Processing the Transcript...'):
            if uploaded_file is not None:
               img_bytes = uploaded_file.read()
               img_data = base64.b64encode(img_bytes).decode('utf-8')
               res = ingestion.run_pipeline(img_data, uploaded_file.name, uploaded_file.type)
               if res is not None:
                  st.success('Done!')
                  img = Image.open(BytesIO(img_bytes))
                  st.markdown("### Uploaded Image")
                  st.image(img)
                  st.markdown(f"""
                              ```
                              {res}
                              ```
                  """)
               else:
                  st.error("The Flow could not be ingested now. Try again later.")
            else:
               st.error("Please upload a Process Flow Image of type - jpg, jpeg or png")

with st.expander("Chat"):
   def rag(question):
      res = rag_over_media.get_results(question)
      st.markdown(res['result'].content)

   question = st.text_input("Ask a question on the Uploaded Process Flow", value="")
   if question:
      with st.spinner('Running RAG using Neo4j Vector + Graph ...'):
            rag(question)
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
      <td>What should I do if my flight landed and have no connecting flight?</td>
      <td>My travel date is Aug 3, 2020. Will I get a refund if my flight was not cancelled by SQ</td>
      <td></td>
   </tr>
   <tr>
      <td></td>
      <td></td>
      <td></td>
   </tr>
   <tr>
      <td></td>
      <td></td>
   </tr>
   </table>
   """, unsafe_allow_html=True)


with st.expander("Reset DB"):
   if st.button('Reset', type="primary"):
      with st.spinner('Clearing Neo4j DB ...'):
         rag_over_media.reset_db()
         st.success('DB Cleared!')