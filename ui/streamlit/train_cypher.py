examples = [{
    "question": "Where are most pythonistas located?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) MATCH (p)-[:HAS_POSITION]->(pos:Position) WHERE toLower(s.name) CONTAINS 'python' WITH pos.location AS location, COUNT(p) AS num_pythonistas ORDER BY num_pythonistas DESC RETURN location, num_pythonistas LIMIT 1"""
}, {
    "question": "How many Texas-based experts do I have on Java?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) MATCH (p)-[:HAS_POSITION]->(pos:Position) WHERE toLower(s.name) CONTAINS 'java' AND toLower(s.level) CONTAINS 'expert' AND (toLower(pos.location) CONTAINS 'texas' OR toLower(pos.location) CONTAINS 'tx') RETURN COUNT(p)"""
}, {
    "question": "I have to fill 10 Front end roles. Who are all I have based on ideal skillsets for a front end role?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) WHERE (toLower(s.name) CONTAINS 'html' OR toLower(s.name) CONTAINS 'css' OR toLower(s.name) CONTAINS 'javascript' OR toLower(s.name) CONTAINS 'react' OR toLower(s.name) CONTAINS 'angular') RETURN p LIMIT 10"""
}, {
    "question": "What skills do my Strategy Consultants have?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position)-[:AT_COMPANY]->(c:Company), (p)-[:HAS_SKILL]->(s:Skill) WHERE toLower(pos.title) CONTAINS 'strategy consultant' RETURN DISTINCT s.name"""
}, {
    "question": "How many java developers attend more than one universities?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill), (p)-[:HAS_EDUCATION]->(e1:Education), (p)-[:HAS_EDUCATION]->(e2:Education) WHERE toLower(s.name) CONTAINS 'java' AND e1.university <> e2.university RETURN COUNT(DISTINCT p)"""
}, {
    "question": "Who went to most number of universities?",
    "answer": """MATCH (p:Person)-[:HAS_EDUCATION]->(e:Education) WITH p, COUNT(e.university) as num_universities ORDER BY num_universities DESC LIMIT 1 RETURN p, num_universities"""
}, {
    "question": "Do I have any expert on mainframes?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) WHERE toLower(s.name) CONTAINS 'mainframes' AND toLower(s.level) CONTAINS 'expert' RETURN COUNT(p)"""
}, {
    "question": "How many are knowledgable on all of - java, python, javascript, security?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) WHERE (toLower(s.name) CONTAINS 'java' OR toLower(s.name) CONTAINS 'python' OR toLower(s.name) CONTAINS 'javascript' OR toLower(s.name) CONTAINS 'security') WITH p, COUNT(s) AS skill_count WHERE skill_count = 4 RETURN COUNT(p)"""
}, {
    "question": "Where do most of them work at?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position)-[:AT_COMPANY]->(c:Company) RETURN c.name, COUNT(p) AS num_people ORDER BY num_people DESC LIMIT 1"""
}, {
    "question": "Where did most of them study?",
    "answer": """MATCH (p:Person)-[:HAS_EDUCATION]->(e:Education) RETURN e.university, COUNT(p) AS num_people ORDER BY num_people DESC LIMIT 1"""
}, {
    "question": "Where does most marketing managers work?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position)-[:AT_COMPANY]->(c:Company) WHERE toLower(pos.title) CONTAINS 'marketing manager' RETURN c.name, COUNT(p) AS num_people ORDER BY num_people DESC LIMIT 1"""
}, {
    "question": "Do I have anyone with expertise on Java and Cyber security?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s1:Skill), (p)-[:HAS_SKILL]->(s2:Skill) WHERE toLower(s1.name) CONTAINS 'java' AND toLower(s2.name) CONTAINS 'cyber security' RETURN p"""
}, {
    "question": "Which data scientist is based out of Texas?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position) WHERE toLower(pos.title) CONTAINS 'data scientist' AND (toLower(pos.location) CONTAINS 'texas' OR toLower(pos.location) CONTAINS 'tx') RETURN p"""
}, {
    "question": "Which skill is popular among people with bachelor degrees?",
    "answer": """MATCH (p:Person)-[:HAS_EDUCATION]->(e:Education), (p)-[:HAS_SKILL]->(s:Skill) WHERE toLower(e.degree) CONTAINS 'bachelor' WITH s, COUNT(p) AS person_count ORDER BY person_count DESC LIMIT 1 RETURN s.name, person_count"""
}, {
    "question": "How many people have worked as a software engineer at Google?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position)-[:AT_COMPANY]->(c:Company) WHERE toLower(pos.title) CONTAINS 'software engineer' AND toLower(c.name) CONTAINS 'google' RETURN COUNT(p)"""
}, {
    "question": "How many people have a skill level of intermediate in Python?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) WHERE toLower(s.name) CONTAINS 'python' AND toLower(s.level) CONTAINS 'intermediate' RETURN COUNT(p)"""
}, {
    "question": "How many people have held a position in New York City?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position) WHERE toLower(pos.location) CONTAINS 'new york city' RETURN COUNT(p)"""
}, {
    "question": "How many people have a master's degree in data science?",
    "answer": """MATCH (p:Person)-[:HAS_EDUCATION]->(e:Education) WHERE toLower(e.degree) CONTAINS 'master' AND toLower(e.degree) CONTAINS 'data science' RETURN COUNT(p)"""
}, {
    "question": "How many people have worked as a data analyst at Facebook?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position)-[:AT_COMPANY]->(c:Company) WHERE toLower(pos.title) CONTAINS 'data analyst' AND toLower(c.name) CONTAINS 'facebook' RETURN COUNT(p)"""
}, {
    "question": "How many people have a skill level of beginner in JavaScript?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) WHERE toLower(s.name) CONTAINS 'javascript' AND toLower(s.level) CONTAINS 'beginner' RETURN COUNT(p)"""
}, {
    "question": "How many people have a bachelor's degree in electrical engineering?",
    "answer": """MATCH (p:Person)-[:HAS_EDUCATION]->(e:Education) WHERE toLower(e.degree) CONTAINS 'bachelor' AND toLower(e.degree) CONTAINS 'electrical engineering' RETURN COUNT(p)"""
}, {
    "question": "How many people have worked as a project manager in London?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position) WHERE toLower(pos.title) CONTAINS 'project manager' AND toLower(pos.location) CONTAINS 'london' RETURN COUNT(p)"""
}, {
    "question": "How many people have a PhD in physics from MIT?",
    "answer": """MATCH (p:Person)-[:HAS_EDUCATION]->(e:Education) WHERE toLower(e.degree) CONTAINS 'phd' AND toLower(e.degree) CONTAINS 'physics' AND toLower(e.university) CONTAINS 'mit' RETURN COUNT(p)"""
}, {
    "question": "How many people have a degree in Computer Science from Stanford University?",
    "answer": """MATCH (p:Person)-[:HAS_EDUCATION]->(e:Education) WHERE toLower(e.degree) CONTAINS 'computer science' AND toLower(e.university) CONTAINS 'stanford university' RETURN COUNT(p)"""
}, {
    "question": "How many people have worked as a Software Engineer at Google?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position)-[:AT_COMPANY]->(c:Company) WHERE toLower(pos.title) CONTAINS 'software engineer' AND toLower(c.name) CONTAINS 'google' RETURN COUNT(p)"""
}, {
    "question": "How many people have a skill level of 'intermediate' in Python?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) WHERE toLower(s.name) CONTAINS 'python' AND toLower(s.level) CONTAINS 'intermediate' RETURN COUNT(p)"""
}, {
    "question": "How many people have a Master's degree in Data Science?",
    "answer": """MATCH (p:Person)-[:HAS_EDUCATION]->(e:Education) WHERE toLower(e.degree) CONTAINS 'master' AND toLower(e.degree) CONTAINS 'data science' RETURN COUNT(p)"""
}, {
    "question": "How many people have worked as a Data Analyst in New York?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position) WHERE toLower(pos.title) CONTAINS 'data analyst' AND toLower(pos.location) CONTAINS 'new york' RETURN COUNT(p)"""
}, {
    "question": "How many people have a PhD in Physics from MIT?",
    "answer": """MATCH (p:Person)-[:HAS_EDUCATION]->(e:Education) WHERE toLower(e.degree) CONTAINS 'phd' AND toLower(e.degree) CONTAINS 'physics' AND toLower(e.university) CONTAINS 'mit' RETURN COUNT(p)"""
}, {
    "question": "How many people have worked as a Product Manager at Amazon?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position)-[:AT_COMPANY]->(c:Company) WHERE toLower(pos.title) CONTAINS 'product manager' AND toLower(c.name) CONTAINS 'amazon' RETURN COUNT(p)"""
}, {
    "question": "How many people have a skill level of 'beginner' in JavaScript?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) WHERE toLower(s.name) CONTAINS 'javascript' AND toLower(s.level) CONTAINS 'beginner' RETURN COUNT(p)"""
}, {
    "question": "How many people have a Bachelor's degree in Mathematics?",
    "answer": """MATCH (p:Person)-[:HAS_EDUCATION]->(e:Education) WHERE toLower(e.degree) CONTAINS 'bachelor' AND toLower(e.degree) CONTAINS 'mathematics' RETURN COUNT(p)"""
}, {
    "question": "How many people have worked as a Data Scientist in San Francisco?",
    "answer": """MATCH (p:Person)-[:HAS_POSITION]->(pos:Position) WHERE toLower(pos.title) CONTAINS 'data scientist' AND toLower(pos.location) CONTAINS 'san francisco' RETURN COUNT(p)"""
}, {
    "question": "How many knows Delphi?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) WHERE toLower(s.name) CONTAINS 'delphi' RETURN COUNT(p)"""
}, {
    "question": "How many experts do we have on MS Word?",
    "answer": """MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) WHERE toLower(s.name) CONTAINS 'ms word' AND toLower(s.level) CONTAINS 'expert' RETURN COUNT(p)"""
}, {
    "question": "What skills does p1685120816675380030 have?",
    "answer": """MATCH (p:Person {id: 'p1685120816675380030'})-[:HAS_SKILL]->(s:Skill) RETURN s.name"""
}, {
    "question": "Who went to most number of universities and how many did they go?",
    "answer": """MATCH (p:Person)-[:HAS_EDUCATION]->(e:Education) WITH p, count(e) AS num_educations ORDER BY num_educations DESC LIMIT 1 RETURN p.id, num_educations"""
}, {
    "question": "which are all the companies did p1685120816675380030 work?",
    "answer": "MATCH (p:Person {id: 'p1685120816675380030'})-[:HAS_POSITION]->(pos:Position)-[:AT_COMPANY]->(c:Company) RETURN c.name"
}, {
    "question": "What skills do p1685157378573414524 and p1685153569085002139 have in common?",
    "answer": """MATCH (p1:Person)-[:HAS_SKILL]->(s:Skill)<-[:HAS_SKILL]-(p2:Person) WHERE p1.id = 'p1685157378573414524' AND p2.id = 'p1685153569085002139' RETURN DISTINCT s.name"""
}]

