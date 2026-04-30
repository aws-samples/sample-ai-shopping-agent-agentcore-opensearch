# Deployment Guide for AI Shopping Agent

## Quick Start

This guide provides a streamlined deployment process for the blog post demo.

## Architecture Overview

```
Internet → ALB (Public Subnets) → EC2 (Private Subnet) → AgentCore Runtime
                                         ↓
                                   OpenSearch Service
                                         ↓
                                   Bedrock (Claude + Nova)
```

### Network Architecture

- **2 Public Subnets** (AZ1, AZ2): Host the Application Load Balancer
- **1 Private Subnet** (AZ1): Hosts the EC2 instance running the agent and Streamlit
- **NAT Gateway**: Enables EC2 to reach AWS services and download packages
- **Internet Gateway**: Provides public internet access to the ALB

### Security

- EC2 instance has **no public IP** and is only accessible via:
  - AWS Systems Manager (SSM) Session Manager for administrative access
  - Application Load Balancer on port 8501 for Streamlit traffic
- Security groups enforce least-privilege access:
  - ALB accepts HTTP (80) from internet
  - EC2 accepts connections only from ALB on port 8501
  - EC2 can make HTTPS calls to AWS services

## Deployment Steps

### 1. Deploy Infrastructure

**Option A: Create OpenSearch domain automatically (OpenSearch 3.5)**

```bash
aws cloudformation deploy \
  --template-file cloudformation.yaml \
  --stack-name shopping-agent \
  --parameter-overrides CreateOpenSearchDomain=true \
  --capabilities CAPABILITY_NAMED_IAM \
  --region <your-region>
```

**Option B: Use existing OpenSearch domain**

```bash
aws cloudformation deploy \
  --template-file cloudformation.yaml \
  --stack-name shopping-agent \
  --parameter-overrides \
      CreateOpenSearchDomain=false \
      OpenSearchDomainName=<your-opensearch-domain> \
  --capabilities CAPABILITY_NAMED_IAM \
  --region <your-region>
```

**Multi-Region Note:** This template is fully portable across AWS regions. Replace `<your-region>` with any region supporting the required services (e.g., us-east-1, us-west-2, eu-west-1, ap-southeast-1).

**Wait**: Stack creation takes ~5-10 minutes (NAT Gateway provisioning)

### 2. Get Stack Outputs

```bash
aws cloudformation describe-stacks \
  --stack-name shopping-agent \
  --query 'Stacks[0].Outputs' \
  --output table
```

Note these values:
- `InstanceId`: For SSM connection
- `EC2RoleArn`: For OpenSearch mapping
- `LoadBalancerDNS`: For accessing the app

### 3. Connect to EC2 Instance

```bash
aws ssm start-session \
  --target <instance-id> \
  --region us-east-1
```

Switch to ec2-user:
```bash
sudo su - ec2-user
cd ~/shopping-agent
```

### 4. Complete OpenSearch Setup

Follow steps in `opensearch_setup.md`:
1. Run `create_connector.py`
2. Create model group, register model, deploy model
3. Create ingest pipeline and product index
4. Ingest sample data
5. Map IAM roles in OpenSearch Dashboards Security

### 5. Deploy Agent to AgentCore

Edit `agentcore.py` with your OpenSearch domain name and region, then:

```bash
python3.11 agentcore.py
```

**Save the Agent Runtime ARN** from the output.

### 6. Configure and Run Streamlit

Clone your repository:
```bash
git clone <repo-url> .
```

Edit `app.py`:
```python
REGION = "us-east-1"
AGENT_RUNTIME_ARN = "arn:aws:bedrock-agentcore:..."
```

Start Streamlit:
```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Or run in background:
```bash
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 > streamlit.log 2>&1 &
```

### 7. Access the Application

Open the ALB URL in your browser:
```
http://<LoadBalancerDNS>
```

## Troubleshooting

### Streamlit Not Accessible

1. Check Streamlit is running:
   ```bash
   ps aux | grep streamlit
   ```

2. Check target health:
   ```bash
   aws elbv2 describe-target-health \
     --target-group-arn <from-cloudformation-outputs>
   ```

3. Verify security groups allow ALB → EC2 on port 8501

### Agent Errors

1. Check CloudWatch Logs for AgentCore Runtime
2. Verify OpenSearch IAM role mappings
3. Test agent locally in `search_agent.py` before deploying

### Connection Issues

1. Verify NAT Gateway is running
2. Check route tables for private subnet
3. Ensure security group egress rules allow HTTPS

## Cost Considerations

Approximate monthly costs (us-east-1):

- **NAT Gateway**: ~$32/month + data transfer
- **Application Load Balancer**: ~$16/month + LCU charges
- **EC2 t3.medium**: ~$30/month (on-demand)
- **OpenSearch 2x t3.medium.search**: ~$72/month
- **Bedrock**: Pay per request
- **AgentCore Runtime**: Pay per invocation

**Total**: ~$100-150/month for a development environment

## Production Recommendations

1. **HTTPS**: Add ACM certificate to ALB listener
2. **Authentication**: Integrate AWS Cognito or OAuth
3. **High Availability**: Deploy EC2 instances in multiple AZs with Auto Scaling
4. **Monitoring**: Enable CloudWatch detailed monitoring and alarms
5. **Logging**: Configure structured logging for Streamlit and agent
6. **Secrets**: Use AWS Secrets Manager for sensitive configuration
7. **Container**: Package as Docker image for ECS/Fargate deployment

## Cleanup

```bash
# Stop Streamlit on EC2
# Delete AgentCore Runtime via console/CLI
# Delete OpenSearch domain
aws cloudformation delete-stack --stack-name shopping-agent
```
