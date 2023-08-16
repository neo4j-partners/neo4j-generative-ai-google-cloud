# assetmanager
This is a sample notebook and web application which shows how Google Vertex AI Generative AI can be used with Neo4j.  We will explore how to leverage Google VertexAI LLMs to build and consume a knowledge graph in Neo4j.

This notebook parses Form-13 data From SEC EDGAR. The Form 13 files are semi structured data that are pretty nasty to parse  We'll use generative AI to do it for us.  We will then also use the LLM to generate Cypher statments to load the extracted data into a Neo4j graph.  Then, we'll use a chatbot to query the knowledge graph we've created.

## Setup
To get started, create a [managed notebook](https://console.cloud.google.com/vertex-ai/workbench/managed) in Google Cloud Vertex AI.

Once that has started, open the notebook and a terminal window within that.  Clone this repo with the command:

    git clone https://github.com/neo4j-partners/neo4j-generative-ai-google-cloud.git

The notebook uses Python 3.8 for LangChain.  However the managed notebooks are currently on 3.7.  So, we'll need to install a newer version of Python.  You can do that by running these commands in the terminal.

    VENV=py38
    conda create -y -q -p $HOME/conda_env/$VENV python=3.8 ipykernel
    source /opt/conda/bin/activate ~/conda_env/$VENV
    python -m ipykernel install --user --name $VENV
    conda install -y -c conda-forge ipywidgets

## Notebook
Now you're ready to run the [notebook](notebook.ipynb)!