instr_template = """
Here are the instructions to follow:
1. Use the Neo4j schema to generate cypher compatible ONLY for Neo4j Version 5
2. Do not use EXISTS, SIZE keywords in the cypher.
3. Use only Nodes and relationships mentioned in the schema while generating the response
4. Reply ONLY in Cypher
5. Always do a case-insensitive and fuzzy search for any properties related search. Eg: to search for a Company name use `toLower(c.name) contains 'neo4j'`
6. Candidate node is synonymous to Person.
"""


template = """
Using this Neo4j schema and Reply ONLY in Cypher when it makes sense.

Schema: {text}
"""

schema = """
Nodes:
    label:'Person',id:string,role:string,description:string //Person Node
    label:'Position',id:string,title:string,location:string,startDate:string,endDate:string,url:string //Position Node
    label:'Company',id:string,name:string //Company Node
    label:'Skill',id:string,name:string,level:string //Skill Node
    label:'Education',id:string,degree:string,university:string,graduation_date:string,score:string,url:string //Education Node
Relationships:
    (:Person)-[:HAS_POSITION]->(:Position)
    (:Position)-[:AT_COMPANY]->(:Company)
    (:Person)-[:HAS_SKILL]->(:Skill)
    (:Person)-[:HAS_EDUCATION]->(:Education)

Output Format Cypher(Strict): //Only Cypher as output. No other text
MATCH (p:Person)-[:HAS_SKILL]->(s:Skill) WHERE toLower(p.name) CONTAINS 'java' AND toLower(p.level) CONTAINS 'expert' RETURN COUNT(p) 

"""

output_fmt = """
---------------
The output should be in this JSON format:
{
  "cypher": ".."
}"""
