#!/bin/bash
# Setup Managed Identity for Azure Container Apps to access Key Vault
# This script enables system-assigned Managed Identity and grants Key Vault access

set -e

echo "🔑 Setting up Managed Identity for Container Apps"
echo "=================================================="
echo ""

# Configuration
RESOURCE_GROUP="rg-neo4j-rag-bitnet"
KEY_VAULT_NAME="kv-neo4j-rag-prod"
CONTAINER_APP_NAME="neo4j-rag-service"  # Update if your app has a different name

echo "📋 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Key Vault: $KEY_VAULT_NAME"
echo "  Container App: $CONTAINER_APP_NAME"
echo ""

# Check if logged in to Azure
echo "🔍 Checking Azure CLI authentication..."
if ! az account show &>/dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

SUBSCRIPTION=$(az account show --query name -o tsv)
echo "✅ Logged in to Azure"
echo "  Subscription: $SUBSCRIPTION"
echo ""

# Check if Container App exists
echo "🔍 Checking if Container App exists..."
if ! az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "⚠️  Container App '$CONTAINER_APP_NAME' not found."
    echo ""
    echo "Available Container Apps:"
    az containerapp list --resource-group $RESOURCE_GROUP --query "[].name" -o table
    echo ""
    read -p "Enter the correct Container App name: " CONTAINER_APP_NAME
    
    if ! az containerapp show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP &>/dev/null; then
        echo "❌ Container App still not found. Please create it first."
        exit 1
    fi
fi
echo "✅ Container App found: $CONTAINER_APP_NAME"
echo ""

# Enable system-assigned Managed Identity
echo "🔐 Enabling System-Assigned Managed Identity..."
az containerapp identity assign \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --system-assigned \
    --output table

echo "✅ Managed Identity enabled"
echo ""

# Get the Managed Identity Principal ID
echo "🔍 Retrieving Managed Identity Principal ID..."
PRINCIPAL_ID=$(az containerapp identity show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query principalId -o tsv)

if [ -z "$PRINCIPAL_ID" ]; then
    echo "❌ Failed to retrieve Principal ID"
    exit 1
fi

echo "✅ Principal ID: $PRINCIPAL_ID"
echo ""

# Grant Key Vault access to Managed Identity
echo "🔑 Granting Key Vault access to Managed Identity..."
az keyvault set-policy \
    --name $KEY_VAULT_NAME \
    --object-id $PRINCIPAL_ID \
    --secret-permissions get list \
    --output table

echo "✅ Key Vault access granted"
echo ""

# Set environment variable for Key Vault name
echo "📝 Setting AZURE_KEY_VAULT_NAME environment variable..."
az containerapp update \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --set-env-vars "AZURE_KEY_VAULT_NAME=$KEY_VAULT_NAME" \
    --output table

echo "✅ Environment variable set"
echo ""

# Verify the configuration
echo "✅ Verifying configuration..."
echo ""
echo "Managed Identity Details:"
az containerapp identity show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --output table

echo ""
echo "Environment Variables:"
az containerapp show \
    --name $CONTAINER_APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query "properties.template.containers[0].env[].[name,value]" \
    -o table | grep -i "AZURE"

echo ""
echo "=================================================="
echo "✅ Managed Identity Setup Complete!"
echo "=================================================="
echo ""
echo "📋 Summary:"
echo "  Container App: $CONTAINER_APP_NAME"
echo "  Principal ID: $PRINCIPAL_ID"
echo "  Key Vault: $KEY_VAULT_NAME"
echo "  Permissions: Get, List secrets"
echo ""
echo "🔐 The Container App can now:"
echo "  ✓ Authenticate to Azure without credentials"
echo "  ✓ Access secrets from Key Vault"
echo "  ✓ Connect to Neo4j Aura securely"
echo ""
echo "📝 Next Steps:"
echo "  1. Deploy your updated application code"
echo "  2. Test the connection: run test-aura-connection.sh"
echo "  3. Monitor logs: az containerapp logs show --name $CONTAINER_APP_NAME --resource-group $RESOURCE_GROUP --follow"
echo ""
echo "🚀 Your app is now using Managed Identity + Key Vault!"
