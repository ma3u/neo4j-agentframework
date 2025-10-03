"""
Comprehensive Test Suite for Neo4j RAG + Microsoft Agent Framework Integration
Tests performance, functionality, and Azure deployment readiness
"""

import asyncio
import json
import os
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
import logging

# Import the modules we're testing
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.azure_agent.neo4j_rag_tools import Neo4jRAGTools, Neo4jRAGAgent
from src.neo4j_rag import Neo4jRAG, RAGQueryEngine

# Configure test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestNeo4jRAGTools(unittest.IsolatedAsyncioTestCase):
    """Test the Neo4j RAG tools for Agent Framework integration"""
    
    async def asyncSetUp(self):
        """Set up test fixtures"""
        # Mock the Neo4j RAG system to avoid requiring actual database
        self.mock_rag = MagicMock(spec=Neo4jRAG)
        self.mock_query_engine = MagicMock(spec=RAGQueryEngine)
        
        # Create tools instance with mocked dependencies
        self.tools = Neo4jRAGTools()
        self.tools.rag = self.mock_rag
        self.tools.query_engine = self.mock_query_engine
        
        # Set up mock return values
        self.mock_query_response = {
            'answer': 'Neo4j is a graph database that provides ACID transactions and high performance.',
            'sources': [
                {
                    'doc_id': 'test-doc-1',
                    'text': 'Neo4j is a graph database...',
                    'score': 0.95
                },
                {
                    'doc_id': 'test-doc-2', 
                    'text': 'Graph databases are optimized...',
                    'score': 0.87
                }
            ],
            'query_time': 0.123
        }
        
        self.mock_stats_response = {
            'documents': 100,
            'chunks': 5000,
            'avg_chunks_per_doc': 50.0
        }
    
    async def test_query_knowledge_graph_basic(self):
        """Test basic knowledge graph query functionality"""
        # Mock the query engine response
        self.mock_query_engine.query.return_value = self.mock_query_response
        
        # Test the tool
        result = await self.tools.query_knowledge_graph(
            "What is Neo4j?",
            max_results=3,
            include_metadata=True
        )
        
        # Verify the call was made
        self.mock_query_engine.query.assert_called_once_with("What is Neo4j?", k=3)
        
        # Verify response format
        self.assertIsInstance(result, str)
        self.assertIn("Neo4j is a graph database", result)
        self.assertIn("Performance Metrics", result)
        self.assertIn("417x faster", result)
        
        # Verify performance tracking
        self.assertEqual(self.tools._performance_stats['total_queries'], 1)
    
    async def test_query_knowledge_graph_performance_tracking(self):
        """Test that performance statistics are properly tracked"""
        self.mock_query_engine.query.return_value = self.mock_query_response
        
        # Run multiple queries
        for i in range(5):
            await self.tools.query_knowledge_graph(f"Test query {i}")
        
        # Verify performance tracking
        self.assertEqual(self.tools._performance_stats['total_queries'], 5)
        self.assertGreater(self.tools._performance_stats['avg_response_time'], 0)
    
    async def test_query_knowledge_graph_error_handling(self):
        """Test error handling in knowledge graph queries"""
        # Mock an exception
        self.mock_query_engine.query.side_effect = Exception("Database connection failed")
        
        result = await self.tools.query_knowledge_graph("Test query")
        
        # Verify error is handled gracefully
        self.assertIn("❌ Error querying knowledge graph", result)
        self.assertIn("Database connection failed", result)
    
    async def test_search_similar_content(self):
        """Test semantic similarity search functionality"""
        # Mock vector search response
        mock_vector_results = [
            {'text': 'Neo4j performance optimization', 'score': 0.92, 'doc_id': 'doc1'},
            {'text': 'Graph database indexing', 'score': 0.85, 'doc_id': 'doc2'},
            {'text': 'Vector search algorithms', 'score': 0.78, 'doc_id': 'doc3'}
        ]
        self.mock_rag.optimized_vector_search.return_value = mock_vector_results
        
        result = await self.tools.search_similar_content(
            "performance optimization",
            similarity_threshold=0.8,
            max_results=3
        )
        
        # Verify the call
        self.mock_rag.optimized_vector_search.assert_called_once_with(
            "performance optimization", k=3
        )
        
        # Verify response format
        self.assertIn("Semantic Search Results", result)
        self.assertIn("0.920", result)  # Similarity score
        self.assertIn("417x optimized", result)
    
    async def test_search_similar_content_threshold_filtering(self):
        """Test similarity threshold filtering"""
        mock_vector_results = [
            {'text': 'High similarity content', 'score': 0.95, 'doc_id': 'doc1'},
            {'text': 'Medium similarity content', 'score': 0.75, 'doc_id': 'doc2'},
            {'text': 'Low similarity content', 'score': 0.65, 'doc_id': 'doc3'}
        ]
        self.mock_rag.optimized_vector_search.return_value = mock_vector_results
        
        result = await self.tools.search_similar_content(
            "test query",
            similarity_threshold=0.8,
            max_results=5
        )
        
        # Should only include results with score >= 0.8
        self.assertIn("High similarity content", result)
        self.assertNotIn("Medium similarity content", result)
        self.assertNotIn("Low similarity content", result)
    
    async def test_get_system_statistics(self):
        """Test system statistics retrieval"""
        self.mock_rag.get_stats.return_value = self.mock_stats_response
        
        result = await self.tools.get_system_statistics()
        
        # Verify the call
        self.mock_rag.get_stats.assert_called_once()
        
        # Verify response content
        self.assertIn("Neo4j RAG System Statistics", result)
        self.assertIn("Documents: 100", result)
        self.assertIn("Text Chunks: 5,000", result)
        self.assertIn("417x faster", result)
        self.assertIn("System Optimization Status", result)
    
    async def test_parameter_validation(self):
        """Test input parameter validation"""
        self.mock_query_engine.query.return_value = self.mock_query_response
        
        # Test max_results validation
        result = await self.tools.query_knowledge_graph(
            "test", max_results=20  # Should be clamped to 10
        )
        
        # Verify max_results was clamped
        self.mock_query_engine.query.assert_called_with("test", k=10)
    
    async def test_performance_metrics_calculation(self):
        """Test that performance metrics are calculated correctly"""
        # Set up initial stats
        self.tools._performance_stats = {
            "total_queries": 4,
            "cache_hits": 2,
            "avg_response_time": 150.0
        }
        
        # Mock cache to simulate cache hit
        self.mock_rag._query_cache = {"test_key": "cached_result"}
        
        self.mock_query_engine.query.return_value = self.mock_query_response
        
        result = await self.tools.query_knowledge_graph("test query")
        
        # Verify stats were updated
        self.assertEqual(self.tools._performance_stats['total_queries'], 5)
        self.assertIn("Cache Hit Rate: 40.0%", result)


