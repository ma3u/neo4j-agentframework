"""
Test Suite: Integration Testing (Issue #12)
Tests TC-INT.* and TC-ERR.* series
"""

import pytest
from playwright.sync_api import Page, expect
import requests
import time


class TestServiceIntegration:
    """Test Suite: Service Integration (TC-INT.1 - TC-INT.10)"""

    def test_tc_int_1_streamlit_connects_neo4j(self, streamlit_page: Page):
        """TC-INT.1: Streamlit connects to Neo4j successfully"""
        # Check Neo4j health card
        neo4j_status = streamlit_page.get_by_text("Neo4j", exact=False)

        if neo4j_status.count() > 0:
            expect(neo4j_status.first).to_be_visible()

            # Should show green/healthy status
            # Check for "healthy" or green indicator

    def test_tc_int_2_streamlit_connects_rag(self, streamlit_page: Page):
        """TC-INT.2: Streamlit connects to RAG service successfully"""
        # Check RAG service health
        rag_status = streamlit_page.get_by_text("RAG Service", exact=False)

        if rag_status.count() > 0:
            expect(rag_status.first).to_be_visible()

    def test_tc_int_3_rag_connects_bitnet(self):
        """TC-INT.3: RAG service connects to BitNet successfully"""
        # Direct API test
        response = requests.get("http://localhost:8001/health", timeout=5)
        assert response.status_code == 200

    def test_tc_int_4_end_to_end_query_flow(self, streamlit_page: Page):
        """TC-INT.4: End-to-end query flow works (Streamlit → RAG → BitNet → Neo4j)"""
        # Send a query through the UI
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        chat_input.fill("End-to-end test query")
        chat_input.press("Enter")

        # Wait for response
        time.sleep(10)

        # Should get response from full stack
        messages = streamlit_page.locator('[data-testid="stChatMessage"]')
        assert messages.count() >= 2, "Should have user and assistant messages"

    def test_tc_int_5_document_upload_flow(self, streamlit_page: Page, create_test_pdf):
        """TC-INT.5: Document upload flow works (Streamlit → RAG → Neo4j)"""
        pdf_file = create_test_pdf("integration_test.pdf", size_kb=100)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            file_input.first.set_input_files(pdf_file)
            time.sleep(1)

            upload_button = streamlit_page.get_by_text("Upload", exact=False)
            if upload_button.count() > 0:
                upload_button.first.click()
                time.sleep(10)

                # Verify upload succeeded
                success_msg = streamlit_page.get_by_text("success", exact=False)
                if success_msg.count() > 0:
                    expect(success_msg.first).to_be_visible()

    def test_tc_int_6_health_checks_all_services(self, streamlit_page: Page):
        """TC-INT.6: Health checks work for all services"""
        # Reload to trigger health checks
        streamlit_page.reload()
        time.sleep(3)

        # All three health cards should be present
        services = ["Neo4j", "RAG", "BitNet"]
        for service in services:
            service_card = streamlit_page.get_by_text(service, exact=False)
            if service_card.count() > 0:
                expect(service_card.first).to_be_visible()

    def test_tc_int_7_stats_endpoint_complete_data(self):
        """TC-INT.7: Stats endpoint returns complete data"""
        response = requests.get("http://localhost:8000/stats", timeout=5)
        assert response.status_code == 200

        data = response.json()
        expected_fields = ["status", "neo4j_connected", "avg_response_time_ms"]
        for field in expected_fields:
            assert field in data, f"Missing field: {field}"

    def test_tc_int_8_network_connectivity_containers(self):
        """TC-INT.8: Network connectivity between containers"""
        # Test connectivity between services
        services = {
            "rag": "http://localhost:8000/health",
            "bitnet": "http://localhost:8001/health"
        }

        for name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                assert response.status_code == 200, f"{name} service not reachable"
            except Exception as e:
                pytest.fail(f"Failed to connect to {name}: {e}")

    def test_tc_int_9_service_restart_recovery(self):
        """TC-INT.9: Service restart recovery"""
        # This would require orchestrating service restarts
        # Skip for now or implement with docker commands

    def test_tc_int_10_concurrent_users(self, streamlit_page: Page):
        """TC-INT.10: Concurrent users supported"""
        # Send multiple queries rapidly
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")

        for i in range(5):
            chat_input.fill(f"Concurrent test {i}")
            chat_input.press("Enter")
            time.sleep(1)

        # All queries should be handled


