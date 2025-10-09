# Azure Key Vault Setup for Neo4j Aura Integration

Complete guide for setting up secure credential management using Azure Key Vault and Managed Identity for Neo4j Aura connection.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Architecture](#architecture)
4. [Setup Steps](#setup-steps)
5. [Local Development](#local-development)
6. [Azure Deployment](#azure-deployment)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

## Overview

This setup provides **zero-credential deployment** for Neo4j Aura integration using:

- ✅ **Azure Key Vault** - Centralized secret management
- ✅ **Managed Identity** - No credentials in code or config
- ✅ **Auto-rotation** - Azure handles token lifecycle
- ✅ **Audit logging** - Full trail of secret access
- ✅ **RBAC** - Fine-grained access control

### Security Benefits

| Feature | Without Key Vault | With Managed Identity + Key Vault |
|---------|-------------------|-----------------------------------|
| Credentials in code | ❌ Yes | ✅ No |
| Manual rotation | ❌ Yes | ✅ Auto (tokens) |
| Audit trail | ⚠️ Limited | ✅ Full |
| Secret leakage risk | ❌ High | ✅ Minimal |
| Compliance ready | ⚠️ Basic | ✅ Advanced |

## Prerequisites

### Required Tools

```bash
# Azure CLI
az --version  # Should be 2.50.0+

# Azure subscription
az login
az account show

# GitHub CLI (for issue tracking)
gh --version
```

### Required Access

- Azure subscription with Contributor role
- Ability to create resources in resource group
- Neo4j Aura instance (we're using: 812bc7bd)

### Neo4j Aura Instance Details

From your Aura console, note:
- **Instance ID**: `812bc7bd`
- **Connection URI**: `neo4j+s://812bc7bd.databases.neo4j.io`
- **Username**: `neo4j` (default)
- **Password**: (you set this during instance creation)

## Architecture

```
┌─────────────────────────────────────────────────┐
│   Azure Container Apps (RAG Service)             │
│   ┌───────────────────────────────────────┐     │
│   │  System-Assigned Managed Identity     │     │
│   │  (No credentials needed!)             │     │
│   └───────────────┬───────────────────────┘     │
│                   │ Authenticates                 │
└───────────────────┼───────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│   Azure Key Vault (kv-neo4j-rag-prod)            │
│   ┌───────────────────────────────────────┐     │
│   │  Secrets:                             │     │
│   │  • neo4j-aura-uri                     │     │
│   │  • neo4j-aura-username                │     │
│   │  • neo4j-aura-password                │     │
│   └───────────────────────────────────────┘     │
└─────────────────────┬───────────────────────────┘
                      │ Returns credentials
                      ↓
┌─────────────────────────────────────────────────┐
│   Neo4j Aura (812bc7bd)                          │
│   neo4j+s://812bc7bd.databases.neo4j.io         │
└─────────────────────────────────────────────────┘
```

## Setup Steps

### Step 1: Create Azure Key Vault and Store Credentials

Run the automated setup script:

```bash
cd scripts
chmod +x setup-azure-keyvault.sh
./setup-azure-keyvault.sh
```

**What this script does:**
1. Creates resource group (if not exists)
2. Creates Azure Key Vault `kv-neo4j-rag-prod`
3. Prompts for your Aura password
4. Stores 3 secrets:
   - `neo4j-aura-uri`
   - `neo4j-aura-username`
   - `neo4j-aura-password`
5. Grants your user account access (for local dev)

**Expected output:**
```
🔐 Setting up Azure Key Vault for Neo4j Aura Integration
==========================================================

✅ Key Vault Setup Complete!

Key Vault: kv-neo4j-rag-prod
Vault URL: https://kv-neo4j-rag-prod.vault.azure.net
Secrets stored: 3 (uri, username, password)
```

### Step 2: Install Python Dependencies

```bash
cd neo4j-rag-demo
pip install -r requirements.txt
```

This installs:
- `azure-identity>=1.17.1` - Managed Identity support
- `azure-keyvault-secrets>=4.8.0` - Key Vault client

### Step 3: Test Local Connection

```bash
# Set the Key Vault name
export AZURE_KEY_VAULT_NAME=kv-neo4j-rag-prod

# Test credential retrieval
cd neo4j-rag-demo/src
python azure_keyvault_config.py
```

**Expected output:**
```
🔐 Testing Azure Key Vault Configuration
==================================================
INFO - Initializing Key Vault client for: kv-neo4j-rag-prod
INFO - ✅ Key Vault client initialized: https://kv-neo4j-rag-prod.vault.azure.net
INFO - Fetching credentials from Azure Key Vault...
INFO - ✅ Successfully retrieved credentials from Key Vault
INFO - ✅ Credentials retrieved successfully
   URI: neo4j+s://812bc7bd.databases.neo4j.io
   Username: neo4j
   Password: ********

✅ Configuration test passed!
```

### Step 4: Test Neo4j RAG Connection

```bash
cd neo4j-rag-demo
export AZURE_KEY_VAULT_NAME=kv-neo4j-rag-prod
python scripts/test-aura-connection.sh
```

This verifies:
- Key Vault credential retrieval
- Neo4j Aura connection
- Vector search functionality

### Step 5: Setup Managed Identity for Container Apps

For Azure deployment, enable Managed Identity:

```bash
cd scripts
chmod +x setup-managed-identity.sh
./setup-managed-identity.sh
```

**What this script does:**
1. Enables system-assigned Managed Identity on Container App
2. Grants Managed Identity access to Key Vault
3. Sets `AZURE_KEY_VAULT_NAME` environment variable
4. Verifies configuration

**Expected output:**
```
🔑 Setting up Managed Identity for Container Apps
==================================================

✅ Managed Identity Setup Complete!

Container App: neo4j-rag-service
Principal ID: xxxxx-xxxx-xxxx-xxxx-xxxxxxxxx
Key Vault: kv-neo4j-rag-prod
Permissions: Get, List secrets

🔐 The Container App can now:
  ✓ Authenticate to Azure without credentials
  ✓ Access secrets from Key Vault
  ✓ Connect to Neo4j Aura securely
```

## Local Development

### Option 1: Using Azure CLI Credentials (Recommended)

```bash
# Login to Azure
az login

# Set Key Vault name
export AZURE_KEY_VAULT_NAME=kv-neo4j-rag-prod

# Run your application
cd neo4j-rag-demo
python src/your_app.py
```

The `DefaultAzureCredential` will automatically use your Azure CLI login.

### Option 2: Using Environment Variables (Fallback)

If you prefer not to use Key Vault locally:

```bash
# Create .env file
cat > neo4j-rag-demo/.env << EOF
NEO4J_URI=neo4j+s://812bc7bd.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
EOF

# Run your application
cd neo4j-rag-demo
python src/your_app.py
```

The code automatically falls back to environment variables if Key Vault is not configured.

## Azure Deployment

### Update Container App

After running `setup-managed-identity.sh`, deploy your updated code:

```bash
# Build and push container
cd neo4j-rag-demo
docker build -t your-registry.azurecr.io/neo4j-rag:latest .
docker push your-registry.azurecr.io/neo4j-rag:latest

# Update Container App
az containerapp update \
    --name neo4j-rag-service \
    --resource-group rg-neo4j-rag-bitnet \
    --image your-registry.azurecr.io/neo4j-rag:latest
```

### Verify Deployment

```bash
# Check logs
az containerapp logs show \
    --name neo4j-rag-service \
    --resource-group rg-neo4j-rag-bitnet \
    --follow

# Look for:
# "🔐 Using Azure Key Vault for credentials"
# "✅ Connected to: neo4j+s://812bc7bd.databases.neo4j.io"
```

## Testing

### Test Credential Retrieval

```bash
cd neo4j-rag-demo
export AZURE_KEY_VAULT_NAME=kv-neo4j-rag-prod

python -c "
from src.azure_keyvault_config import AuraConfig
config = AuraConfig()
creds = config.get_neo4j_credentials()
print(f'URI: {creds.uri}')
print(f'Username: {creds.username}')
print(f'Password: {\"*\" * len(creds.password)}')
"
```

### Test Neo4j Connection

```bash
cd neo4j-rag-demo
export AZURE_KEY_VAULT_NAME=kv-neo4j-rag-prod

python -c "
from src.neo4j_rag import Neo4jRAG

# This now uses Key Vault automatically!
rag = Neo4jRAG()
stats = rag.get_stats()
print(f'Connected! Documents: {stats[\"total_documents\"]}')
rag.close()
"
```

### Test RAG Query

```bash
cd neo4j-rag-demo
export AZURE_KEY_VAULT_NAME=kv-neo4j-rag-prod

python scripts/rag_demo.py
```

## Troubleshooting

### Issue: "Failed to initialize Key Vault client"

**Cause**: Not logged in to Azure or wrong Key Vault name

**Solution**:
```bash
az login
export AZURE_KEY_VAULT_NAME=kv-neo4j-rag-prod
```

### Issue: "Access denied" when accessing Key Vault

**Cause**: Your user or Managed Identity doesn't have permissions

**Solution for local dev**:
```bash
# Grant yourself access
az keyvault set-policy \
    --name kv-neo4j-rag-prod \
    --upn your-email@domain.com \
    --secret-permissions get list
```

**Solution for Container Apps**:
```bash
# Re-run Managed Identity setup
./scripts/setup-managed-identity.sh
```

### Issue: "Neo4j connection failed"

**Cause**: Wrong URI or password in Key Vault

**Solution**:
```bash
# Update password
az keyvault secret set \
    --vault-name kv-neo4j-rag-prod \
    --name neo4j-aura-password \
    --value "your_correct_password"

# Verify URI
az keyvault secret show \
    --vault-name kv-neo4j-rag-prod \
    --name neo4j-aura-uri \
    --query value -o tsv
```

### Issue: Code still using local credentials

**Cause**: Environment variables override Key Vault

**Solution**:
```bash
# Unset local env vars
unset NEO4J_URI
unset NEO4J_USERNAME
unset NEO4J_PASSWORD

# Set Key Vault name
export AZURE_KEY_VAULT_NAME=kv-neo4j-rag-prod
```

### Issue: "DefaultAzureCredential failed to retrieve token"

**Cause**: Multiple authentication methods conflicting

**Solution**:
```bash
# Clear Azure CLI cache
az account clear
az login

# Or use specific credential
export AZURE_CLIENT_ID=your-managed-identity-id
```

## Code Examples

### Basic Usage

```python
from src.neo4j_rag import Neo4jRAG

# Automatically uses Key Vault if AZURE_KEY_VAULT_NAME is set
rag = Neo4jRAG()

# Add document
rag.add_document("Your content here", metadata={"source": "test.pdf"})

# Search
results = rag.vector_search("your query", k=5)

# Clean up
rag.close()
```

### Explicit Key Vault Usage

```python
from src.neo4j_rag import Neo4jRAG

# Force Key Vault usage
rag = Neo4jRAG(use_azure_keyvault=True)

# Rest is the same
rag.close()
```

### Disable Key Vault (Local Dev)

```python
from src.neo4j_rag import Neo4jRAG

# Use direct credentials
rag = Neo4jRAG(
    uri="bolt://localhost:7687",
    username="neo4j",
    password="password",
    use_azure_keyvault=False
)

rag.close()
```

## Security Best Practices

### ✅ DO

- Use Managed Identity in production
- Rotate Aura password regularly
- Monitor Key Vault access logs
- Use separate Key Vaults for dev/prod
- Enable soft-delete on Key Vault
- Use Azure RBAC for Key Vault access

### ❌ DON'T

- Commit .env files with credentials
- Share Aura passwords via email/Slack
- Use same credentials across environments
- Disable Key Vault logging
- Grant broad Key Vault permissions

## Monitoring

### View Key Vault Access Logs

```bash
az monitor activity-log list \
    --resource-group rg-neo4j-rag-bitnet \
    --resource-type Microsoft.KeyVault/vaults \
    --max-events 50
```

### Monitor Container App Logs

```bash
az containerapp logs show \
    --name neo4j-rag-service \
    --resource-group rg-neo4j-rag-bitnet \
    --follow \
    | grep -i "key vault\|aura\|credentials"
```

## Related Documentation

- [Neo4j Aura Documentation](https://neo4j.com/docs/aura/)
- [Azure Key Vault Best Practices](https://docs.microsoft.com/azure/key-vault/general/best-practices)
- [Managed Identity Documentation](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/)
- [Issue #14: Neo4j Aura Integration](https://github.com/ma3u/neo4j-agentframework/issues/14)

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review logs in Azure Portal
3. Create issue in GitHub repository
4. Tag with `cloud`, `infrastructure`, `security`

---

**Last Updated**: October 9, 2025  
**Maintainer**: Neo4j Agent Framework Team  
**Status**: ✅ Production Ready
