# Setup and Installation Guide

This guide provides detailed instructions for setting up and configuring the real-time agent system.

## Prerequisites

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 1GB free space

### Azure Requirements

Choose one of the following Azure AI services:

#### Azure OpenAI
- Azure subscription with access to Azure OpenAI Service
- Deployed GPT model (GPT-3.5 or GPT-4 recommended)
- API endpoint and access key

#### AI Foundry
- Azure subscription with access to AI Foundry
- Configured AI Foundry workspace
- Model deployment and endpoint access

## Installation Methods

### Method 1: Git Clone (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/PerfectThymeTech/real-time-agent.git
cd real-time-agent

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .
```

### Method 2: Direct Installation (Future)

```bash
# When published to PyPI
pip install real-time-agent
```

## Configuration

### Step 1: Environment Setup

1. Copy the configuration template:
   ```bash
   cp config/.env.template .env
   ```

2. Edit the `.env` file with your specific configuration:
   ```bash
   nano .env  # or use your preferred editor
   ```

### Step 2: Azure OpenAI Configuration

If using Azure OpenAI, configure these settings:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-01

# Set provider
REAL_TIME_AGENT_PROVIDER=azure_openai
```

#### Getting Azure OpenAI Credentials

1. **Create Azure OpenAI Resource**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Create a new Azure OpenAI resource
   - Note the endpoint URL and region

2. **Deploy a Model**:
   - In the Azure OpenAI Studio, go to Deployments
   - Create a new deployment with GPT-3.5 or GPT-4
   - Note the deployment name

3. **Get API Key**:
   - In the Azure OpenAI resource, go to Keys and Endpoint
   - Copy either Key 1 or Key 2
   - Copy the Endpoint URL

### Step 3: AI Foundry Configuration

If using AI Foundry, configure these settings:

```env
# AI Foundry Configuration
AI_FOUNDRY_ENDPOINT=https://your-foundry-endpoint.com/
AI_FOUNDRY_API_KEY=your-foundry-api-key-here

# Set provider
REAL_TIME_AGENT_PROVIDER=ai_foundry
```

#### Getting AI Foundry Credentials

