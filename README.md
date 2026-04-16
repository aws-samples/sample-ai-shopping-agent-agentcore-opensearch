# AI Shopping Agent with Amazon Bedrock AgentCore Runtime and Amazon OpenSearch Service

This repository contains the code for building an AI-powered shopping agent using
[Strands Agents](https://github.com/strands-agents/sdk-python),
[Amazon Bedrock AgentCore Runtime](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html),
and [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/).

The agent performs semantic product search using natural language queries, powered by
Amazon Nova Multimodal Embeddings for vector search and Anthropic Claude for response generation.

## Architecture

1. User submits a question
2. AgentCore Runtime receives the request and routes it to the Strands Retail Agent
3. Strands Agent processes the task and invokes the `search_products` tool
4. OpenSearch Service performs semantic search and returns relevant product results
5. Strands Agent invokes Amazon Bedrock LLMs to generate a natural language response
6. Agent response is returned to the user

## Prerequisites

- AWS account with appropriate permissions
- OpenSearch Service domain (version 2.13 or later)

## Repository Structure

| File | Description |
|------|-------------|
| `cloudformation.yaml` | CloudFormation template — VPC, NAT gateway, EC2 instance, and all IAM roles/policies |
| `requirements.txt` | Python dependencies |
| `create_connector.py` | Creates ML connector between OpenSearch and Bedrock Nova embeddings |
| `opensearch_setup.md` | OpenSearch Dashboards Dev Tools commands |
| `search_agent.py` | Strands Agent with product search tool |
| `agentcore.py` | Deploys the agent to Bedrock AgentCore Runtime |

## Setup Steps

### 1. Deploy the CloudFormation Stack

The CloudFormation template creates everything you need:

- **VPC** with public and private subnets, NAT gateway for outbound internet access
- **EC2 instance** in the private subnet, accessible only via SSM Session Manager
- **Python 3.11**, git, and all pip dependencies pre-installed via cfn-init
- **EC2 instance role** with all required permissions: Bedrock, AgentCore, ECR, CodeBuild, IAM, S3, OpenSearch, and SSM
- **OpenSearchBedrockEmbeddingRole** — allows OpenSearch Service to invoke Bedrock embeddings

```bash
aws cloudformation deploy \
  --template-file cloudformation.yaml \
  --stack-name shopping-agent \
  --capabilities CAPABILITY_NAMED_IAM \
  --region <your-region>
```

> **Alternative:** If you prefer not to use CloudFormation, install Python 3.11 locally,
> run `pip install -r requirements.txt`, and create the IAM roles manually as described in the blog post.

### 2. Connect to the EC2 Instance and Map OpenSearch Permissions

After the stack completes, map the EC2 instance role as a backend role for `ml_full_access`
in OpenSearch Dashboards. This is required before running `create_connector.py`:

1. Open OpenSearch Dashboards → Security → Roles → **ml_full_access**
2. Click **Mapped Users** → **Manage Mapping**
3. Under **Backend roles**, add the EC2 role ARN from the stack outputs:
   `arn:aws:iam::<ACCOUNT_ID>:role/shopping-agent-EC2Role`

Then connect to the instance via SSM Session Manager. The instance ID is in the stack outputs.

```bash
aws ssm start-session --target <instance-id> --region <your-region>
```

Switch to `ec2-user` and navigate to the working directory:

```bash
sudo su - ec2-user
cd ~/shopping-agent
```

Python 3.11 and all pip dependencies are already installed. Clone this repo to get the script files:

```bash
git clone <your-repo-url> .
```

### 3. Create ML Connector

Edit `create_connector.py` and set `host`, `region`, and `account_id`, then run:

```bash
python3.11 create_connector.py
```

Note the `connector_id` from the output.

### 4. Register and Deploy Model (OpenSearch Dashboards)

Follow the commands in `opensearch_setup.md` using OpenSearch Dashboards Dev Tools:
- Create a model group
- Register the model with your connector_id
- Deploy the model

### 5. Create Pipeline, Index, and Ingest Data (OpenSearch Dashboards)

Continue with the remaining commands in `opensearch_setup.md`:
- Create the ingest pipeline
- Create the product index
- Ingest sample data
- Test with a query

### 6. Configure OpenSearch Security for Agent

In OpenSearch Dashboards Security:
1. Create a role named `agent-permissions`
2. Add cluster permissions: `cluster:admin/opensearch/ml/models/get`, `cluster:admin/opensearch/ml/predict`
3. Add index permissions for `product*`: `search`, `get`
4. Map the EC2 instance role as a backend role

### 7. Test the Agent Locally

Edit `search_agent.py` and set `host`, `region`, and `model_id` in the `search_products` function.

For local testing, uncomment the test line and comment `app.run()`:

```python
strands_agent_bedrock({"prompt": "Search jacket"})  # Uncomment for testing
# app.run()  # Comment for testing
```

```bash
python3.11 search_agent.py
```

### 8. Deploy to AgentCore Runtime

Revert `search_agent.py` for deployment (comment test line, uncomment `app.run()`).

Edit `agentcore.py` and set `REGION` and `OPENSEARCH_DOMAIN_NAME`, then run:

```bash
python3.11 agentcore.py
```

### 9. Map AgentCore Execution Role in OpenSearch

In OpenSearch Dashboards, add the AgentCore execution role as a backend role for `agent-permissions`:

```
arn:aws:iam::<ACCOUNT_ID>:role/AmazonBedrockAgentCoreSDKRuntime-<REGION>-custom
```

### 10. Invoke the Agent

Test using the AgentCore Agent Sandbox with a prompt like: `Search jacket less than 50$`

## Cleanup

To avoid incurring future charges:
1. Delete the OpenSearch Service domain
2. Delete Amazon Bedrock AgentCore Runtime resources
3. Delete the CloudFormation stack: `aws cloudformation delete-stack --stack-name shopping-agent`

## Authors

- Omama Khurshid — GTM Specialist Solutions Architect Analytics, AWS
- Jumana Nagaria — Prototyping Architect, AWS
- Canberk Keles — Solutions Architect, AWS
