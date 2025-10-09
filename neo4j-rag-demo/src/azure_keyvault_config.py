"""
Azure Key Vault Configuration for Neo4j Aura
Provides secure credential management using Azure Managed Identity

This module handles:
- Secure retrieval of Neo4j Aura credentials from Azure Key Vault
- Automatic authentication using Managed Identity (no credentials needed!)
- Fallback to local environment variables for development
- Caching of credentials to minimize Key Vault calls
"""

import os
import logging
from typing import Dict, Optional
from dataclasses import dataclass

try:
    from azure.identity import DefaultAzureCredential
    from azure.keyvault.secrets import SecretClient
    from azure.core.exceptions import AzureError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False
    logging.warning(
        "Azure SDK not available. Install with: pip install azure-identity azure-keyvault-secrets"
    )

logger = logging.getLogger(__name__)


@dataclass
class Neo4jCredentials:
    """Neo4j connection credentials"""
    uri: str
    username: str
    password: str


class AuraConfig:
    """
    Secure configuration for Neo4j Aura using Azure Key Vault and Managed Identity
    
    Usage:
        # In Azure (production) - uses Managed Identity automatically
        config = AuraConfig()
        creds = config.get_neo4j_credentials()
        
        # Local development - uses environment variables or Azure CLI
        config = AuraConfig()  # Falls back to local env vars
        creds = config.get_neo4j_credentials()
    
    Environment Variables:
        AZURE_KEY_VAULT_NAME: Name of the Azure Key Vault (required for production)
        NEO4J_URI: Local development Neo4j URI (fallback)
        NEO4J_USERNAME: Local development username (fallback)
        NEO4J_PASSWORD: Local development password (fallback)
    """
    
    def __init__(
        self, 
        key_vault_name: Optional[str] = None,
        use_cache: bool = True
    ):
        """
        Initialize AuraConfig
        
        Args:
            key_vault_name: Azure Key Vault name (defaults to AZURE_KEY_VAULT_NAME env var)
            use_cache: Cache credentials to minimize Key Vault API calls (default: True)
        """
        self.key_vault_name = key_vault_name or os.getenv("AZURE_KEY_VAULT_NAME")
        self.use_cache = use_cache
        self._cached_credentials: Optional[Neo4jCredentials] = None
        self._secret_client: Optional[SecretClient] = None
        
        # Initialize Azure Key Vault client if available
        if self.key_vault_name and AZURE_AVAILABLE:
            try:
                self._initialize_keyvault_client()
            except Exception as e:
                logger.warning(
                    f"Failed to initialize Key Vault client: {e}. "
                    "Falling back to environment variables."
                )
        elif self.key_vault_name and not AZURE_AVAILABLE:
            logger.warning(
                "Key Vault name provided but Azure SDK not installed. "
                "Install with: pip install azure-identity azure-keyvault-secrets"
            )
    
    def _initialize_keyvault_client(self):
        """Initialize Azure Key Vault client with Managed Identity"""
        logger.info(f"Initializing Key Vault client for: {self.key_vault_name}")
        
        # DefaultAzureCredential automatically handles:
        # 1. Managed Identity (in Azure Container Apps)
        # 2. Azure CLI credentials (local development)
        # 3. Visual Studio Code credentials
        # 4. Environment variables (AZURE_CLIENT_ID, etc.)
        credential = DefaultAzureCredential()
        
        vault_url = f"https://{self.key_vault_name}.vault.azure.net"
        self._secret_client = SecretClient(
            vault_url=vault_url,
            credential=credential
        )
        
        logger.info(f"✅ Key Vault client initialized: {vault_url}")
    
    def get_neo4j_credentials(self) -> Neo4jCredentials:
        """
        Get Neo4j Aura credentials securely
        
        Returns:
            Neo4jCredentials with uri, username, and password
        
        Raises:
            ValueError: If credentials cannot be retrieved
        """
        # Return cached credentials if available
        if self.use_cache and self._cached_credentials:
            logger.debug("Using cached credentials")
            return self._cached_credentials
        
        # Try to get from Azure Key Vault first
        if self._secret_client:
            try:
                credentials = self._get_credentials_from_keyvault()
                if self.use_cache:
                    self._cached_credentials = credentials
                return credentials
            except Exception as e:
                logger.error(f"Failed to get credentials from Key Vault: {e}")
                logger.info("Falling back to environment variables")
        
        # Fallback to environment variables (local development)
        credentials = self._get_credentials_from_env()
        if self.use_cache:
            self._cached_credentials = credentials
        return credentials
    
    def _get_credentials_from_keyvault(self) -> Neo4jCredentials:
        """Retrieve credentials from Azure Key Vault"""
        logger.info("Fetching credentials from Azure Key Vault...")
        
        try:
            uri = self._secret_client.get_secret("neo4j-aura-uri").value
            username = self._secret_client.get_secret("neo4j-aura-username").value
            password = self._secret_client.get_secret("neo4j-aura-password").value
            
            logger.info("✅ Successfully retrieved credentials from Key Vault")
            logger.debug(f"URI: {uri}")
            
            return Neo4jCredentials(
                uri=uri,
                username=username,
                password=password
            )
        except AzureError as e:
            logger.error(f"Azure Key Vault error: {e}")
            raise ValueError(f"Failed to retrieve credentials from Key Vault: {e}")
    
    def _get_credentials_from_env(self) -> Neo4jCredentials:
        """Retrieve credentials from environment variables (fallback)"""
        logger.info("Using credentials from environment variables")
        
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME", "neo4j")
        password = os.getenv("NEO4J_PASSWORD")
        
        if not uri:
            uri = "bolt://localhost:7687"
            logger.warning(
                f"NEO4J_URI not set, using default: {uri}"
            )
        
        if not password:
            password = "password"
            logger.warning(
                "NEO4J_PASSWORD not set, using default: 'password'"
            )
        
        return Neo4jCredentials(
            uri=uri,
            username=username,
            password=password
        )
    
    def test_connection(self) -> bool:
        """
        Test if credentials can be retrieved successfully
        
        Returns:
            True if credentials can be retrieved, False otherwise
        """
        try:
            creds = self.get_neo4j_credentials()
            logger.info(f"✅ Credentials retrieved successfully")
            logger.info(f"   URI: {creds.uri}")
            logger.info(f"   Username: {creds.username}")
            logger.info(f"   Password: {'*' * len(creds.password)}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to retrieve credentials: {e}")
            return False
    
    def clear_cache(self):
        """Clear cached credentials (force refresh on next get)"""
        self._cached_credentials = None
        logger.debug("Credential cache cleared")
    
    def get_credentials_dict(self) -> Dict[str, str]:
        """
        Get credentials as dictionary (for backward compatibility)
        
        Returns:
            Dict with 'uri', 'username', 'password' keys
        """
        creds = self.get_neo4j_credentials()
        return {
            "uri": creds.uri,
            "username": creds.username,
            "password": creds.password
        }


# Convenience function for quick setup
def get_aura_credentials() -> Dict[str, str]:
    """
    Quick helper to get Neo4j Aura credentials
    
    Returns:
        Dict with 'uri', 'username', 'password' keys
    
    Example:
        from azure_keyvault_config import get_aura_credentials
        
        creds = get_aura_credentials()
        driver = GraphDatabase.driver(
            creds['uri'],
            auth=(creds['username'], creds['password'])
        )
    """
    config = AuraConfig()
    return config.get_credentials_dict()


if __name__ == "__main__":
    # Test the configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("🔐 Testing Azure Key Vault Configuration")
    print("=" * 50)
    
    config = AuraConfig()
    success = config.test_connection()
    
    if success:
        print("\n✅ Configuration test passed!")
    else:
        print("\n❌ Configuration test failed!")
        print("\nTroubleshooting:")
        print("1. Make sure AZURE_KEY_VAULT_NAME is set")
        print("2. Run: az login (for local development)")
        print("3. Or set NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD")
