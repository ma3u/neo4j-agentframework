#!/usr/bin/env python3
"""Test connection to new Aura instance 6b870b04"""

import sys
sys.path.insert(0, '/Users/ma3u/projects/ms-agentf-neo4j/neo4j-rag-demo')

from neo4j import GraphDatabase

import os
from dotenv import load_dotenv

load_dotenv('/Users/ma3u/projects/ms-agentf-neo4j/neo4j-rag-demo/.env')

uri = os.getenv('NEO4J_URI')
username = os.getenv('NEO4J_USERNAME')
password = os.getenv('NEO4J_PASSWORD')

print('🔍 Testing Neo4j Aura Connection')
print('=' * 50)
print(f'Instance: 6b870b04 (ma3u - new free instance)')
print(f'URI: {uri}')
print(f'Username: {username}')
print(f'Password: {"*" * len(password)}')
print()

try:
    print('🔌 Connecting to Aura instance...')
    driver = GraphDatabase.driver(uri, auth=(username, password))

    with driver.session() as session:
        # Test connection
        result = session.run('RETURN "Connection successful!" as message')
        record = result.single()
        print(f'✅ {record["message"]}')

        # Get database info
        result = session.run('''
            CALL dbms.components() YIELD name, versions, edition
            RETURN name, versions[0] as version, edition
        ''')
        for record in result:
            print(f'   Database: {record["name"]} {record["version"]} ({record["edition"]})')

        # Check for existing data
        result = session.run('MATCH (n) RETURN count(n) as node_count')
        count = result.single()['node_count']
        print(f'   Nodes: {count}')

        # Check for indexes
        result = session.run('SHOW INDEXES')
        indexes = list(result)
        print(f'   Indexes: {len(indexes)}')

    driver.close()
    print()
    print('=' * 50)
    print('🎉 SUCCESS! Your Aura instance is ready for RAG!')
    print('=' * 50)
    print()
    print('Credentials stored in:')
    print('  • neo4j-rag-demo/.env')
    print('  • Azure Key Vault: kv-neo4j-rag-7048')
    print()
    print('Next steps:')
    print('  1. Update RAG service to use new instance')
    print('  2. Deploy to Azure Container Apps')
    print('  3. Configure Azure AI Foundry Assistant')

except Exception as e:
    print(f'❌ Connection failed: {e}')
    print()
    print('Please check:')
    print('  1. Instance is fully initialized (wait 1-2 min)')
    print('  2. Password copied correctly')
    print('  3. No firewall blocking your IP')
