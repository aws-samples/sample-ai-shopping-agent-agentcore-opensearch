"""
Step 8: Configure and launch the Strands Agent to Bedrock AgentCore Runtime.

This script creates the AgentCore execution IAM role with necessary permissions,
then uses the starter toolkit to build and deploy the agent as a containerized
application on AgentCore Runtime.

Usage:
    python agentcore.py

Prerequisites:
    - Completed Step 7 (search_agent.py tested locally)
    - AgentCoreAccessPolicy attached to the IAM principal running this script
      (see setup_iam_principals.py)
    - pip install -r requirements.txt
"""

from bedrock_agentcore_starter_toolkit import Runtime
from boto3.session import Session
import json

# ============================================================================
# CONFIGURATION PARAMETERS - Customize these for your environment
# ============================================================================

# AWS Configuration
REGION = ''  # CHANGE THIS - Your AWS region (e.g., us-east-1)
AGENT_NAME = 'search_agent'

# OpenSearch Configuration
OPENSEARCH_DOMAIN_NAME = ''  # CHANGE THIS - Your OpenSearch domain hostname (e.g., 'search-mydomain-xxxxx.us-east-1.es.amazonaws.com')

# ============================================================================
# AUTO-DETECTED AWS CONFIGURATION
# ============================================================================

# Initialize AWS session
boto_session = Session(region_name=REGION)
region = boto_session.region_name
account_id = boto_session.client('sts').get_caller_identity()['Account']

print(f"Deploying to AWS Account: {account_id}")
print(f"Region: {region}")
print(f"Agent Name: {AGENT_NAME}")
print(f"OpenSearch Domain: {OPENSEARCH_DOMAIN_NAME}")

# ============================================================================
# IAM ROLE SETUP
# ============================================================================

# Define the execution role
execution_role_name = f"AmazonBedrockAgentCoreSDKRuntime-{region}-custom"
execution_role_arn = f"arn:aws:iam::{account_id}:role/{execution_role_name}"

# Create IAM client
iam_client = boto_session.client('iam')

# Create execution role with proper trust policy and permissions
try:
    # Trust policy for Bedrock AgentCore
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {
                    "Service": "bedrock-agentcore.amazonaws.com"
                },
                "Action": "sts:AssumeRole"
            }
        ]
    }

    # Create the role
    try:
        iam_client.create_role(
            RoleName=execution_role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description="Execution role for Bedrock AgentCore with full permissions"
        )
        print(f"✓ Created execution role: {execution_role_name}")
    except iam_client.exceptions.EntityAlreadyExistsException:
        print(f"✓ Execution role already exists: {execution_role_name}")

    # Comprehensive execution policy with all required permissions
    bedrock_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "BedrockModelAccess",
                "Effect": "Allow",
                "Action": [
                    "bedrock:InvokeModel",
                    "bedrock:InvokeModelWithResponseStream"
                ],
                "Resource": [
                    "arn:aws:bedrock:*::foundation-model/*",
                    f"arn:aws:bedrock:{region}:{account_id}:inference-profile/*"
                ]
            },
            {
                "Sid": "ECRAuthToken",
                "Effect": "Allow",
                "Action": [
                    "ecr:GetAuthorizationToken"
                ],
                "Resource": "*"
            },
            {
                "Sid": "ECRImageAccess",
                "Effect": "Allow",
                "Action": [
                    "ecr:BatchGetImage",
                    "ecr:GetDownloadUrlForLayer",
                    "ecr:BatchCheckLayerAvailability"
                ],
                "Resource": f"arn:aws:ecr:{region}:{account_id}:repository/bedrock-agentcore-*"
            },
            {
                "Sid": "CloudWatchLogsAccess",
                "Effect": "Allow",
                "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    "logs:DescribeLogGroups",
                    "logs:DescribeLogStreams"
                ],
                "Resource": f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"
            },
            {
                "Sid": "CloudWatchTransactionSearchAccess",
                "Effect": "Allow",
                "Action": [
                    "xray:PutTraceSegments",
                    "xray:PutTelemetryRecords"
                ],
                "Resource": "*"
            },
            {
                "Sid": "OpenSearchAccess",
                "Effect": "Allow",
                "Action": [
                    "es:ESHttpGet",
                    "es:ESHttpPost",
                    "es:ESHttpPut"
                ],
                "Resource": f"arn:aws:es:{region}:{account_id}:domain/{OPENSEARCH_DOMAIN_NAME}/*"
            }
        ]
    }

    iam_client.put_role_policy(
        RoleName=execution_role_name,
        PolicyName="BedrockAgentCoreExecutionPolicy",
        PolicyDocument=json.dumps(bedrock_policy)
    )
    print("✓ Attached comprehensive execution policies to role")
    print("  - Bedrock model access (foundation models + inference profiles)")
    print("  - ECR image access")
    print("  - CloudWatch Logs (application logs)")
    print("  - X-Ray tracing (observability)")
    print(f"  - OpenSearch access ({OPENSEARCH_DOMAIN_NAME})")

except Exception as e:
    print(f"✗ Error creating execution role: {e}")
    raise

# ============================================================================
# AGENT CONFIGURATION AND DEPLOYMENT
# ============================================================================

print("Configuring agent...")
agentcore_runtime = Runtime()

response = agentcore_runtime.configure(
    entrypoint="search_agent.py",
    execution_role=execution_role_arn,
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region=region,
    agent_name=AGENT_NAME
)
print("✓ Configuration complete")

print("Building and deploying agent...")
print("   (This may take a few minutes as CodeBuild creates ARM64 container)")
launch_result = agentcore_runtime.launch()
print("✓ Agent deployed successfully!")
