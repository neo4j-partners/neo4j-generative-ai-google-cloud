import vertexai
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
import streamlit as st

import traceback

project_id = st.secrets["GCP_PROJECT"]
location = st.secrets["GCP_LOCATION"]

def init():
    vertexai.init(project=project_id, location=location)

init()

text_model_name = st.secrets["SUMMARY_MODEL"]
code_model_name = st.secrets["CYPHER_MODEL"]

def run_text_model(
    model_name: str,
    temperature: float,
    max_decode_steps: int,
    top_p: float,
    top_k: int,
    prompt: str,
    ) :
    gen_model = GenerativeModel(model_name=model_name, 
                                generation_config=GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                candidate_count=1,
                max_output_tokens=max_decode_steps
            ))
    return gen_model.generate_content(prompt).text

def call_text_model(prompt, system_prompt=None):
    try:
        if system_prompt != None:
            prompt = f"""< Objective and persona >
            {system_prompt}

            < Instructions >
            {prompt}
            """
        res = run_text_model(text_model_name, 
                             0, 4096, 0.1, 1, prompt)
        return res
    except Exception as e:
        traceback.print_exc()
        print(e)

