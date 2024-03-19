import vertexai
import streamlit as st
from vertexai.preview.generative_models import GenerativeModel

import traceback

project_id = st.secrets["GCP_PROJECT"]
location = st.secrets["GCP_LOCATION"]

def init():
    vertexai.init(project=project_id, location=location)

init()

text_model_name = st.secrets["SUMMARY_MODEL"]
if text_model_name == '':
    text_model_name = 'text-bison@002'

code_model_name = st.secrets["CYPHER_MODEL"]
if code_model_name == '':
    code_model_name = 'code-bison@002'

def run_text_model(
    project_id: str,
    model_name: str,
    temperature: float,
    max_decode_steps: int,
    top_p: float,
    top_k: int,
    prompt: str,
    location: str = "us-central1",
    ) :
    """Text Completion Use a Large Language Model."""
    vertexai.init(project=project_id, location=location)
    model = GenerativeModel(model_name)
    responses = model.generate_content(
        prompt,
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_decode_steps,
            "top_k": top_k,
            "top_p": top_p,
        },
        stream=True)
    res = ''
    for response in responses:
        res = res + response.text
    return res

def call_text_model(prompt):
    try:
        res = run_text_model(project_id, text_model_name, 0, 1024, 0.8, 40, prompt, location)
        return res
    except Exception as e:
        traceback.print_exc()
        print(e)

def call_code_model(prompt):
    try:
        res = run_text_model(project_id, text_model_name, 0, 4000, 0.8, 40, prompt, location)
        return res
    except Exception as e:
        traceback.print_exc()
        print(e)

