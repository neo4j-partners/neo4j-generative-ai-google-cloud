from langchain.schema import HumanMessage
from langchain.schema import SystemMessage
from langchain_google_vertexai import ChatVertexAI
from langchain_core.output_parsers import JsonOutputParser
from vertexai.language_models import TextEmbeddingModel
import re
from string import Template
import json
import time
import streamlit as st
from graphdatascience import GraphDataScience
import traceback
import ingestion.llm_util as llm_util
from timeit import default_timer as timer

host = st.secrets["NEO4J_HOST"]+":"+st.secrets["NEO4J_PORT"]
user = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASSWORD"]
db = st.secrets["NEO4J_DB"]

gds = GraphDataScience(
    st.secrets["NEO4J_HOST"],
    auth=(user, password),
    aura_ds=True)

gds.set_database(db)

llm_util.init()

emb_model_name = st.secrets["EMBEDDING_MODEL"]
EMBEDDING_MODEL = TextEmbeddingModel.from_pretrained(emb_model_name)
model_name = st.secrets["MULTIMODAL_MODEL"]

process_flow_prompt = """From the process image provided, extract the flow as a Graph of nodes and edges in json format. Do not miss any of these information.
* Any text at the start of the image and outside the flow chart box are the title and subtitle. Add them inside the first flow chart box JSON object. 
* Treat each box as separate nodes even if they contain same text inside
* Restrict to the following keys for nodes object:
    - id //lower-case alphanumeric id to refer in the edges object
    - label //any free text inside the box
    - type //If the label is a question, then it's a decision box no matter the shape of the box itself.
    - Create relevant keys (in camelCases. ignore special characters for key names) and values for any text outside the box but refer the process. These texts will be UNCONNECTED boxes closer to the box. Eg. cost for each class of fares. Remember this and do not miss these key info. They are not to be confused with `terms`
    - terms //A box CONNECTED via DOTTED edges to the flow box are considered as terms. So, place those text inside the terms key of the connected flow box. Sometimes a single can be connected to more than one boxes. In that case, include the term to each of the boxes connected. Has to be string not list
* Restrict to the following keys for edges object:
    - label //any free text that refer to the edge arrow
    - from //id of the source node
    - to //id of the target node. This should not be equal to `from` node
* Text inside boxes are not unique. So do not assume if 2 boxes with same text are one and the same. So, you have to create 2 different nodes
* REMEMBER: Create new node object every time even if the text/label inside is same with previous nodes. This is SUPER IMPORTANT.
  Please be careful with this point, as decision steps can be wrongly reused
* Ensure that you extract all the edges. Do not pass empty or invalid node references in the edge object
* Please double-check the DAG you created above and ensure it fits the image input
"""

def run_pipeline(img_data, img_name, img_type):
    start = timer()
    try:
        f = img_name
        print(f"  {f}: Reading Image")
        print(f"    {f}: Extracting Nodes & Edges")
        flow_json = parse(process_flow_prompt, img_data, img_type)
        st.toast("Extracted Process Nodes & Relationships ✅")
        print(f"    {f}: Generating Cypher")
        constraints, ent_cyp, rel_cyp = generate_cypher_with_vector_emb(flow_json)
        st.toast("Generated Cypher ingestion scripts ✅")
        print(f"    {f}: Ingesting Data")
        for e in constraints:
            gds.run_cypher(e)
        for e in ent_cyp:
            gds.run_cypher(e)
        for r in rel_cyp:
            gds.run_cypher(r)
        gds.run_cypher("""CREATE VECTOR INDEX `process-flow-emb` IF NOT EXISTS 
        FOR (s:Step) 
        ON (s.emb) 
        OPTIONS {indexConfig: {
        `vector.dimensions`: 768,
        `vector.similarity_function`: 'cosine'
        }}""")
        st.toast("Neo4j Data Ingestion DONE ✅")
        print(f"    {f}: Processing DONE")
        return constraints + ent_cyp + rel_cyp
    except Exception as e:
        traceback.print_exc()
        return None
    finally:
        end = timer()
        elapsed = (end-start)
        print(f"    {f}: Took {elapsed}secs")

