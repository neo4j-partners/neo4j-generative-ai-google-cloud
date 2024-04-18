from vertexai.generative_models import (
    GenerationConfig,
    GenerativeModel
)
import json
import pandas as pd
from langchain.prompts.prompt import PromptTemplate
from retry import retry
from timeit import default_timer as timer
import streamlit as st
import ingestion.llm_util as llm_util
from vertexai.language_models import TextEmbeddingModel
from json import loads
from semantic_layer.semantic_fn import sec_tool, tpl_fn

llm_util.init()

emb_model_name = st.secrets["EMBEDDING_MODEL"]

SYSTEM_PROMPT = """You are a Financial expert with SEC filings who can answer questions by summarizing the context below."""
PROMPT_TEMPLATE = """< Instructions >
< Question >
{input}

< Constraints >
1. Answer the question based on the context provided in JSON below.
2. Do not assume or retrieve any information outside of the context 
3. List the results in rich text format if there are more than one results
4. If the context is empty, just respond None
5. Stay faithful to the context and please do not waver.

Here is the context in JSON format. Context might contain Annual report chunk for the company involved.
In that case, note that company's are not considered asset managers in this dataset, 
and form10ks don't include asset manager information. Where asset manager info is made explicitly available, 
you can assume the mentioned asset managers are impacted by the same things as the companies. 

< Context >
{context} 
"""

PROMPT = PromptTemplate(
    input_variables=["input", "context"], template=PROMPT_TEMPLATE
)

EMBEDDING_MODEL = TextEmbeddingModel.from_pretrained(emb_model_name)
model_name = st.secrets["SUMMARY_MODEL"]

def semantic_layer_qa(query): 
    model = GenerativeModel(
        model_name,
        generation_config=GenerationConfig(temperature=0),
        tools=[sec_tool],
    )
    chat = model.start_chat()
    response = chat.send_message(query)
    parts = response.candidates[0].content.parts[0]
    if 'name' in parts.function_call:
        return tpl_fn[parts.function_call.name](query, parts.function_call.args)
    else:
        return parts.text


def df_to_context(df):
    result = df.to_json(orient="records")
    parsed = loads(result)
    text = json.dumps(parsed, indent=1)
    return text


@retry(tries=1)
def get_results(question):
    start = timer()
    try:
        df = semantic_layer_qa(question)
        if isinstance(df, pd.DataFrame):
            ctx = df_to_context(df)
            ans = PROMPT.format(input=question, context=ctx)
            result = llm_util.call_text_model(ans, SYSTEM_PROMPT)
            r = {'context': ctx, 'result': result}
            return r
        elif df is None:
            ans = PROMPT.format(input=question, 
                    context='No related information in the DB')
            result = llm_util.call_text_model(ans, SYSTEM_PROMPT)
            return {'context': {}, 'result': result}
        else:
            return {'context': {}, 'result': df}
    finally:
        print('Generation Time : {}'.format(timer() - start))

