import streamlit as st
import ingestion.pipeline as ingestion
from io import StringIO
from pathlib import Path
from PIL import Image

st.set_page_config(
    page_title="SEC - Form 13 Data Ingestion",
    page_icon="🧠",
    layout="wide",
)

st.title("SEC - Form 13 Data Ingestion")

with st.form("ingestion_form"):
   with st.expander("Uploaded file will be extracted as:"):
      schema = Image.open('./images/form13-schema.png')
      st.image(schema)
   uploaded_file = st.file_uploader('Upload SEC Form 13 Filing', type=['txt'])
   # Every form must have a submit button.
   submitted = st.form_submit_button("Submit")
   if submitted:
       with st.spinner('Processing the Transcript...'):
         if uploaded_file is not None:
            stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))
            string_data = stringio.read()
            res = ingestion.run_pipeline(Path(uploaded_file.name).stem, string_data)
            if res is not None:
               st.success('Done!')
               with st.expander("See Generated Cypher"):
                  st.markdown(f"""
                              ```
                              {res}
                              ```
                  """)
            else:
               st.error("The Filing could not be ingested now. Try again later.")
         else:
            st.error("Please upload an SEC Form 13 File")