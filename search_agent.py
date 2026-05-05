"""
Strands Agent with Bedrock AgentCore Runtime for product search.

This agent uses Amazon Bedrock (Claude) and OpenSearch Service to perform
semantic product search. It can be run locally for testing or deployed
to Bedrock AgentCore Runtime.

Usage:
    Local testing:  Uncomment strands_agent_bedrock() call, comment app.run()
    Deployment:     Comment strands_agent_bedrock() call, uncomment app.run()

Prerequisites:
    - OpenSearch Service domain with product index and deployed embedding model
    - IAM principal has Bedrock model access and OpenSearch permissions
    - agent-permissions role mapped in OpenSearch Dashboards
    - pip install -r requirements.txt
"""

from strands import Agent, tool
from strands_tools import calculator
import argparse
import json
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

app = BedrockAgentCoreApp()


@tool
def search_products(query: str, size: int = 5):
    """Search products in OpenSearch using neural search."""
    try:
        # ============================================================================
        # CONFIGURATION - Change these values for your environment
        # ============================================================================
        host = ''  # CHANGE THIS - OpenSearch domain endpoint (e.g., 'search-mydomain-xxx.us-east-1.es.amazonaws.com')
        region = ''  # CHANGE THIS - AWS region (e.g., us-east-1)
        account_id = ''  # CHANGE THIS - Your AWS account ID (e.g., '123456789012')

        # ============================================================================

        service = 'es'
        credentials = boto3.Session().get_credentials()
        awsauth = AWS4Auth(
            credentials.access_key,
            credentials.secret_key,
            region,
            service,
            session_token=credentials.token
        )

        # Create OpenSearch client
        client = OpenSearch(
            hosts=[{'host': host, 'port': 443}],
            http_auth=awsauth,
            use_ssl=True,
            verify_certs=True,
            connection_class=RequestsHttpConnection
        )

        search_body = {
            "_source": False,
            "fields": ["title", "price", "category", "image"],
            "size": size,
            "query": {
                "neural": {
                    "title_vector": {
                        "query_text": query,
                        "model_id": "",  # CHANGE THIS - Your OpenSearch embedding model ID (from Step 4)
                        "k": 3
                    }
                }
            }
        }

        response = client.search(
            body=search_body,
            index="product"
        )

        products = []
        for hit in response['hits']['hits']:
            fields = hit.get('fields', {})
            product = {
                'title': fields.get('title', [''])[0] if fields.get('title') else '',
                'price': fields.get('price', [''])[0] if fields.get('price') else '',
                'category': fields.get('category', [''])[0] if fields.get('category') else '',
                'image': fields.get('image', [''])[0] if fields.get('image') else ''
            }
            products.append(product)

        return f"Found {len(products)} products: {json.dumps(products, indent=2)}"
    except Exception as e:
        return f"Search error: {str(e)}"


model_id = "global.anthropic.claude-haiku-4-5-20251001-v1:0"
model = BedrockModel(
    model_id=model_id,
)
agent = Agent(
    model=model,
    tools=[search_products],
    system_prompt="You're a helpful assistant. You can do product search, and tell the product details."
)


@app.entrypoint
def strands_agent_bedrock(payload):
    """
    Invoke the agent with a payload.
    """
    user_input = payload.get("prompt")
    print("User input:", user_input)
    response = agent(user_input)
    return response.message['content'][0]['text']


if __name__ == "__main__":
    # strands_agent_bedrock({"prompt": "Search jacket"})  # UNCOMMENT THIS FOR TESTING
    app.run()  # UNCOMMENT THIS FOR DEPLOYMENT, MAKE SURE THE ABOVE LINE IS COMMENTED
