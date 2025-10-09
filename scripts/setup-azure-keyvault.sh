#!/bin/bash
# Setup Azure Key Vault for Neo4j Aura Credentials
# This script creates a Key Vault and stores the Aura instance credentials securely

set -e

echo "🔐 Setting up Azure Key Vault for Neo4j Aura Integration"
echo "=========================================================="
echo ""

# Configuration
RESOURCE_GROUP="rg-neo4j-rag-bitnet"
LOCATION="uksouth"  # Same region as Aura instance 812bc7bd
KEY_VAULT_NAME="kv-neo4j-rag-prod"
AURA_INSTANCE_ID="812bc7bd"
AURA_URI="neo4j+s://${AURA_INSTANCE_ID}.databases.neo4j.io"

echo "📋 Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Key Vault Name: $KEY_VAULT_NAME"
echo "  Aura Instance: $AURA_INSTANCE_ID"
echo "  Aura URI: $AURA_URI"
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

# Check if resource group exists
echo "🔍 Checking if resource group exists..."
if ! az group show --name $RESOURCE_GROUP &>/dev/null; then
    echo "📦 Creating resource group: $RESOURCE_GROUP"
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION \
        --output table
    echo "✅ Resource group created"
else
    echo "✅ Resource group already exists"
fi
echo ""

# Create Key Vault
echo "🔐 Creating Azure Key Vault: $KEY_VAULT_NAME"
if az keyvault show --name $KEY_VAULT_NAME --resource-group $RESOURCE_GROUP &>/dev/null; then
    echo "⚠️  Key Vault already exists. Using existing vault."
else
    az keyvault create \
        --name $KEY_VAULT_NAME \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --enable-rbac-authorization false \
        --output table
    echo "✅ Key Vault created"
fi
echo ""

# Store Neo4j Aura URI
echo "💾 Storing Aura connection URI..."
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "neo4j-aura-uri" \
    --value "$AURA_URI" \
    --output none
echo "✅ Stored: neo4j-aura-uri"

# Store Neo4j username
echo "💾 Storing Aura username..."
az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "neo4j-aura-username" \
    --value "neo4j" \
    --output none
echo "✅ Stored: neo4j-aura-username"

# Store Neo4j password (prompt user)
echo ""
echo "🔑 Please enter your Neo4j Aura password for instance $AURA_INSTANCE_ID"
echo "   (You can find this in Neo4j Aura console)"
read -s -p "Password: " AURA_PASSWORD
echo ""

if [ -z "$AURA_PASSWORD" ]; then
    echo "❌ Password cannot be empty"
    exit 1
fi

az keyvault secret set \
    --vault-name $KEY_VAULT_NAME \
    --name "neo4j-aura-password" \
    --value "$AURA_PASSWORD" \
    --output none
echo "✅ Stored: neo4j-aura-password"
echo ""

# Grant current user access (for local development)
echo "🔑 Granting your user account access to Key Vault..."
CURRENT_USER=$(az ad signed-in-user show --query id -o tsv)
az keyvault set-policy \
    --name $KEY_VAULT_NAME \
    --object-id $CURRENT_USER \
    --secret-permissions get list \
    --output none
echo "✅ Access granted for local development"
echo ""

# Verify secrets
echo "✅ Verifying stored secrets..."
SECRETS=$(az keyvault secret list --vault-name $KEY_VAULT_NAME --query "[].name" -o tsv)
echo "  Secrets in vault:"
for secret in $SECRETS; do
    echo "    - $secret"
done
echo ""

# Display summary
echo "=========================================================="
echo "✅ Azure Key Vault Setup Complete!"
echo "=========================================================="
echo ""
echo "📋 Summary:"
echo "  Key Vault: $KEY_VAULT_NAME"
echo "  Vault URL: https://${KEY_VAULT_NAME}.vault.azure.net"
echo "  Location: $LOCATION"
echo "  Secrets stored: 3 (uri, username, password)"
echo ""
echo "🔐 Stored Credentials for Aura Instance: $AURA_INSTANCE_ID"
echo "  URI: $AURA_URI"
echo "  Username: neo4j"
echo "  Password: ******** (securely stored)"
echo ""
echo "📝 Next Steps:"
echo "  1. Run: export AZURE_KEY_VAULT_NAME=$KEY_VAULT_NAME"
echo "  2. Test local connection with test script"
echo "  3. Setup Managed Identity for Container Apps"
echo ""
echo "🚀 Ready to use with AuraConfig class!"