class TestNeo4jRAGAgent(unittest.IsolatedAsyncioTestCase):
    """Test the complete Agent Framework integration"""
    
    async def asyncSetUp(self):
        """Set up test fixtures for agent testing"""
        # Mock environment variables
        self.env_patcher = patch.dict(os.environ, {
            'AZURE_AI_PROJECT_ENDPOINT': 'https://test-project.services.ai.azure.com/api/projects/test',
            'AZURE_AI_MODEL_DEPLOYMENT_NAME': 'gpt-4o-mini',
            'NEO4J_URI': 'bolt://localhost:7687',
            'NEO4J_USER': 'neo4j',
            'NEO4J_PASSWORD': 'password'
        })
        self.env_patcher.start()
    
    async def asyncTearDown(self):
        """Clean up test fixtures"""
        self.env_patcher.stop()
    
    @patch('src.azure_agent.neo4j_rag_tools.AzureCliCredential')
    @patch('src.azure_agent.neo4j_rag_tools.AzureAIAgentClient')
    @patch('src.azure_agent.neo4j_rag_tools.ChatAgent')
    async def test_agent_initialization(self, mock_chat_agent, mock_client, mock_credential):
        """Test agent initialization process"""
        # Mock the credential and client
        mock_credential_instance = AsyncMock()
        mock_credential.return_value = mock_credential_instance
        
        mock_client_instance = MagicMock()
        mock_client.return_value = mock_client_instance
        
        mock_agent_instance = MagicMock()
        mock_chat_agent.return_value = mock_agent_instance
        
        # Create and initialize agent
        agent = Neo4jRAGAgent(
            project_endpoint="https://test.ai.azure.com/projects/test",
            model_deployment_name="gpt-4o-mini"
        )
        
        # Mock the Neo4j tools initialization
        agent.neo4j_tools = MagicMock()
        
        await agent.initialize()
        
        # Verify initialization calls
        mock_client.assert_called_once()
        mock_chat_agent.assert_called_once()
        
        # Verify agent configuration
        call_args = mock_chat_agent.call_args
        self.assertIn('chat_client', call_args.kwargs)
        self.assertIn('instructions', call_args.kwargs)
        self.assertIn('tools', call_args.kwargs)
        
        # Verify instructions mention performance optimization
        instructions = call_args.kwargs['instructions']
        self.assertIn('417x faster', instructions)
        self.assertIn('Neo4j', instructions)
    
    @patch('src.azure_agent.neo4j_rag_tools.Neo4jRAGTools')
    async def test_chat_functionality(self, mock_tools_class):
        """Test chat functionality with mocked components"""
        # Mock the tools
        mock_tools = AsyncMock()
        mock_tools_class.return_value = mock_tools
        
        # Mock agent
        mock_agent = AsyncMock()
        mock_run_result = MagicMock()
        mock_run_result.text = "This is a test response from the agent"
        mock_agent.run.return_value = mock_run_result
        
        agent = Neo4jRAGAgent()
        agent.agent = mock_agent
        agent.neo4j_tools = mock_tools
        
        # Test chat
        response = await agent.chat("What is Neo4j?")
        
        # Verify response
        self.assertEqual(response, "This is a test response from the agent")
        mock_agent.run.assert_called_once_with("What is Neo4j?")
    
    async def test_chat_error_handling(self):
        """Test error handling in chat functionality"""
        agent = Neo4jRAGAgent()
        
        # Mock agent that raises an exception
        mock_agent = AsyncMock()
        mock_agent.run.side_effect = Exception("Agent processing failed")
        agent.agent = mock_agent
        agent.neo4j_tools = MagicMock()
        
        response = await agent.chat("Test query")
        
        # Verify error is handled gracefully
        self.assertIn("I apologize, but I encountered an error", response)
        self.assertIn("Agent processing failed", response)


