#!/usr/bin/env python3
"""
Test Neo4j Aura Connection
Tests connectivity to your Aura instance: c748b32e
"""

import os
import sys
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load environment variables
load_dotenv("neo4j-rag-demo/.env")

def test_aura_connection():
    """Test connection to Neo4j Aura instance"""

    uri = os.getenv("NEO4J_URI")
    username = os.getenv("NEO4J_USERNAME", "neo4j")
    password = os.getenv("NEO4J_PASSWORD")

    print("🔍 Testing Neo4j Aura Connection")
    print("=" * 50)
    print(f"URI: {uri}")
    print(f"Username: {username}")
    print(f"Password: {'*' * len(password) if password else 'NOT SET'}")
    print()

    if not password or password == "your_aura_password_here":
        print("❌ Error: NEO4J_PASSWORD not configured")
        print()
        print("Please update neo4j-rag-demo/.env with your Aura password")
        print("You can find it in Neo4j Aura console after creating the instance")
        return False

    try:
        print("🔌 Connecting to Aura instance c748b32e...")
        driver = GraphDatabase.driver(uri, auth=(username, password))

        # Test connection
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful!' as message")
            record = result.single()
            print(f"✅ {record['message']}")

            # Get database info
            result = session.run("""
                CALL dbms.components() YIELD name, versions, edition
                RETURN name, versions[0] as version, edition
            """)
            for record in result:
                print(f"   Database: {record['name']} {record['version']} ({record['edition']})")

            # Check for existing data
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            count = result.single()['node_count']
            print(f"   Nodes: {count}")

        driver.close()
        print()
        print("🎉 Your Aura instance is ready for RAG!")
        return True

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print()
        print("Troubleshooting:")
        print("1. Verify password in neo4j-rag-demo/.env")
        print("2. Check instance is RUNNING in Aura console")
        print("3. Verify firewall rules allow your IP")
        return False

if __name__ == "__main__":
    success = test_aura_connection()
    sys.exit(0 if success else 1)
