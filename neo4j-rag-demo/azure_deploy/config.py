"""
Azure configuration for Neo4j RAG deployment
"""

import os
from pydantic import BaseSettings
from typing import Optional


class AzureConfig(BaseSettings):
    """Azure deployment configuration"""

    # Azure Resource Configuration
    subscription_id: str = os.getenv("AZURE_SUBSCRIPTION_ID", "")
    resource_group: str = os.getenv("AZURE_RESOURCE_GROUP", "rg-neo4j-rag-agent")
    location: str = os.getenv("AZURE_LOCATION", "eastus")

    # Azure AI Services
    ai_services_endpoint: str = os.getenv("AZURE_AI_SERVICES_ENDPOINT", "")
    ai_services_key: str = os.getenv("AZURE_AI_SERVICES_KEY", "")
    openai_deployment_name: str = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")

    # Azure Container Apps
    container_app_name: str = os.getenv("CONTAINER_APP_NAME", "neo4j-rag-agent")
    container_registry: str = os.getenv("CONTAINER_REGISTRY", "")

    # Neo4j Configuration
    neo4j_uri: str = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user: str = os.getenv("NEO4J_USER", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "password")

    # Application Configuration
    app_name: str = "Neo4j RAG Agent"
    app_version: str = "1.0.0"
    api_prefix: str = "/api/v1"

    # Monitoring
    app_insights_connection_string: str = os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING", "")
    enable_telemetry: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global config instance
config = AzureConfig()