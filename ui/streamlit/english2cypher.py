import os
from retry import retry
from timeit import default_timer as timer
import streamlit as st

from langchain.llms import VertexAI
from langchain import LLMChain
from langchain.prompts.prompt import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from train_cypher import template, schema, instr_template, examples
cypher_prefix = ["ALTER","CALL","CREATE","DEALLOCATE","DELETE","DENY","DETACH","DROP","DRYRUN","ENABLE","FOREACH","GRANT","LOAD","MATCH","MERGE","OPTIONAL","REALLOCATE","REMOVE","RENAME","RETURN","REVOKE","SET","SHOW","START","STOP","TERMINATE","UNWIND","USE","USING","WITH"]


def extract_cypher(s):
    if s.startswith(tuple(cypher_prefix)):
        return s
    else:
        arr = s.split('\n', 1)
        if len(arr) == 1:
            return 'MATCH (e:Nothing) return e.name'
        return extract_cypher(arr[1])
    

def createPrompt(messages):
    sys_tpl="You are an assistant that translates english to Neo4j cypher"
    system_message_prompt = SystemMessage(content=sys_tpl)
    instr_human = HumanMessagePromptTemplate(
        prompt=PromptTemplate(
            template=instr_template,
            input_variables=[]   
        )
    )
    instr_ai = AIMessage(content='Roger that')
    prompt = [system_message_prompt, instr_human, instr_ai]
    prompt = prompt + getExamplePrompts()
    tmp = []
    for _ in range(6):
        if(len(messages) > 0):
            aiMsg = messages.pop()
            tmp.append(AIMessage(
                content=aiMsg))
            huMsg = messages.pop()
            tmp.append(HumanMessage(content=huMsg))
    if len(tmp) > 0:
        tmp.reverse()
        prompt = prompt + tmp
    human_message_prompt = HumanMessagePromptTemplate.from_template(template)
    prompt.append(human_message_prompt)
    return ChatPromptTemplate.from_messages(prompt)

def getExamplePrompts():
    eg_prompt = []
    for eg in examples:
        for k, v in eg.items():
            if k == "q": 
                eg_human = HumanMessagePromptTemplate(
                    prompt=PromptTemplate(
                        template=v,
                        input_variables=[] 
                    )
                )
                eg_prompt.append(eg_human)
            else:
                eg_ai = AIMessage(content=v)
                eg_prompt.append(eg_ai)
    return eg_prompt


@retry(tries=1, delay=5)
def generate_cypher(messages):
    start = timer()
    try:
        chat = VertexAI(model_name='text-bison@001',
                            tuned_model_name=st.secrets["TUNED_CYPHER_MODEL"],
                            max_output_tokens=1024,
                            temperature=0,
                            top_p=0.95,
                            top_k=0.40,
                            # allow_reuse=True,
                            verbose=True)
        if messages:
            question = messages.pop()
        else: 
            question = 'How many cases are there?'
        chat_prompt = createPrompt(messages)
        chain = LLMChain(llm=chat, prompt=chat_prompt)
        response = chain.run(schema + "\nQuestion: "+ question + "\nAnswer:\n")
        # Sometime the models bypasses system prompt and returns
        # data based on previous dialogue history
        if not "MATCH" in response and "{" in response:
            raise Exception(
                "Model bypassed system message and is returning response based on previous conversation history" + response)
        # If the model apologized, remove the first line
        elif "apologi" in response:
            response = " ".join(response.split("\n")[1:])
        if "Answer:" in response:
            response = response.split("Answer:\n")[1].strip()
        if "answer:" in response:
            response = response.split("answer:")[1].strip()
        if "A: " in response:
            response = response.split("A: ")[1].strip()
        if "AI: " in response:
            response = response.split("AI: ")[1].strip()
        if "Reason:" in response:
            response = response.split("Reason:\n")[0].strip()
        # Sometime the model adds quotes around Cypher when it wants to explain stuff
        if "`" in response:
            response = response.split("```")[1].strip("`")
        # print(response)
        return response
    except:
        return "LLM Quota Exceeded. Please try again"
    finally:
        print('Cypher Generation Time : {}'.format(timer() - start))


