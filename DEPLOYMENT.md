# CareerGraph Deployment Guide

Complete guide for deploying CareerGraph to AWS with Docker, GitHub Actions CI/CD, ECR, and EC2.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [AWS Infrastructure Setup](#aws-infrastructure-setup)
3. [GitHub Configuration](#github-configuration)
4. [Local Testing](#local-testing)
5. [Deployment](#deployment)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools
- [AWS CLI](https://aws.amazon.com/cli/) installed and configured
- [Docker](https://www.docker.com/) installed locally
- [Git](https://git-scm.com/) for version control
- GitHub account with repository access

### Required AWS Resources
- AWS Account with appropriate permissions
- EC2 instance (t2.small or larger recommended)
- ECR repository for Docker images

### Cost Estimation
- **EC2 t2.small**: ~$17/month (on-demand pricing)
- **ECR Storage**: ~$0.10/GB/month
- **Data Transfer**: Varies based on usage
- **Total estimated**: ~$20-30/month

## AWS Infrastructure Setup

### Step 1: Create ECR Repository

```bash
# Set your region
export AWS_REGION=us-east-1

# Create ECR repository
aws ecr create-repository \
    --repository-name careergraph \
    --region $AWS_REGION

# Save the repository URI (you'll need this later)
ECR_URI=$(aws ecr describe-repositories --repository-names careergraph --region $AWS_REGION --query 'repositories[0].repositoryUri' --output text)
echo "ECR Repository URI: $ECR_URI"
```

### Step 2: Launch EC2 Instance

#### Using AWS Console:

1. Navigate to EC2 Dashboard
2. Click "Launch Instance"
3. Configure instance:
   - **Name**: careergraph-server
   - **AMI**: Amazon Linux 2023 or Ubuntu 22.04 LTS
   - **Instance type**: t2.small (or t2.micro for testing)
   - **Key pair**: Create new or select existing
   - **Network settings**:
     - Allow SSH (port 22) from your IP
     - Allow HTTP (port 80) from anywhere
     - Allow Custom TCP (port 8000) from anywhere
4. Configure storage: 20 GB gp3 (recommended)
5. Launch instance

#### Using AWS CLI:

```bash
# Create security group
aws ec2 create-security-group \
    --group-name careergraph-sg \
    --description "Security group for CareerGraph" \
    --region $AWS_REGION

# Get security group ID
SG_ID=$(aws ec2 describe-security-groups --group-names careergraph-sg --region $AWS_REGION --query 'SecurityGroups[0].GroupId' --output text)

# Add ingress rules
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 22 --cidr 0.0.0.0/0 --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 80 --cidr 0.0.0.0/0 --region $AWS_REGION
aws ec2 authorize-security-group-ingress --group-id $SG_ID --protocol tcp --port 8000 --cidr 0.0.0.0/0 --region $AWS_REGION

# Launch instance (update AMI ID for your region)
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.small \
    --key-name YOUR_KEY_NAME \
    --security-group-ids $SG_ID \
    --region $AWS_REGION \
    --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=careergraph-server}]'
```

### Step 3: Configure EC2 Instance

SSH into your EC2 instance and install Docker:

```bash
# SSH into EC2
ssh -i your-key.pem ec2-user@<EC2_PUBLIC_IP>

# Update system
sudo yum update -y  # For Amazon Linux
# OR
sudo apt-get update && sudo apt-get upgrade -y  # For Ubuntu

# Install Docker
sudo yum install docker -y  # For Amazon Linux
# OR
sudo apt-get install, docker.io -y  # For Ubuntu

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add user to docker group
sudo usermod -aG docker ec2-user  # or ubuntu
newgrp docker

# Install AWS CLI (if not already installed)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Enter region (e.g., us-east-1)
# Leave default output format blank or enter 'json'

# Test Docker
docker --version
aws --version
```

## GitHub Configuration

### Step 1: Add GitHub Secrets

Navigate to your repository on GitHub → Settings → Secrets and variables → Actions → New repository secret

Add the following secrets:

| Secret Name | Description | Example Value |
|------------|-------------|---------------|
| `AWS_ACCESS_KEY_ID` | AWS access key for deployment | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | AWS secret access key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_REGION` | AWS region | `us-east-1` |
| `ECR_REPOSITORY` | ECR repository name | `careergraph` |
| `EC2_HOST` | EC2 public IP or hostname | `54.123.45.67` |
| `EC2_USER` | EC2 SSH username | `ec2-user` or `ubuntu` |
| `EC2_SSH_KEY` | Private SSH key for EC2 | Contents of your `.pem` file |

### Step 2: Verify Workflows

The repository includes two GitHub Actions workflows:

1. **CI Workflow** (`.github/workflows/ci.yml`):
   - Runs on push to main/develop
   - Lints code
   - Builds Docker image
   - Tests Docker image
   - Pushes to ECR (main branch only)

2. **CD Workflow** (`.github/workflows/deploy.yml`):
   - Triggers after successful CI on main
   - Deploys latest image to EC2
   - Runs health checks

## Local Testing

### Test with Docker

```bash
# Build the Docker image
docker build -t careergraph:local .

# Run the container
docker run -d -p 8000:8000 --name careergraph-test careergraph:local

# Test the application
curl http://localhost:8000/health

# View logs
docker logs careergraph-test

# Stop and remove
docker stop careergraph-test
docker rm careergraph-test
```

### Test with docker-compose

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Test the application
curl http://localhost:8000/health

# Stop the application
docker-compose down
```

## Deployment

### Automatic Deployment (Recommended)

1. Make changes to your code
2. Commit and push to main branch:
   ```bash
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```
3. GitHub Actions will automatically:
   - Run tests
   - Build Docker image
   - Push to ECR
   - Deploy to EC2
4. Monitor the deployment in the "Actions" tab on GitHub

### Manual Deployment

If you need to deploy manually:

```bash
# Login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin <ECR_URI>

# Build and tag image
docker build -t careergraph:latest .
docker tag careergraph:latest <ECR_URI>:latest

# Push to ECR
docker push <ECR_URI>:latest

# SSH to EC2 and deploy
ssh -i your-key.pem ec2-user@<EC2_PUBLIC_IP>

# On EC2:
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <ECR_URI>
docker pull <ECR_URI>:latest
docker stop careergraph || true
docker rm careergraph || true
docker run -d --name careergraph -p 8000:8000 --restart unless-stopped <ECR_URI>:latest
```

## Monitoring

### Check Application Status

```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@<EC2_PUBLIC_IP>

# Check container status
docker ps

# View logs
docker logs careergraph

# Follow logs in real-time
docker logs -f careergraph

# Check resource usage
docker stats careergraph
```

### Health Check

```bash
# From your local machine
curl http://<EC2_PUBLIC_IP>:8000/health

# Expected response:
# {"status":"healthy","timestamp":"...","openai_configured":false}
```

### Access the Application

Open in your browser:
```
http://<EC2_PUBLIC_IP>:8000
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs careergraph

# Check if port is already in use
sudo netstat -tulpn | grep 8000

# Remove old containers
docker stop careergraph
docker rm careergraph

# Pull latest image and restart
docker pull <ECR_URI>:latest
docker run -d --name careergraph -p 8000:8000 --restart unless-stopped <ECR_URI>:latest
```

### ECR Login Issues

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Re-login to ECR
aws ecr get-login-password --region $AWS_REGION | docker login --username AWS --password-stdin <ECR_URI>
```

### GitHub Actions Failing

1. Check workflow logs in GitHub Actions tab
2. Verify all secrets are set correctly
3. Ensure EC2 instance is running
4. Check EC2 security group allows SSH from GitHub's IP ranges

### Application Not Responding

```bash
# Restart container
docker restart careergraph

# Check EC2 security group
# Ensure port 8000 is open

# Check EC2 instance status
aws ec2 describe-instance-status --instance-ids <INSTANCE_ID>
```

### Performance Issues

```bash
# Check resource usage
docker stats careergraph

# If memory/CPU is high, consider upgrading EC2 instance type
# Stop instance, change instance type in AWS console, restart

# Clear old Docker images
docker image prune -af
```

## Production Best Practices

### 1. Enable HTTPS

Use nginx or ALB with SSL certificate:

```bash
# Install cert bot and nginx
sudo yum install nginx certbot python3-certbot-nginx -y

# Configure nginx as reverse proxy
# Edit /etc/nginx/nginx.conf

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com
```

### 2. Set Up Domain Name

1. Register a domain (e.g., on Route 53)
2. Create an A record pointing to EC2 public IP
3. Update security group if needed

### 3. Enable CloudWatch Logs

```bash
# Install CloudWatch agent on EC2
wget https://s3.amazonaws.com/amazoncloudwatch-agent/amazon_linux/amd64/latest/amazon-cloudwatch-agent.rpm
sudo rpm -U ./amazon-cloudwatch-agent.rpm

# Configure CloudWatch agent
sudo /opt/aws/amazon-cloudwatch-agent/ config-wizard
```

### 4. Implement Backups

- Use EBS snapshots for EC2 volumes
- Consider multi-AZ deployment for high availability

### 5. Rate Limiting

Consider implementing rate limiting to protect against abuse:
- Use AWS WAF for application-level protection
- Implement API rate limiting in application code

## Support

For issues or questions:
- Check existing GitHub Issues
- Create a new issue with detailed description
- Include logs and error messages

## License

See LICENSE file in repository.
