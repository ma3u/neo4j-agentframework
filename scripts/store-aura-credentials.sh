#!/bin/bash
# Store Neo4j Aura API credentials in Azure Key Vault
# Instance: c748b32e (westeurope, 2GB RAM)

set -e

echo "🔐 Storing Neo4j Aura Credentials in Azure Key Vault"
echo "=" * 50

# Configuration
RESOURCE_GROUP="rg-neo4j-rag-bitnet"
LOCATION="westeurope"  # Same as Aura instance
KEY_VAULT_NAME="kv-neo4j-rag-${RANDOM}"
AURA_INSTANCE_ID="c748b32e"

# Aura API Credentials (prompt user for security)
echo "🔑 Please enter your Aura API Client ID"
read -p "Client ID: " AURA_CLIENT_ID

echo "🔑 Please enter your Aura API Client Secret"
read -s -p "Client Secret: " AURA_CLIENT_SECRET
echo

# Aura Database Connection
AURA_URI="neo4j+s://${AURA_INSTANCE_ID}.databases.neo4j.io"
AURA_USERNAME="neo4j"

echo "Configuration:"
echo "  Resource Group: $RESOURCE_GROUP"
echo "  Location: $LOCATION"
echo "  Key Vault: $KEY_VAULT_NAME"
echo "  Aura Instance: $AURA_INSTANCE_ID"
echo "  Aura URI: $AURA_URI"
echo

# Step 1: Create Resource Group (if it doesn't exist)
echo "📦 Creating resource group..."
az group create \
    --name "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --output none || echo "Resource group already exists"
echo "✅ Resource group ready"

# Step 2: Create Key Vault
echo "🔑 Creating Key Vault..."
az keyvault create \
    --name "$KEY_VAULT_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --enable-rbac-authorization false \
    --output none
echo "✅ Key Vault created: $KEY_VAULT_NAME"

# Step 3: Store Aura Database Connection (for RAG service)
echo "💾 Storing Aura database connection..."

az keyvault secret set \
    --vault-name "$KEY_VAULT_NAME" \
    --name "neo4j-aura-uri" \
    --value "$AURA_URI" \
    --output none
echo "✅ Stored: neo4j-aura-uri"

az keyvault secret set \
    --vault-name "$KEY_VAULT_NAME" \
    --name "neo4j-aura-username" \
    --value "$AURA_USERNAME" \
    --output none
echo "✅ Stored: neo4j-aura-username"

# You need to provide the database password
echo
echo "🔑 Please enter your Neo4j Aura DATABASE password"
echo "   (Found in Aura console when you created instance $AURA_INSTANCE_ID)"
read -s -p "Database Password: " AURA_DB_PASSWORD
echo

if [ -z "$AURA_DB_PASSWORD" ]; then
    echo "❌ Error: Password cannot be empty"
    exit 1
fi

az keyvault secret set \
    --vault-name "$KEY_VAULT_NAME" \
    --name "neo4j-aura-password" \
    --value "$AURA_DB_PASSWORD" \
    --output none
echo "✅ Stored: neo4j-aura-password"

# Step 4: Store Aura API Credentials (for instance management)
echo "💾 Storing Aura API credentials..."

az keyvault secret set \
    --vault-name "$KEY_VAULT_NAME" \
    --name "aura-api-client-id" \
    --value "$AURA_CLIENT_ID" \
    --output none
echo "✅ Stored: aura-api-client-id"

az keyvault secret set \
    --vault-name "$KEY_VAULT_NAME" \
    --name "aura-api-client-secret" \
    --value "$AURA_CLIENT_SECRET" \
    --output none
echo "✅ Stored: aura-api-client-secret"

# Step 5: Set access policy for current user
echo "🔐 Setting access policy..."
CURRENT_USER=$(az account show --query user.name -o tsv)
az keyvault set-policy \
    --name "$KEY_VAULT_NAME" \
    --upn "$CURRENT_USER" \
    --secret-permissions get list set delete \
    --output none
echo "✅ Access granted to: $CURRENT_USER"

# Summary
echo
echo "=" * 50
echo "🎉 Credentials Stored Successfully!"
echo "=" * 50
echo
echo "Key Vault: $KEY_VAULT_NAME"
echo "Region: $LOCATION"
echo
echo "Stored Secrets:"
echo "  Database Connection:"
echo "    • neo4j-aura-uri: $AURA_URI"
echo "    • neo4j-aura-username: $AURA_USERNAME"
echo "    • neo4j-aura-password: ***"
echo
echo "  Aura API (for instance management):"
echo "    • aura-api-client-id: $AURA_CLIENT_ID"
echo "    • aura-api-client-secret: ***"
echo
echo "Next Steps:"
echo "  1. Update neo4j-rag-demo/.env with:"
echo "     AZURE_KEY_VAULT_NAME=$KEY_VAULT_NAME"
echo
echo "  2. Test connection:"
echo "     python test_aura_connection.py"
echo
echo "  3. Deploy RAG service to Azure Container Apps"
echo "     ./scripts/azure-deploy-enterprise.sh"
echo
