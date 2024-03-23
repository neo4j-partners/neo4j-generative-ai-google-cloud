import vertexai
from anthropic import AnthropicVertex
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
    project_id: str,
    model_name: str,
    temperature: float,
    max_decode_steps: int,
    top_p: float,
    top_k: int,
    system_prompt: str,
    prompt: str,
    location: str = "us-central1",
    ) :
    """Text Completion Use a Large Language Model."""
    client = AnthropicVertex(region=location, project_id=project_id)
    message = client.messages.create(
        system=system_prompt,
        max_tokens=max_decode_steps,
        temperature=temperature,
        top_k=top_k, top_p=top_p,
        messages=[
            {
            "role": "user",
            "content": prompt,
            }
        ],
        model=model_name,
    )
    return message.content[0].text

def call_text_model(prompt, system_prompt='You are an assistant who understands natural language and provide the required response'):
    try:
        res = run_text_model(project_id, text_model_name, 
                             0, 4096, 0.1, 1, system_prompt, prompt, location)
        return res
    except Exception as e:
        traceback.print_exc()
        print(e)

