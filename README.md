# Intelligent App with Google Generative AI and Neo4j
This is a sample application which shows how Google Vertex AI Generative AI can be used with Neo4j.  To get started, you will need to run the notebook [ingestion/ingestion.ipynb](notebook/notebook.ipynb).

With that complete, you can run the web app in [ui](ui).

## About
We will explore how to leverage Google VertexAI LLMs to build and consume a knowledge graph in Neo4j.

This notebook parses data from a public corpus of Resumes / Curriculum Vitae using Google Vertex AI Generative AI's `text-bison` model. The model is prompted to recognise and extract entities and relationships. Also, we use the `text-bison` model and prompt it to convert questions in english to Cypher - Neo4j's query language for data retrieval.

### Sample questions:
1. How many experts do we have on MS Word?
2. What skills does p1685120816675380030 have?
3. What skills do p1685157378573414524 and p1685153569085002139 have in common?
4. which are all the companies did p1685120816675380030 work?
5. Who went to most number of universities and how many did they go?
6. where do most candidates get educated?
7. How many knows Delphi?