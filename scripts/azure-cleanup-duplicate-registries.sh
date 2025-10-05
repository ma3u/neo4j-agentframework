#!/bin/bash
# Azure Resource Cleanup Script - Remove Duplicate Container Registries
# This script safely removes duplicate Container Registries while keeping the one in use

set -e

RESOURCE_GROUP="rg-neo4j-rag-bitnet"

echo "🔍 Azure Resource Cleanup - Duplicate Container Registries"
echo "=========================================================="
echo ""

# Check if logged in
if ! az account show &>/dev/null; then
    echo "❌ Not logged into Azure. Please run: az login"
    exit 1
fi

echo "📋 Current Container Registries in $RESOURCE_GROUP:"
echo ""

# List all container registries
REGISTRIES=$(az acr list --resource-group $RESOURCE_GROUP --query "[].name" -o tsv)

if [ -z "$REGISTRIES" ]; then
    echo "✅ No container registries found."
    exit 0
fi

# Count registries
REGISTRY_COUNT=$(echo "$REGISTRIES" | wc -l | tr -d ' ')
echo "Found $REGISTRY_COUNT container registries:"
echo ""

# List with details
az acr list --resource-group $RESOURCE_GROUP \
    --query "[].{Name:name, SKU:sku.name, CreatedDate:creationDate, UsageGB:usage.value}" \
    --output table

echo ""
echo "=========================================================="
echo ""

# Find which registry is actively used by Container Apps
echo "🔍 Checking which registry is used by Container Apps..."
echo ""

ACTIVE_REGISTRY=$(az containerapp list --resource-group $RESOURCE_GROUP \
    --query "[0].properties.template.containers[0].image" -o tsv | cut -d'/' -f1 2>/dev/null)

if [ -n "$ACTIVE_REGISTRY" ]; then
    echo "✅ Active registry (in use by Container Apps): $ACTIVE_REGISTRY"
    echo ""
else
    echo "⚠️  No Container Apps found using registries"
    echo "   Recommend keeping the NEWEST registry"
    echo ""

    # Find newest registry
    ACTIVE_REGISTRY=$(az acr list --resource-group $RESOURCE_GROUP \
        --query "sort_by(@, &creationDate)[-1].name" -o tsv)
    echo "📅 Newest registry: $ACTIVE_REGISTRY (recommended to keep)"
    echo ""
fi

# Identify registries to delete
echo "🗑️  Registries that can be safely deleted:"
echo ""

REGISTRIES_TO_DELETE=()
for registry in $REGISTRIES; do
    if [ "$registry" != "$ACTIVE_REGISTRY" ]; then
        echo "   ❌ $registry (not in use)"
        REGISTRIES_TO_DELETE+=("$registry")
    else
        echo "   ✅ $registry (KEEP - currently in use)"
    fi
done

echo ""
echo "=========================================================="
echo ""

# Ask for confirmation
if [ ${#REGISTRIES_TO_DELETE[@]} -eq 0 ]; then
    echo "✅ No duplicate registries to delete. You're all set!"
    exit 0
fi

echo "⚠️  WARNING: This will delete ${#REGISTRIES_TO_DELETE[@]} container registries!"
echo ""
echo "Registries to DELETE:"
for registry in "${REGISTRIES_TO_DELETE[@]}"; do
    echo "   - $registry"
done
echo ""
echo "Registry to KEEP:"
echo "   - $ACTIVE_REGISTRY"
echo ""

read -p "Continue with deletion? (yes/no): " CONFIRM

if [ "$CONFIRM" != "yes" ]; then
    echo "❌ Cleanup cancelled. No changes made."
    exit 0
fi

echo ""
echo "🗑️  Deleting duplicate registries..."
echo ""

# Delete each duplicate registry
for registry in "${REGISTRIES_TO_DELETE[@]}"; do
    echo "Deleting $registry..."
    az acr delete --name "$registry" --resource-group $RESOURCE_GROUP --yes
    echo "   ✅ Deleted $registry"
done

echo ""
echo "=========================================================="
echo "✅ Cleanup Complete!"
echo ""
echo "Summary:"
echo "   Deleted: ${#REGISTRIES_TO_DELETE[@]} registries"
echo "   Kept: $ACTIVE_REGISTRY"
echo "   Monthly savings: \$$(( ${#REGISTRIES_TO_DELETE[@]} * 5 ))"
echo ""
echo "Current resources:"
az acr list --resource-group $RESOURCE_GROUP --query "[].{Name:name, SKU:sku.name}" --output table
echo ""
echo "=========================================================="
