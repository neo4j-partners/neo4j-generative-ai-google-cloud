# neo4j-generative-ai-google-cloud
This is a sample notebook and web application which shows how Google Cloud Vertex AI can be used with Neo4j. We will explore how to leverage generative AI to build and consume a knowledge graph in Neo4j.

The dataset we're using is from the SEC's EDGAR system.  It was downloaded using [these scripts](https://github.com/neo4j-partners/neo4j-sec-edgar-form13).

The dataflow in this demo consists of two parts:
1. Ingestion - we read the EDGAR files with VertexAI, extracting entities and relationships from them which is then ingested into a Neo4j database deployed from [GCP Marketplace](https://console.cloud.google.com/marketplace/browse?filter=partner:Neo4j)
2. Consumption - A user inputs natural language into a chat UI.  Vertex AI GenAI converts that to Neo4j Cypher which is run against the database.  This flow allows non technical users to query the database.

## Setup VertexAI Workbench
To get started setting up the demo, clone this repo into a VertexAI Workbench environment and then run through the notebooks numbered 1 and 2.
Create a [managed notebook](https://console.cloud.google.com/vertex-ai/workbench/managed) in Google Cloud Vertex AI.  Be sure to select "single user" when starting a managed notebook to run this, otherwise the auth won't allow access to the preview.

Once that has started, open the notebook and a terminal window within that.  Clone this repo with the command:

    git clone https://github.com/neo4j-partners/neo4j-generative-ai-google-cloud.git

## Deploy Neo4j AuraDS Professional
This demo requires a Neo4j instance.  You can deploy that using the GCP Marketplace listing [here](https://console.cloud.google.com/marketplace/browse?filter=partner:Neo4j)

## Enable VertexAI API and GenAI Models
This demo uses multiple GenAI Models inside the Vertex GenAI Model Garden. Please ensure that you have access to these Models:
- Text Embedding Gecko
- Gemini Pro 1.0 Vision
- Code-bison 
- Anthropic Claude V3

## UI
The UI application is based on Streamlit. In this example we're going to show how to run it on a [Google Compute Engine (GCE)](https://console.cloud.google.com/compute/instances) VM.  First, deploy a VM. You need to replace your environment specific values in the command below:

    export VM_INSTANCE_NAME='neo4j-generative-ai-google-cloud'
    export GCP_PROJECT_NAME=$(gcloud config get-value project)
    gcloud compute instances create $VM_INSTANCE_NAME \
        --project=$GCP_PROJECT_NAME \
        --zone=us-central1-c \
        --machine-type=e2-medium \
        --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
        --maintenance-policy=MIGRATE --provisioning-model=STANDARD \
        --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/trace.append \
        --tags=allow-http,http-server \
        --create-disk=auto-delete=yes,boot=yes,device-name=$VM_INSTANCE_NAME,image=projects/debian-cloud/global/images/debian-11-bullseye-v20230509,mode=rw,size=10,type=projects/$GCP_PROJECT_NAME/zones/us-central1-c/diskTypes/pd-balanced \
        --no-shielded-secure-boot \
        --shielded-vtpm --shielded-integrity-monitoring \
        --labels=goog-ec-src=vm_add-gcloud --reservation-affinity=any
        

Next, login to the new VM instance:

    gcloud compute ssh --zone "us-central1-c" $VM_INSTANCE_NAME --project $GCP_PROJECT_NAME

We're going to be running the application on port 80.  That requires root access, so first:

    sudo su

Then you'll need to install git and clone this repo:

    apt install -y git
    mkdir -p /app
    cd /app
    git clone https://github.com/neo4j-partners/neo4j-generative-ai-google-cloud.git
    cd neo4j-generative-ai-google-cloud

Login using GCP credentials via the `gcloud` cli.

    gcloud auth application-default login

Let's install python & pip first:

    apt install -y python
    apt install -y pip

Now, let's create a Virtual Environment to isolate our Python environment and activate it

    apt-get install -y python3-venv
    python3 -m venv /app/venv/genai
    source /app/venv/genai/bin/activate

To install Streamlit and other dependencies:

    cd ui
    pip install -r requirements.txt

Check if `streamlit` command is accessible from PATH by running this command:

    streamlit --version

If not, you need to add the `streamlit` binary to PATH variable like below:

    export PATH="/app/venv/genai/bin:$PATH"

Next up you'll need to create a secrets file for the app to use.  Open the file and edit it:

    cd streamlit
    cd .streamlit
    cp secrets.toml.example secrets.toml
    vi secrets.toml

You will now need to edit that file to reflect your credentials. The file has the following variables:

    # GCP
    GCP_PROJECT = "myprojectname" #e.g. neo4jbd
    GCP_LOCATION = "us-central1" #e.g. us-central1
    SUMMARY_MODEL = "" #e.g. gemini-1.5-pro-preview-0409
    CYPHER_MODEL = "" #e.g. gemini-1.5-pro-preview-0409
    EMBEDDING_MODEL  = "" #e.g. textembedding-gecko@003. Ensure that the same model is provided during the ingestion phases in the `2-text-embedding.ipynb` notebook
    MULTIMODAL_MODEL = "" #e.g. claude-3-sonnet@20240229
    # NEO4J
    NEO4J_HOST = "neo4j+s://URL"
    NEO4J_PORT = "7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "Foo12345678"
    NEO4J_DB = "neo4j"

Now we can run the app with the commands:

    cd ..
    streamlit run Home.py --server.port=80

On a GCP VM to run on port 80:
- Ensure you are a root or has access to run on port 80
- If you are running `sudo`, you also need to run the `gcloud auth` command above as a sudoer. And ensure that `streamlit` is accessible from the PATH.
- Ensure that the VM has port 80 open for HTTP access. You might need to open that port or any other via firewall-rules. You can use the [following gcloud command](https://cloud.google.com/sdk/gcloud/reference/compute/firewall-rules/create) to open the port. Make sure you replace with relevant values. You also need to add network tags to your VM before executing this command:

    ```bash
    gcloud compute firewall-rules create <rule-name> --allow tcp:80 --source-tags=<list-of-your-instances-name-tags> --source-ranges=0.0.0.0/0 --description="<your-description-here>"
    ```
