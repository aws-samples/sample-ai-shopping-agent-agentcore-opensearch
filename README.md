# AI Shopping Agent with Amazon Bedrock AgentCore Runtime and Amazon OpenSearch Service

This repository contains the code for building an AI-powered shopping agent using
[Strands Agents](https://github.com/strands-agents/sdk-python),
[Amazon Bedrock AgentCore Runtime](https://docs.aws.amazon.com/bedrock/latest/userguide/agentcore.html),
and [Amazon OpenSearch Service](https://aws.amazon.com/opensearch-service/).

**⚠️ IMPORTANT**: This is a sample application for demonstration and educational purposes only. It should not be used in production without additional security hardening.

The agent performs semantic product search using natural language queries, powered by
Amazon Nova Multimodal Embeddings for vector search and Anthropic Claude for response generation.

## Architecture

![Architecture Diagram](images/diagram.png)

### Data Flow

1. User sends question via CloudFront (HTTPS), authenticates with Cognito
2. CloudFront routes request via VPC Origin to internal ALB, then to EC2
3. Frontend app (EC2) invokes AgentCore Runtime API
4. Strands Agent invokes `search_products` tool → OpenSearch performs semantic search (Nova embeddings via Bedrock)
5. Strands Agent invokes Bedrock (Claude) to generate natural language response
6. Agent response is returned to EC2, then to user via CloudFront

### Infrastructure Components

- **VPC**: Private network with public and private subnets across 2 availability zones
- **CloudFront Distribution**: Provides HTTPS access with TLS 1.2+ via VPC Origin
- **Amazon Cognito**: User authentication with hosted UI login (self-signup disabled)
- **Internal Application Load Balancer**: Routes traffic from CloudFront to EC2 (private, no public access)
- **EC2 Instance**: Runs in private subnet, hosts the frontend app and deploys agent via AgentCore CLI
- **NAT Gateway**: Enables outbound internet access for the EC2 instance
- **OpenSearch Service**: Vector database for semantic product search (OpenSearch 3.5)
- **Bedrock AgentCore Runtime**: Serverless agent orchestration service

## Prerequisites

- **AWS account** with permissions for CloudFormation, EC2, VPC, IAM, Bedrock, AgentCore, OpenSearch, and SSM
- **AWS CLI** configured with credentials
- **Model Access in Amazon Bedrock:** Anthropic Claude Haiku 4.5 and Amazon Nova Multimodal Embeddings

## Setup Steps

### 1. Deploy the CloudFormation Stack

**Option A: Create OpenSearch domain automatically (Recommended)**

```bash
aws cloudformation deploy \
  --template-file cloudformation.yaml \
  --stack-name shopping-agent \
  --parameter-overrides \
      CreateOpenSearchDomain=true \
      OpenSearchDomainName=shopping-agent-search \
      OpenSearchAdminUsername=admin \
      OpenSearchAdminPassword='YourSecurePassword123!' \
  --capabilities CAPABILITY_NAMED_IAM \
  --region <your-region>
```

**⏱️ Deployment Time:** ~20-35 minutes (includes OpenSearch domain creation)

**Option B: Use an existing OpenSearch domain**

If you already have an OpenSearch domain, set `CreateOpenSearchDomain=false` and provide your domain name:

```bash
aws cloudformation deploy \
  --template-file cloudformation.yaml \
  --stack-name shopping-agent \
  --parameter-overrides \
      CreateOpenSearchDomain=false \
      OpenSearchDomainName=<your-existing-domain-name> \
  --capabilities CAPABILITY_NAMED_IAM \
  --region <your-region>
```

Once complete, get the stack outputs:

```bash
aws cloudformation describe-stacks \
  --stack-name shopping-agent \
  --query 'Stacks[0].Outputs' \
  --output table
```

Note these values from the outputs: `InstanceId`, `OpenSearchDomainEndpoint`, `EC2RoleArn`, `OpenSearchBedrockEmbeddingRoleArn`, `AppURL`.

### 2. Connect to EC2 and Clone Repo

Connect via SSM Session Manager:

```bash
aws ssm start-session --target <instance-id> --region <your-region>
```

```bash
sudo su
cd ~/shopping-agent
git clone <your-repo-url> .
```

Python 3.11, Node.js 20, AgentCore CLI, and uv are pre-installed on the instance.

### 3. Configure OpenSearch Security

Open OpenSearch Dashboards (endpoint from stack outputs) and log in with admin credentials.

#### 3a. Map Embedding Role to `ml_full_access`

1. **Security** → **Roles** → **`ml_full_access`** → **Mapped users** → **Manage mapping**
2. Under **Backend roles**, add:
   - `arn:aws:iam::<ACCOUNT_ID>:role/OpenSearchBedrockEmbeddingRole-<REGION>`
   - `arn:aws:iam::<ACCOUNT_ID>:role/shopping-agent-EC2Role`
3. Click **Map**

#### 3b. Create `shopping_agent_setup` Role

1. **Security** → **Roles** → **Create role**
2. **Name:** `shopping_agent_setup`
3. **Cluster permissions** — add individually:
   ```
   cluster:admin/ingest/pipeline/put
   cluster:admin/ingest/pipeline/get
   cluster:admin/ingest/pipeline/delete
   cluster:admin/opensearch/ml/create_connector
   cluster:admin/opensearch/ml/register_model_group
   cluster:admin/opensearch/ml/register_model
   cluster:admin/opensearch/ml/deploy_model
   cluster:admin/opensearch/ml/predict
   cluster:admin/opensearch/ml/undeploy_model
   cluster:admin/opensearch/ml/delete_connector
   cluster:admin/opensearch/ml/models/get
   cluster:monitor/nodes/info
   cluster:monitor/health
   ```
4. **Index permissions** — index patterns: `*`, add individually:
   ```
   indices:admin/create
   indices:admin/delete
   indices:admin/mapping/put
   indices:data/write/index
   indices:data/write/bulk
   indices:data/write/delete
   indices:data/read/search
   indices:data/read/get
   ```
5. **Create**, then **Mapped users** → **Manage mapping** → add `admin` under **Users** → **Map**

> **Note:** Wildcard permissions (e.g., `cluster:admin/opensearch/ml/*`) are not supported in all OpenSearch versions. Use explicit permissions as listed above.

#### 3c. Create `agent-permissions` Role

1. **Security** → **Roles** → **Create role**
2. **Name:** `agent-permissions`
3. **Cluster permissions:**
   - `cluster:admin/opensearch/ml/models/get`
   - `cluster:admin/opensearch/ml/predict`
4. **Index permissions** — index patterns: `product*`:
   - `indices:data/read/search`
   - `indices:data/read/get`
5. **Create**, then **Mapped users** → **Manage mapping**
6. Under **Backend roles**, add: `arn:aws:iam::<ACCOUNT_ID>:role/shopping-agent-EC2Role`
7. Click **Map**

### 4. Create ML Connector

Edit `create_connector.py` and set `host`, `region`, and `account_id`, then run:

```bash
python3.11 create_connector.py
```

Note the `connector_id` from the output.

### 5. Register and Deploy Model (OpenSearch Dashboards)

Follow the commands in [`opensearch_setup.md`](opensearch_setup.md) using OpenSearch Dashboards **Dev Tools**:

- Create a model group
- Register the model with your `connector_id`
- Deploy the model

### 6. Create Pipeline, Index, and Ingest Data (OpenSearch Dashboards)

Continue with the remaining commands in [`opensearch_setup.md`](opensearch_setup.md):

- Create the ingest pipeline
- Create the product index
- Ingest sample data
- Test with a neural search query

### 7. Test Agent Locally and Deploy to AgentCore Runtime

#### Configure the Agent

Edit `search_agent.py` and set `host`, `region`, and `model_id` in the `search_products` function:

- `host` — your OpenSearch domain endpoint (from stack outputs)
- `region` — your AWS region (e.g., `us-east-1`)
- `model_id` — your OpenSearch embedding model ID (from Step 5)

> **Important:** The `model_id` inside `search_products` must be your **OpenSearch embedding model ID** (from Step 5), NOT the Claude/Bedrock LLM model ID.

#### Test Locally

Uncomment the test line at the bottom of `search_agent.py` and comment `app.run()`:

```python
strands_agent_bedrock({"prompt": "Search jacket"})  # Uncomment for testing
# app.run()  # Comment for testing
```

```bash
python3.11 search_agent.py
```

You should see product results from your OpenSearch index. After testing, revert the changes (comment test line, uncomment `app.run()`).

#### Deploy to AgentCore

```bash
cd ~/shopping-agent
agentcore create --name ShoppingAgent --defaults
cd ShoppingAgent
cp ../search_agent.py app/ShoppingAgent/main.py
```

Add dependencies:

```bash
cd app/ShoppingAgent
uv add opensearch-py requests-aws4auth boto3
cd ../..
```

Deploy (~5-10 minutes):

```bash
agentcore deploy
```

Verify:

```bash
agentcore status
```

**Save the Runtime ARN** from the output.

### 8. Map AgentCore Execution Role in OpenSearch

1. Find the execution role: **IAM Console** → **Roles** → search for `BedrockAgentCore`
2. Copy the role ARN
3. **OpenSearch Dashboards** → **Security** → **Roles** → **`agent-permissions`** → **Mapped users** → **Manage mapping**
4. Under **Backend roles**, add the execution role ARN
5. Click **Map**

### 9. Run the Frontend

On the EC2 instance (via SSM session from Step 2):

```bash
cd ~/shopping-agent/frontend
pip3.11 install -r requirements.txt
```

Edit `api.py` — set `REGION` and `AGENT_RUNTIME_ARN` (from `agentcore status` output):

```python
REGION = "us-east-1"  # Your AWS region
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:<ACCOUNT_ID>:runtime/<AGENT_NAME>"
```

Start the app:

```bash
nohup python3.11 api.py > ~/api.log 2>&1 &
```

#### Access the Application

Open the `AppURL` from CloudFormation outputs in your browser. You will be redirected to the **Cognito login page**.

Create a user (from your local terminal, not EC2):

```bash
aws cognito-idp admin-create-user \
  --user-pool-id <POOL_ID> \
  --username user@example.com \
  --temporary-password "TempPass1!" \
  --user-attributes Name=email,Value=user@example.com Name=email_verified,Value=true

aws cognito-idp admin-set-user-password \
  --user-pool-id <POOL_ID> \
  --username user@example.com \
  --password "YourPassword1!" \
  --permanent
```

#### Try These Sample Queries

- "Search for jackets under $50"
- "Find men's clothing"
- "Show me jewelry"
- "What t-shirts are available?"
- "Search for a backpack"

![Shopping Assistant Demo](images/the-website.png)

## Cleanup

1. **Delete the AgentCore Runtime:**
   ```bash
   cd ~/shopping-agent/ShoppingAgent
   agentcore remove all
   agentcore deploy
   ```

2. **Delete the CloudFormation stack:**
   ```bash
   aws cloudformation delete-stack --stack-name shopping-agent --region <your-region>
   ```

The stack deletion removes all resources (OpenSearch, VPC, EC2, ALB, NAT Gateway, IAM roles). Takes ~20-40 minutes.

> **Note:** NAT Gateway and OpenSearch domain incur the highest costs. Delete promptly when done testing.

## Authors

- Omama Khurshid — GTM Specialist Solutions Architect Analytics, AWS
- Jumana Nagaria — Prototyping Architect, AWS
- Canberk Keles — Solutions Architect, AWS
