from timeit import default_timer as timer

from vertex_chat import VertexLLM
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

sys_tpl = f"""
You are an assistant that helps to generate text to form nice and human understandable answers based.
The latest prompt contains the information, and you need to generate a human readable response based on the given information.
Make it sound like the information are coming from an AI assistant, but don't add any information.
Do not add any additional information that is not explicitly provided in the latest prompt.
I repeat, do not add any information that is not explicitly given.
IMPORTANT: 
1. If you cannot find any information in the text, Summarise the JSON text in english.
E.g: if the provided information only has IDs, just say Here are the IDs and provide them.
2. NEVER ever apologise in the response.
3. When you dont totally understand, just return the output as-is
"""

def createPrompt(messages):
    system_message_prompt = SystemMessage(content=sys_tpl)
    prompt = [system_message_prompt]
    if messages:
        question = messages.pop()
        human_message_prompt = HumanMessage(content=question)
    tmp = []
    for _ in range(3):
        if(len(messages) > 0):
            msg = messages.pop()
            tmp.append(HumanMessage(content=msg))
    if len(tmp) > 0:
        tmp.reverse()
        prompt = prompt + tmp
    if question:
        prompt.append(human_message_prompt)
    return ChatPromptTemplate.from_messages(prompt)

def generate_response(messages):
    start = timer()
    try:
        chat = VertexLLM(model_name='text-bison@001',
                            max_output_tokens=1024,
                            temperature=0,
                            top_p=0.8,
                            top_k=40,
                            # allow_reuse=True,
                            verbose=True)
        chat_prompt = createPrompt(messages)
        chain = LLMChain(llm=chat, prompt=chat_prompt)
        response = chain.run({})
        # If the model apologized, remove the first line or sentence
        if "apologi" in response:
            if "\n" in response:
                response = " ".join(response.split("\n")[1:])
            else:
                response = " ".join(response.split(".")[1:])
        return response
    except:
        return "Something wrong with the Cypher or LLM token limit exceeded. Please ask again"
    finally:
        print('Response Generation Time : {}'.format(timer() - start))

