"""
Create ML Connector between OpenSearch Service and Amazon Bedrock Nova Multimodal Embeddings.

This script creates a connector in OpenSearch Service that links to the Bedrock Nova
Multimodal Embeddings model.

Usage:
    python3.11 create_connector.py

After running, note the connector_id from the output. You will need it for the next steps
in OpenSearch Dashboards Dev Tools (see opensearch_setup.md).

Prerequisites:
    - OpenSearchBedrockEmbeddingRole IAM role created
    - IAM principal mapped as a backend role for ml_full_access in OpenSearch Dashboards
    - pip install -r requirements.txt
"""

import boto3
import requests
from requests_aws4auth import AWS4Auth

# ============================================================================
# CONFIGURATION - Change these values for your environment
# ============================================================================

host = ''  # CHANGE THIS - OpenSearch domain endpoint (e.g., https://search-mydomain-xxx.us-east-1.es.amazonaws.com)
region = ''  # CHANGE THIS - AWS region (e.g., us-east-1)
account_id = ''  # CHANGE THIS - Your AWS account ID

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

path = '/_plugins/_ml/connectors/_create'
url = host + path

payload = {
    "name": "Amazon Bedrock Nova multimodal model - text embedding",
    "description": "Test connector for Amazon Bedrock Nova multimodal model - text embedding",
    "version": 1,
    "protocol": "aws_sigv4",
    "credential": {
        "roleArn": f"arn:aws:iam::{account_id}:role/OpenSearchBedrockEmbeddingRole"
    },
    "parameters": {
        "region": region,
        "service_name": "bedrock",
        "model": "amazon.nova-2-multimodal-embeddings-v1:0",
        "input_docs_processed_step_size": 1,
        "dimensions": 1024,
        "embeddingTypes": ["float"],
        "truncationMode": "NONE"
    },
    "actions": [
        {
            "action_type": "predict",
            "method": "POST",
            "headers": {
                "content-type": "application/json",
                "x-amz-content-sha256": "required"
            },
            "url": "https://bedrock-runtime.${parameters.region}.amazonaws.com/model/${parameters.model}/invoke",
            "request_body": '{\n  "taskType": "SINGLE_EMBEDDING",\n  "singleEmbeddingParams": {\n  "embeddingPurpose": "GENERIC_INDEX",\n   "embeddingDimension": ${parameters.dimensions},\n    "text": {\n      "truncationMode": "${parameters.truncationMode}",\n      "value": "${parameters.inputText}"\n    }\n  }\n}',
            "pre_process_function": "connector.pre_process.bedrock.nova.text_embedding",
            "post_process_function": "connector.post_process.bedrock.nova.embedding"
        }
    ]
}

headers = {"Content-Type": "application/json"}

print("Creating ML connector in OpenSearch Service...")
r = requests.post(url, auth=awsauth, json=payload, headers=headers, timeout=15)
print(f"Status Code: {r.status_code}")
print(r.text)

if r.status_code == 200:
    import json
    response = json.loads(r.text)
    connector_id = response.get("connector_id", "")
    print(f"\n✓ Connector created successfully!")
    print(f"  connector_id: {connector_id}")
    print(f"\nNext steps in OpenSearch Dashboards Dev Tools:")
    print(f"  1. Create a model group (see opensearch_setup.md)")
    print(f"  2. Register a model with this connector_id")
    print(f"  3. Deploy the model")