1. **Access AI Foundry Workspace**:
   - Go to [AI Foundry](https://ai.azure.com)
   - Select or create a workspace

2. **Deploy a Model**:
   - Choose a model from the model catalog
   - Deploy it to your workspace
   - Note the endpoint URL

3. **Get API Key**:
   - In your workspace, go to the deployment
   - Copy the API key and endpoint URL

### Step 4: Advanced Configuration

Additional configuration options:

```env
# Agent Behavior
REAL_TIME_AGENT_MAX_TOKENS=1000
REAL_TIME_AGENT_TEMPERATURE=0.7
REAL_TIME_AGENT_STREAMING=true
REAL_TIME_AGENT_SYSTEM_PROMPT=You are a helpful AI assistant.

# Connection Settings
REAL_TIME_AGENT_WEBSOCKET_TIMEOUT=30
REAL_TIME_AGENT_HEARTBEAT_INTERVAL=10
REAL_TIME_AGENT_MAX_RECONNECT_ATTEMPTS=5

# Logging
REAL_TIME_AGENT_LOG_LEVEL=INFO
```

## Authentication Methods

### Method 1: API Key Authentication (Simplest)

Set API keys directly in environment variables:

```env
AZURE_OPENAI_API_KEY=your-api-key
AI_FOUNDRY_API_KEY=your-api-key
```

### Method 2: Managed Identity (Production Recommended)

For production deployments, use Azure Managed Identity:

1. **Configure Managed Identity**:
   ```bash
   # No API key needed in environment
   # Remove or comment out API key variables
   # AZURE_OPENAI_API_KEY=
   ```

2. **Grant Permissions**:
   - Assign "Cognitive Services OpenAI User" role to the managed identity
   - For AI Foundry, assign appropriate workspace permissions

3. **Code will automatically use**:
   ```python
   # The providers automatically detect and use managed identity
   # when no API key is provided
   ```

## Verification

### Step 1: Test Installation

```bash
# Test basic import
python -c "import real_time_agent; print('Installation successful!')"
```

### Step 2: Run Basic Example

```bash
# Make sure your .env file is configured
python src/real_time_agent/examples/basic_usage.py
```

Expected output:
```
INFO - Real-time agent initialized successfully!
INFO - User: Hello! Can you help me understand what real-time agents are?
INFO - Assistant: [Response about real-time agents]
...
```

### Step 3: Test Streaming

```bash
python src/real_time_agent/examples/advanced_streaming.py
```

You should see real-time streaming responses.

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Error**: `Authentication failed` or `401 Unauthorized`

**Solutions**:
- Verify API key is correct
- Check endpoint URL format
- Ensure the resource has proper permissions
- For managed identity, verify role assignments

#### 2. Model Not Found

**Error**: `The model 'gpt-4' does not exist`

**Solutions**:
- Verify deployment name in Azure OpenAI Studio
- Check that the model is properly deployed
- Ensure the deployment name matches the configuration

#### 3. Network Connectivity

**Error**: `Connection timeout` or `Cannot reach endpoint`

**Solutions**:
- Verify endpoint URL is correct
- Check network connectivity
- Verify firewall settings
- Test endpoint accessibility with curl:
  ```bash
  curl -H "Authorization: Bearer YOUR_API_KEY" YOUR_ENDPOINT/openai/deployments/YOUR_DEPLOYMENT/chat/completions?api-version=2024-02-01
  ```

#### 4. Streaming Issues

**Error**: `Streaming not supported` or broken streaming

**Solutions**:
- Verify streaming is enabled in configuration
- Check that the model supports streaming
- Test with `streaming=False` first

### Debug Mode

Enable debug logging for detailed troubleshooting:

```env
REAL_TIME_AGENT_LOG_LEVEL=DEBUG
```

Or in code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Getting Help

If you encounter issues:

1. Check the [troubleshooting section](#troubleshooting)
2. Review the [examples](../src/real_time_agent/examples/)
3. Check [GitHub Issues](https://github.com/PerfectThymeTech/real-time-agent/issues)
4. Create a new issue with:
   - Your configuration (without API keys)
   - Error messages
   - Python version and OS
   - Steps to reproduce

## Production Deployment

For production deployments, consider:

### Security
- Use managed identity instead of API keys
- Store secrets in Azure Key Vault
- Enable audit logging
- Implement rate limiting

### Monitoring
- Set up Application Insights
- Configure health checks
- Monitor token usage and costs
- Set up alerts for errors

### Scaling
- Use Azure Container Instances or AKS
- Implement auto-scaling based on load
- Use Azure Load Balancer for high availability
- Consider Azure Functions for serverless deployment

### Sample Production Configuration

```yaml
# Azure Container Instance or Kubernetes deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: real-time-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: real-time-agent
  template:
    metadata:
      labels:
        app: real-time-agent
    spec:
      containers:
      - name: agent
        image: your-registry/real-time-agent:latest
        env:
        - name: AZURE_OPENAI_ENDPOINT
          value: "https://your-resource.openai.azure.com/"
        - name: AZURE_OPENAI_DEPLOYMENT
          value: "gpt-4"
        - name: REAL_TIME_AGENT_LOG_LEVEL
          value: "INFO"
        # Use managed identity - no API key needed
```

## Next Steps

After successful setup:

1. **Explore Examples**: Run all example scripts to understand different patterns
2. **Customize Configuration**: Adjust settings for your specific use case
3. **Integration**: Integrate the agent into your application
4. **Monitoring**: Set up proper logging and monitoring
5. **Testing**: Implement tests for your specific use cases

For detailed usage patterns, see the [Examples Documentation](../examples/).