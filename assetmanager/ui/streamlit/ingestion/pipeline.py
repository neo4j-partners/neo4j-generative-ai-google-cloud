from string import Template
import ingestion.llm_util as llm_util
import ingestion.prompts as prompts
import re
import numpy as np
from timeit import default_timer as timer
from graphdatascience import GraphDataScience
import traceback
import json

import streamlit as st

host = st.secrets["NEO4J_HOST"]+":"+st.secrets["NEO4J_PORT"]
user = st.secrets["NEO4J_USER"]
password = st.secrets["NEO4J_PASSWORD"]
db = st.secrets["NEO4J_DB"]

gds = GraphDataScience(
    st.secrets["NEO4J_HOST"],
    auth=(user, password),
    aura_ds=True)

gds.set_database("neo4j")

def run_pipeline(f, edgar_text):
    start = timer()
    try:
        print(f"  {f}: Reading File")
        print(f"    {f}: Extracting Entities & Relationships")
        manager, filings = run_extraction(f, edgar_text)
        st.toast("Extracted Manager & Filing Info ✅")
        print(f"    {f}: Generating Cypher")
        cyphers = generate_cypher(manager, filings)
        st.toast("Generated Cypher ingestion scripts ✅")
        print(f"    {f}: Ingesting Data")
        for e in cyphers:
            gds.run_cypher(e)
        st.toast("Neo4j Data Ingestion DONE ✅")
        print(f"    {f}: Processing DONE")
        return cyphers
    except Exception as e:
        traceback.print_exc()
        return None
    finally:
        end = timer()
        elapsed = (end-start)
        print(f"    {f}: Took {elapsed}secs")

def run_extraction(f, text):
    start = timer()
    
    parts = text.split('</edgarSubmission>') #splits the text into manager details and filing details
    manager_info = parts[0]
    filing_info = parts[1]
    
    prompt = Template(prompts.mgr_info_tpl).substitute(ctext=manager_info)
    manager = json.loads(llm_util.call_text_model(prompt).split('```')[1].strip('json').replace('/n', ' '))
    
    filing_info_chunks = split_filing_info(filing_info)
    filings = []
    for chunk in filing_info_chunks:
        prompt = Template(prompts.filing_info_tpl).substitute(ctext=chunk)
        response = json.loads(llm_util.call_text_model(prompt).split('```')[1].strip('json').replace('/n', ' '))
        filings = filings + response 
    print(f"    {f}: Total Filings: {len(filings)}")
    end = timer()
    elapsed = (end-start)
    print(f"    {f}: Entity Extraction took {elapsed}secs")
    return (manager, filings)

def get_cypher_compliant_var(_id):
    s = re.sub(r'[\W_]', '', _id).lower() #avoid numbers appearing as firstchar; replace spaces
    return s[:20] #restrict variable size

def split_filing_info(s):
    pattern = '(</(\w+:)?infoTable>)'
    splitter = re.findall(pattern, s)[0][0]
    _parts = s.split(splitter)
    if len(_parts) > 15:
        chunks_of_list = np.array_split(_parts, len(_parts)/15) # max 15 filings per part
        chunks_of_str = map(lambda x: splitter.join(x), chunks_of_list)
        return list(chunks_of_str)
    else:
        return [s]

def generate_cypher(manager, filings):
    cyphers = []
    create_manager = f'MERGE (mgr:Manager{{managerName: "{manager["name"]}"}})'
    cyphers.append(create_manager)
    
    addr_id = get_cypher_compliant_var(manager["name"])
    create_address = f'''MERGE (addr:Address{{id: "{addr_id}"}})
    ON CREATE SET addr.street1 = "{manager["street1"]}",
    addr.street2 = "{manager["street2"]}",
    addr.city = "{manager["city"]}",
    addr.stateOrCountry = "{manager["stateOrCountry"]}",
    addr.zipCode = "{manager["zipCode"]}"
    '''
    cyphers.append(create_address)
    
    relate_mgr_addr = f'''MATCH (mgr:Manager{{managerName: "{manager["name"]}"}})
      MATCH (addr:Address{{id: "{addr_id}"}})
      MERGE (mgr)-[:HAS_ADDRESS]->(addr)'''
    cyphers.append(relate_mgr_addr)
    
    for f in filings:
        create_company = f'''MERGE (co:Company{{cusip: "{f['cusip']}"}}) 
        ON CREATE SET co.companyName = "{f["nameOfIssuer"]}"'''
        cyphers.append(create_company)
        
        on_create_set = f"""o.reportCalendarOrQuarter = "{manager['reportCalendarOrQuarter']}",
               o.value = {float(f.get('value', 0))},
               o.shares = {float(f.get('sshPrnamt', 0))},
               o.sshPrnamtType = "{f.get('sshPrnamtType', '')}",
               o.investmentDiscretion = "{f.get('investmentDiscretion', '')}",
               o.votingSole = {int(f.get('votingSole', '0'))},
               o.votingShared = {int(f.get('votingShared', '0'))},
               o.votingNone = {int(f.get('votingNone', '0'))}"""
        on_merge_set = f"""o.value = o.value + {float(f.get('value', 0))},
               o.shares = o.shares + {float(f.get('sshPrnamt', 0))},
               o.votingSole = o.votingSole + {int(f.get('votingSole', '0'))},
               o.votingShared = o.votingShared + {int(f.get('votingShared', '0'))},
               o.votingNone = o.votingNone + {int(f.get('votingNone', '0'))}"""
        relate_mgr_co = f'''MATCH (mgr:Manager{{managerName: "{manager["name"]}"}})
          MATCH (co:Company{{cusip: "{f['cusip']}"}})
          MERGE (mgr)-[o:OWNS]->(co)
          ON CREATE SET {on_create_set}
          ON MATCH SET {on_merge_set}
          '''
        cyphers.append(relate_mgr_co)
        
    return cyphers