def parse(prompt, encoded_image, file_type):
    try:
        llm = ChatVertexAI(
            model_name=model_name,
            model_kwargs = {
                "temperature":0,
                "top_k":1, "top_p":0.1,
                "max_tokens": 50000
            },
            convert_system_message_to_human = True
        )
        message = HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{file_type};base64,{encoded_image}"
                    }
                },
            ]
        )
        parser = JsonOutputParser()
        chain =  llm | parser
        flow_json = chain.invoke(
            [SystemMessage(content=prompt), message])
        return flow_json
    except Exception as e:
        print(e)
        raise SystemExit(f"Failed to parse. Error: {e}")

def get_prop_str(prop_dict, _id):
    s = []
    for key, val in prop_dict.items():
      if key != 'label' and key != 'id':
         s.append(_id+"."+key+' = "'+str(val).replace('\"', '"').replace('"', '\"')+'"') 
    return ' ON CREATE SET ' + ','.join(s)

def toSnakeCase(string):
    string = re.sub(r'(?<=[a-z])(?<=[0-9])(?=[A-Z])|[^a-zA-Z0-9]', ' ', string).strip().replace(' ', '_')
    return ''.join('_'+string.upper())

def get_cypher_compliant_var(_id):
    return "_"+ re.sub(r'[\W_]', '', _id)

def create_rel_map(in_json):
    rel_map = {}
    for j in in_json['edges']:
          src_id = get_cypher_compliant_var(j['from'])
          text = ''
          if 'label' in j:
            text = j['label']
          if len(text) <= 0:
                continue
          if src_id not in rel_map:
                rel_map[src_id] = text
          else:
            rel_map[src_id] = f'{rel_map[src_id]} (or) {text}'
    return rel_map

def generate_cypher_with_vector_emb(in_json):
    e_map = {}
    e_stmt = []
    r_stmt = []
    e_stmt_tpl = Template("($id:$label{id:'$key'})")
    r_stmt_tpl = Template("""
      MATCH $src
      MATCH $tgt
      MERGE ($src_id)-[r:$rel]->($tgt_id) ON CREATE SET r.label='$text'
    """)
    types = {'Start', 'Process', 'Decision', 'End'}
    constraints = []
    rel_map = create_rel_map(in_json)
    i = 0
    for j in in_json['nodes']:
          process_meta = ''
          text = j['label']
          if 'title' in j: #this is the title metadata object
            subTitle = ''
            if 'subTitle' in j:
                subTitle = j['subTitle']
            meta = {
                'process': text,
                'description': f"{j['title']} \n{subTitle}"
            }
            j = json.dumps(meta)
            process_meta = f'About: {j}'
            continue
          props = ''
          label = j.get('type', 'process').capitalize()
          types.add(label)
          i = i + 1
          id = str(time.time_ns()+i)
          varname = get_cypher_compliant_var(j['id'])
          stmt = e_stmt_tpl.substitute(id=varname, label=label+":Step", key=id)
          e_map[varname] = stmt
          terms = []
          for key, val in j.items():
              if key != 'label' and key != 'id' and key != 'type':
                   terms.append(f'{key}: {val}')
          if varname in rel_map:
            text = f'{text} {rel_map[varname]}'
          if len(terms) > 0:
              terms_str = '\n'.join(terms)
              text = f"{text} \nTerms: \n{terms_str}"
          emb = EMBEDDING_MODEL.get_embeddings([text])[0]
          prop_dict = {
            'text': text + process_meta,
          }
          stmt = f'MERGE {stmt} {get_prop_str(prop_dict, varname)}, {varname}.emb={str(emb.values)}'
          e_stmt.append(stmt)
    for j in in_json['edges']:
          src_id = get_cypher_compliant_var(j['from'])
          if src_id == '_start':
            continue
          text = 'NEXT'
          if 'label' in j:
            text = j['label']
          rel = toSnakeCase(text)
          tgt_id = get_cypher_compliant_var(j['to'])
          if src_id not in e_map or tgt_id not in e_map:
              continue
          stmt = r_stmt_tpl.substitute(
              src_id=src_id, tgt_id=tgt_id, src=e_map[src_id], tgt=e_map[tgt_id], rel=rel, text=text)

          r_stmt.append(stmt)
    
    for typ in types:
        constraints.append(f"CREATE CONSTRAINT unique_{typ.lower()}_id IF NOT EXISTS FOR (n:{typ}) REQUIRE n.id IS UNIQUE")
    return constraints, e_stmt, r_stmt

