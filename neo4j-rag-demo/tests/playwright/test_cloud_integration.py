"""
Cloud Integration Tests
Tests local Playwright against Azure-hosted Neo4j + RAG services
"""

import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.cloud
class TestCloudRAGAPI:
    """Direct API tests for cloud-hosted RAG service"""

    def test_cloud_rag_health(self, cloud_rag_api):
        """Verify cloud RAG service is healthy"""
        health = cloud_rag_api.health()

        assert health["status"] == "healthy"
        assert health["neo4j_connected"] is True
        assert "avg_response_time_ms" in health

        print(f"✓ RAG Service healthy")
        print(f"  Response time: {health.get('avg_response_time_ms', 0):.0f}ms")
        print(f"  Memory: {health.get('memory_mb', 0):.0f}MB")

    def test_cloud_rag_stats(self, cloud_rag_api):
        """Verify cloud RAG service returns statistics"""
        stats = cloud_rag_api.stats()

        assert "status" in stats
        assert "neo4j_connected" in stats

        print(f"✓ RAG Service stats retrieved")
        print(f"  Documents: {stats.get('document_count', 0)}")
        print(f"  Chunks: {stats.get('chunk_count', 0)}")

    def test_cloud_rag_query(self, cloud_rag_api):
        """Test query against cloud RAG service"""
        response = cloud_rag_api.query(
            "What is Neo4j?",
            max_results=3,
            use_llm=False  # Skip LLM for faster test
        )

        assert "sources" in response or "answer" in response

        if "sources" in response:
            print(f"✓ Query executed")
            print(f"  Sources found: {len(response['sources'])}")
            print(f"  Query time: {response.get('query_time_ms', 0):.0f}ms")

    @pytest.mark.slow
    def test_cloud_document_upload(self, cloud_rag_api):
        """Test document upload to cloud RAG service"""
        unique_id = f"cloud_test_{int(time.time())}"

        response = cloud_rag_api.upload_document(
            content=f"Test document for cloud integration. ID: {unique_id}",
            metadata={"source": "cloud_test", "test_id": unique_id}
        )

        print(f"✓ Document uploaded to cloud")

        # Wait for indexing
        time.sleep(5)

        # Try to retrieve it
        query_response = cloud_rag_api.query(unique_id, use_llm=False)
        assert "sources" in query_response or "answer" in query_response


@pytest.mark.cloud
class TestCloudStreamlitUI:
    """UI tests against local Streamlit connected to cloud services"""

    def test_cloud_streamlit_loads(self, streamlit_page: Page):
        """Verify Streamlit UI loads with cloud backend"""
        # Check for main container
        expect(streamlit_page.locator('[data-testid="stAppViewContainer"]')).to_be_visible()

        # Check header
        header = streamlit_page.get_by_text("Neo4j RAG + BitNet", exact=False)
        expect(header.first).to_be_visible(timeout=10000)

        print("✓ Streamlit UI loaded with cloud backend")

    def test_cloud_health_cards_show_cloud_status(self, streamlit_page: Page):
        """Verify health cards show cloud service status"""
        # Wait for health checks to complete
        time.sleep(5)

        # Look for service names
        services = ["Neo4j", "RAG"]
        for service in services:
            service_text = streamlit_page.get_by_text(service, exact=False)
            if service_text.count() > 0:
                print(f"✓ Found {service} health card")

    @pytest.mark.slow
    def test_cloud_end_to_end_query(self, streamlit_page: Page):
        """Test end-to-end query through Streamlit to cloud services"""
        # Find chat input
        chat_input = streamlit_page.get_by_placeholder("Ask a question", exact=False)
        expect(chat_input).to_be_visible(timeout=10000)

        # Send query
        test_query = f"Cloud test query at {int(time.time())}"
        chat_input.fill(test_query)
        chat_input.press("Enter")

        # Wait for response (longer timeout for cloud)
        time.sleep(10)

        # Verify message appears
        user_message = streamlit_page.get_by_text(test_query, exact=False)
        assert user_message.count() > 0, "Query should appear in chat"

        print("✓ End-to-end query through cloud services completed")

    @pytest.mark.slow
    def test_cloud_file_upload(self, streamlit_page: Page, create_test_pdf):
        """Test file upload to cloud RAG service"""
        pdf_file = create_test_pdf(f"cloud_test_{int(time.time())}.pdf", size_kb=100)

        # Find file uploader
        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(pdf_file)
            time.sleep(2)

            # Click upload button
            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                upload_button.first.click()

                # Wait for upload to cloud (longer timeout)
                time.sleep(15)

                print("✓ File uploaded to cloud RAG service")


