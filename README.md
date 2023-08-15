# neo4j-generative-ai-google-cloud

This repo contains sample applications that show how to use Neo4j with the generative AI capabilities in Google Cloud Vertex AI.  We explore how to leverage Google generative AI to build and consume a knowledge graph in Neo4j.

* [assetmanager](assetmanager) - Parses data from the SEC containing quarterly filings of asset managers.  We build a graph containing assets managers and the securities they hold.  A chatbot that queries the knowledge graph is included as well.
* [resume](resume) - Extracts entities like jobs and skills from a collection of resumes, then builds a graphs showing what talents individuals share.  A chatbot that queries the knowledge graph is included as well.
