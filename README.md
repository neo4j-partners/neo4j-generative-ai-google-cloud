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
The notebook has an embeeded Gradio widget that can be run for quick testing.

## UI
The UI application is based on Streamlit. In this example we're going to show how to run it on a [Google Compute Engine (GCE)](https://console.cloud.google.com/compute/instances) VM.  First, deploy a VM.  Then you'll need to install git and clone this repo:

    sudo apt install git -y
    git clone https://github.com/neo4j-partners/intelligent-app-google-generativeai-neo4j.git
    cd intelligent-app-google-generativeai-neo4j

Before running it you have to login using GCP credentials via the `gcloud` cli.

    gcloud auth application-default login

To install Streamlit and other dependencies:

    cd ui
    sudo apt install python -y
    sudo apt install pip -y
    pip install -r requirements.txt

You might need to ensure streamlit command is in the PATH. To do that (replace `MY_USER_NAME` in the command below):

    export PATH="/home/MY_USER_NAME/.local/bin/streamlit:$PATH"


Next up you'll need to create a secrets file for the app to use.  Edit the following command to generate that:

    cd streamlit
    cd .streamlit
    cp secrets.toml.example secrets.toml
    cd ..

You will now need to edit that file to reflect your credentials.

To run the app at a port number, say 80:

    streamlit run main.py --server.port=80

On a GCP VM to run on port 80:
- Ensure you are a root or has access to run on port 80
- If you are running `sudo`, you also need to run the `gcloud auth` command above as a sudoer. And ensure that `streamlit` is accessible from the PATH.
- Ensure that the VM has port 80 open for HTTP access. You might need to open that port or any other via firewall-rules. You can use the [following gcloud command](https://cloud.google.com/sdk/gcloud/reference/compute/firewall-rules/create) to open the port. Make sure you replace with relevant values. You also need to add network tags to your VM before executing this command:

    gcloud compute firewall-rules create <rule-name> --allow tcp:80 --source-tags=<list-of-your-instances-name-tags> --source-ranges=0.0.0.0/0 --description="<your-description-here>"


From the UI, you can ask questions like:
1. How many experts do we have on MS Word?
2. What skills does p1685120816675380030 have?
3. What skills do p1685157378573414524 and p1685153569085002139 have in common?
4. which are all the companies did p1685120816675380030 work?
5. Who went to most number of universities and how many did they go?