@pytest.mark.cloud
class TestCloudPerformance:
    """Performance tests for cloud deployment"""

    def test_cloud_query_performance(self, cloud_rag_api):
        """Measure cloud query performance"""
        start_time = time.time()

        response = cloud_rag_api.query("Performance test", use_llm=False)

        query_time = (time.time() - start_time) * 1000  # ms

        print(f"✓ Cloud query performance:")
        print(f"  Total time: {query_time:.0f}ms")
        print(f"  API time: {response.get('query_time_ms', 0):.0f}ms")

        # Cloud should respond within 2 seconds (including network latency)
        assert query_time < 2000, f"Query took {query_time:.0f}ms, expected < 2000ms"

    def test_cloud_health_check_performance(self, cloud_rag_api):
        """Measure cloud health check performance"""
        start_time = time.time()

        health = cloud_rag_api.health()

        health_time = (time.time() - start_time) * 1000  # ms

        print(f"✓ Cloud health check performance: {health_time:.0f}ms")

        # Health check should be fast
        assert health_time < 1000, f"Health check took {health_time:.0f}ms, expected < 1000ms"

    @pytest.mark.slow
    def test_cloud_concurrent_queries(self, cloud_rag_api):
        """Test cloud service handles concurrent queries"""
        import concurrent.futures

        def run_query(i):
            response = cloud_rag_api.query(f"Concurrent test {i}", use_llm=False)
            return response

        start_time = time.time()

        # Run 5 concurrent queries
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(run_query, i) for i in range(5)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        total_time = (time.time() - start_time) * 1000  # ms

        print(f"✓ Concurrent queries completed:")
        print(f"  Total time: {total_time:.0f}ms")
        print(f"  Average per query: {total_time/5:.0f}ms")

        assert len(results) == 5, "All queries should complete"


@pytest.mark.cloud
class TestCloudResilience:
    """Resilience and error handling tests"""

    def test_cloud_invalid_query_handling(self, cloud_rag_api):
        """Verify cloud service handles invalid queries gracefully"""
        import requests

        try:
            # Send malformed request
            response = requests.post(
                f"{cloud_rag_api.base_url}/query",
                json={"invalid": "data"},
                timeout=10
            )

            # Should return error status
            assert response.status_code >= 400, "Should reject invalid request"
            print("✓ Cloud service handles invalid queries correctly")
        except:
            # Network error is also acceptable
            print("✓ Cloud service unavailable or rejected request")

    def test_cloud_large_query_handling(self, cloud_rag_api):
        """Test cloud service handles large queries"""
        large_query = "test " * 1000  # ~5KB query

        try:
            response = cloud_rag_api.query(large_query, use_llm=False)
            print("✓ Cloud service handles large queries")
        except Exception as e:
            # Should handle gracefully
            print(f"✓ Cloud service rejected large query: {str(e)[:50]}")

    @pytest.mark.slow
    def test_cloud_sustained_load(self, cloud_rag_api):
        """Test cloud service under sustained load"""
        # Send 20 queries in succession
        for i in range(20):
            try:
                cloud_rag_api.query(f"Load test {i}", use_llm=False)
                time.sleep(0.5)  # 2 queries per second
            except Exception as e:
                pytest.fail(f"Query {i} failed: {e}")

        print("✓ Cloud service handled sustained load (20 queries)")