class TestPerformanceValidation(unittest.IsolatedAsyncioTestCase):
    """Test performance characteristics and optimization preservation"""
    
    async def test_response_time_tracking(self):
        """Test that response times are properly tracked"""
        tools = Neo4jRAGTools()
        
        # Mock the underlying components
        tools.rag = MagicMock()
        tools.query_engine = MagicMock()
        tools.query_engine.query.return_value = {
            'answer': 'Test answer',
            'sources': []
        }
        
        start_time = time.time()
        result = await tools.query_knowledge_graph("test query")
        end_time = time.time()
        
        # Verify performance metrics are included
        self.assertIn("Response Time:", result)
        self.assertIn("417x faster", result)
        
        # Verify timing is reasonable (should be very fast with mocked components)
        execution_time = (end_time - start_time) * 1000
        self.assertLess(execution_time, 1000)  # Should be under 1 second
    
    async def test_cache_simulation(self):
        """Test cache behavior simulation"""
        tools = Neo4jRAGTools()
        tools.rag = MagicMock()
        tools.query_engine = MagicMock()
        tools.query_engine.query.return_value = {'answer': 'Test', 'sources': []}
        
        # Simulate cache by adding cache entries
        tools.rag._query_cache = {'test_key': 'cached_value'}
        
        # Run query
        result = await tools.query_knowledge_graph("test")
        
        # Should show cache statistics
        self.assertIn("Cache Hit Rate:", result)
    
    async def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        tools = Neo4jRAGTools()
        tools.rag = MagicMock()
        tools.query_engine = MagicMock()
        tools.query_engine.query.return_value = {'answer': 'Test', 'sources': []}
        
        # Create multiple concurrent requests
        tasks = [
            tools.query_knowledge_graph(f"Query {i}")
            for i in range(10)
        ]
        
        # Execute concurrently
        results = await asyncio.gather(*tasks)
        
        # Verify all requests completed
        self.assertEqual(len(results), 10)
        self.assertEqual(tools._performance_stats['total_queries'], 10)
        
        # Verify all responses contain expected content
        for result in results:
            self.assertIn("417x faster", result)


class TestAzureDeploymentReadiness(unittest.TestCase):
    """Test Azure deployment readiness and configuration"""
    
    def test_environment_variable_handling(self):
        """Test proper handling of environment variables"""
        with patch.dict(os.environ, {
            'AZURE_AI_PROJECT_ENDPOINT': 'https://test.ai.azure.com',
            'AZURE_AI_MODEL_DEPLOYMENT_NAME': 'gpt-4o-mini',
            'NEO4J_URI': 'bolt://neo4j-container:7687'
        }):
            agent = Neo4jRAGAgent()
            
            self.assertEqual(agent.project_endpoint, 'https://test.ai.azure.com')
            self.assertEqual(agent.model_deployment, 'gpt-4o-mini')
    
    def test_default_configuration(self):
        """Test default configuration values"""
        agent = Neo4jRAGAgent()
        
        # Should use defaults when environment variables aren't set
        self.assertEqual(agent.model_deployment, 'gpt-4o-mini')
    
    def test_neo4j_connection_configuration(self):
        """Test Neo4j connection configuration for Azure"""
        tools = Neo4jRAGTools(
            neo4j_uri="bolt://neo4j-azure:7687",
            neo4j_user="neo4j",
            neo4j_password="production-password"
        )
        
        # Verify the configuration was set (we can't test actual connection without DB)
        self.assertIsNotNone(tools.rag)
        self.assertIsNotNone(tools.query_engine)


def run_integration_tests():
    """Run integration tests with actual Neo4j if available"""
    # This would run actual integration tests if Neo4j is available
    logger.info("Integration tests would run here with real Neo4j connection")
    pass


if __name__ == '__main__':
    # Run the test suite
    unittest.main(verbosity=2)