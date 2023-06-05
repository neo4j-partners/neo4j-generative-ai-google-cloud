# Intelligent App with Google Generative AI and Neo4j
This is a sample notebook and web application which shows how Google Vertex AI Generative AI can be used with Neo4j.  We will explore how to leverage Google VertexAI LLMs to build and consume a knowledge graph in Neo4j.

This notebook parses data from a public corpus of Resumes / Curriculum Vitae using Google Vertex AI Generative AI's `text-bison` model. The model is prompted to recognise and extract entities and relationships. 

We then use the `text-bison` model and prompt it to convert questions in english to Cypher - Neo4j's query language for data retrieval.

## Setup
To get started, create a [managed notebook](https://console.cloud.google.com/vertex-ai/workbench/managed) in Google Cloud Vertex AI.  Be sure to select "single user" when starting a managed notebook to run this, otherwise the auth won't allow access to the preview.

Once that has started, open the notebook and a terminal window within that.  Clone this repo with the command:

    git clone https://github.com/neo4j-partners/intelligent-app-google-generativeai-neo4j.git

The notebook uses Python 3.8 for LangChain.  However the managed notebooks are currently on 3.7.  So, we'll need to install a newer version of Python.  You can do that by running these commands in the terminal.

    VENV=py38
    conda create -y -q -p $HOME/conda_env/$VENV python=3.8 ipykernel
    source /opt/conda/bin/activate ~/conda_env/$VENV
    python -m ipykernel install --user --name $VENV

## Notebook
The notebook at [notebook/notebook.ipynb](notebook/notebook.ipynb) walks through prompts and tuning a model.  You will need to run that before the UI.

## UI
To run the UI...