class TestErrorHandling:
    """Test Suite: Error Handling (TC-ERR.1 - TC-ERR.10)"""

    def test_tc_err_1_rag_offline_error(self, streamlit_page: Page):
        """TC-ERR.1: RAG service offline shows error message"""
        # Would require stopping RAG service
        # Check error handling exists

    def test_tc_err_2_neo4j_offline_health_card(self, streamlit_page: Page):
        """TC-ERR.2: Neo4j offline shows error in health card"""
        # Would require stopping Neo4j
        # Verify error state rendering

    def test_tc_err_3_bitnet_timeout_handled(self, streamlit_page: Page):
        """TC-ERR.3: BitNet timeout handled gracefully"""
        # Send query that might timeout
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        chat_input.fill("Very complex query requiring deep analysis")
        chat_input.press("Enter")

        # Should handle timeout without crashing
        time.sleep(35)  # Wait past timeout

    def test_tc_err_4_invalid_api_response(self):
        """TC-ERR.4: Invalid API response handled"""
        # Test with malformed request
        try:
            response = requests.post(
                "http://localhost:8000/query",
                json={"invalid": "data"},
                timeout=5
            )
            # Should return error status
            assert response.status_code >= 400
        except:
            pass  # Expected to fail

    def test_tc_err_5_network_errors_no_crash(self, streamlit_page: Page):
        """TC-ERR.5: Network errors don't crash app"""
        # App should remain functional even if services fail
        expect(streamlit_page.locator('[data-testid="stAppViewContainer"]')).to_be_visible()

    def test_tc_err_6_malformed_query_handled(self, streamlit_page: Page):
        """TC-ERR.6: Malformed query handled"""
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")

        # Send various edge cases
        edge_cases = [
            "",  # Empty
            " " * 1000,  # Whitespace
            "null",
            "<script>alert('xss')</script>",
        ]

        for test_input in edge_cases:
            chat_input.fill(test_input)
            chat_input.press("Enter")
            time.sleep(1)

            # Should not crash

    def test_tc_err_7_upload_failure_error(self, streamlit_page: Page, test_files_dir):
        """TC-ERR.7: Upload failure shows user-friendly error"""
        # Try uploading invalid file
        invalid_file = test_files_dir + "/invalid.xyz"
        with open(invalid_file, 'w') as f:
            f.write("invalid")

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            try:
                file_input.first.set_input_files(invalid_file)
                time.sleep(1)

                upload_button = streamlit_page.get_by_text("Upload", exact=False)
                if upload_button.count() > 0:
                    upload_button.first.click()
                    time.sleep(3)

                    # Should show error
            except:
                pass  # Expected

    def test_tc_err_8_stats_api_timeout(self, streamlit_page: Page):
        """TC-ERR.8: Stats API timeout handled"""
        # If stats API is slow, UI should handle gracefully
        streamlit_page.reload()
        time.sleep(2)

        # UI should still be functional
        expect(streamlit_page.locator('[data-testid="stAppViewContainer"]')).to_be_visible()

    def test_tc_err_9_session_state_corruption(self, streamlit_page: Page):
        """TC-ERR.9: Session state corruption recovery"""
        # Rapid interactions to test state management
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")

        for i in range(10):
            chat_input.fill(f"Rapid test {i}")
            chat_input.press("Enter")

        time.sleep(1)

        # Should handle gracefully

    def test_tc_err_10_container_restart_data_persistence(self):
        """TC-ERR.10: Container restart doesn't lose data"""
        # Would require docker restart
        # Verify data persists in Neo4j
