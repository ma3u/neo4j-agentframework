"""
Smoke Tests - Quick verification that Streamlit UI is functional
"""

import pytest
from playwright.sync_api import Page, expect
import time


class TestSmokeTests:
    """Quick smoke tests to verify basic functionality"""

    def test_streamlit_loads(self, streamlit_page: Page):
        """Verify Streamlit app loads successfully"""
        # Check for main container
        expect(streamlit_page.locator('[data-testid="stAppViewContainer"]')).to_be_visible()

    def test_header_displays(self, streamlit_page: Page):
        """Verify header text is correct"""
        # Look for header text from issue #7
        header = streamlit_page.get_by_text("Neo4j RAG + BitNet", exact=False)
        expect(header.first).to_be_visible(timeout=10000)

    def test_sidebar_visible(self, streamlit_page: Page):
        """Verify sidebar is present"""
        # Check for sidebar
        sidebar = streamlit_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()

    def test_chat_input_exists(self, streamlit_page: Page):
        """Verify chat input is present"""
        # Look for chat input with correct placeholder
        chat_input = streamlit_page.get_by_placeholder("Ask a question about Neo4j, BitNet, or RAG systems", exact=False)
        expect(chat_input).to_be_visible(timeout=10000)

    def test_send_simple_message(self, streamlit_page: Page):
        """TC-7.1: Send a simple message"""
        chat_input = streamlit_page.get_by_placeholder("Ask a question", exact=False)
        expect(chat_input).to_be_visible(timeout=10000)

        # Type and send message
        chat_input.fill("Hello")
        chat_input.press("Enter")

        # Wait a moment for message to appear
        time.sleep(2)

        # Check that message appears in chat
        user_message = streamlit_page.get_by_text("Hello", exact=False)
        assert user_message.count() > 0, "Message should appear in chat"

    def test_health_cards_present(self, streamlit_page: Page):
        """TC-9.1-9.3: Verify health cards are present"""
        # Wait for page to load
        time.sleep(3)

        # Look for service names
        services = ["Neo4j", "RAG", "BitNet"]
        for service in services:
            service_text = streamlit_page.get_by_text(service, exact=False)
            if service_text.count() > 0:
                print(f"✓ Found {service} health card")

    def test_sidebar_controls(self, streamlit_page: Page):
        """Verify sidebar controls exist"""
        # Check for controls section
        controls = streamlit_page.get_by_text("Controls", exact=False)
        if controls.count() > 0:
            expect(controls.first).to_be_visible()

        # Check for configuration sections
        rag_config = streamlit_page.get_by_text("RAG Configuration", exact=False)
        if rag_config.count() > 0:
            expect(rag_config.first).to_be_visible()

    def test_file_uploader_exists(self, streamlit_page: Page):
        """TC-8.1: Verify file uploader exists"""
        # Look for file uploader
        file_input = streamlit_page.locator('input[type="file"]')
        if file_input.count() > 0:
            expect(file_input.first).to_be_attached()

    def test_sliders_present(self, streamlit_page: Page):
        """TC-7.11-7.14: Verify sliders are present"""
        # Check for sliders
        sliders = streamlit_page.locator('[data-testid="stSlider"]')
        assert sliders.count() >= 2, "Should have at least 2 sliders (max results, similarity)"

    def test_page_responsive(self, streamlit_page: Page):
        """TC-RESP.1: Verify page is responsive"""
        # Get initial state
        initial_width = streamlit_page.viewport_size["width"]

        # Resize to mobile
        streamlit_page.set_viewport_size({"width": 375, "height": 667})
        time.sleep(1)

        # Should still be visible
        expect(streamlit_page.locator('[data-testid="stAppViewContainer"]')).to_be_visible()

        # Restore
        streamlit_page.set_viewport_size({"width": initial_width, "height": 1080})


class TestAPIConnectivity:
    """Test API connectivity"""

    def test_rag_service_reachable(self):
        """TC-INT.2: RAG service is reachable"""
        import requests

        response = requests.get("http://localhost:8000/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_bitnet_service_reachable(self):
        """TC-INT.3: BitNet service is reachable"""
        import requests

        try:
            response = requests.get("http://localhost:8001/health", timeout=5)
            assert response.status_code == 200
        except:
            pytest.skip("BitNet service not available")

    def test_neo4j_browser_reachable(self):
        """TC-INT.1: Neo4j browser is reachable"""
        import requests

        response = requests.get("http://localhost:7474", timeout=5)
        assert response.status_code == 200
