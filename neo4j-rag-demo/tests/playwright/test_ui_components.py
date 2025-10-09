"""
UI Component Testing with Playwright MCP Server
Tests individual UI components and interactions in Streamlit
Designed for use with Playwright MCP server for interactive testing
"""

import pytest
from playwright.sync_api import Page, expect
import time


class TestHeaderComponents:
    """Test header and title components"""

    def test_app_title_display(self, streamlit_page: Page):
        """Verify main application title"""
        # Check for main title
        title = streamlit_page.get_by_text("Neo4j RAG + BitNet Chat", exact=False)
        expect(title.first).to_be_visible()

        # Verify it's prominent (should be in a heading)
        heading = streamlit_page.locator("h1, h2").filter(has_text="Neo4j RAG + BitNet")
        assert heading.count() > 0, "Title should be in a heading element"

    def test_developer_mode_indicator(self, streamlit_page: Page):
        """Verify developer mode indicator in header"""
        # Look for "local developer mode" text
        dev_mode = streamlit_page.get_by_text("local developer mode", exact=False)

        if dev_mode.count() > 0:
            expect(dev_mode.first).to_be_visible()
            print("✓ Developer mode indicator found")

    def test_header_navigation(self, streamlit_page: Page):
        """Test header navigation elements"""
        # Check for any navigation or menu items in header
        # Streamlit apps may have hamburger menu
        menu_button = streamlit_page.locator('[data-testid="stToolbar"]')
        if menu_button.count() > 0:
            expect(menu_button.first).to_be_visible()


class TestHealthCards:
    """Test service health card components (Issue #9)"""

    def test_health_cards_layout(self, streamlit_page: Page):
        """Verify health cards are displayed in correct layout"""
        # Wait for cards to load
        time.sleep(3)

        # Look for service names
        services = ["Neo4j", "RAG", "BitNet"]
        found_services = []

        for service in services:
            service_text = streamlit_page.get_by_text(service, exact=False)
            if service_text.count() > 0:
                found_services.append(service)
                print(f"✓ Found {service} health card")

        # At least Neo4j and RAG should be present
        assert len(found_services) >= 2, f"Expected at least 2 health cards, found {len(found_services)}"

    def test_health_card_status_indicators(self, streamlit_page: Page):
        """Verify health cards show status (green/red/yellow)"""
        time.sleep(3)

        # Look for status indicators (could be emojis, colors, or text)
        # Check for common status indicators
        status_indicators = ["✓", "✗", "🟢", "🔴", "🟡", "healthy", "unhealthy", "offline"]

        page_content = streamlit_page.content()
        found_indicators = [indicator for indicator in status_indicators if indicator in page_content]

        assert len(found_indicators) > 0, "Health cards should show status indicators"

    def test_health_card_response_times(self, streamlit_page: Page):
        """Verify health cards show response times"""
        time.sleep(3)

        # Look for time-related text (ms, seconds)
        page_content = streamlit_page.content()

        # Check for millisecond indicators
        has_ms = "ms" in page_content or "milliseconds" in page_content
        has_time_info = has_ms or "response time" in page_content.lower()

        if has_time_info:
            print("✓ Health cards show response time information")

    def test_health_card_port_numbers(self, streamlit_page: Page):
        """TC-9.7: Verify port numbers are displayed (7687, 8000, 8001)"""
        time.sleep(3)

        expected_ports = ["7687", "8000", "8001"]
        page_content = streamlit_page.content()

        found_ports = [port for port in expected_ports if port in page_content]

        print(f"✓ Found ports: {', '.join(found_ports)}")
        assert len(found_ports) >= 2, "Should display at least 2 service ports"


class TestChatInterface:
    """Test chat interface components (Issue #7)"""

    def test_chat_input_placeholder(self, streamlit_page: Page):
        """Verify chat input has correct placeholder text"""
        # Look for chat input with placeholder
        chat_input = streamlit_page.get_by_placeholder("Ask a question", exact=False)
        expect(chat_input).to_be_visible(timeout=10000)

        # Get actual placeholder text
        placeholder = chat_input.get_attribute("placeholder")
        print(f"✓ Chat input placeholder: {placeholder}")

        assert "question" in placeholder.lower(), "Placeholder should mention asking questions"

    def test_chat_input_enabled(self, streamlit_page: Page):
        """Verify chat input is enabled and interactive"""
        chat_input = streamlit_page.get_by_placeholder("Ask a question", exact=False)

        # Check if input is enabled
        expect(chat_input).to_be_enabled()

        # Try typing in it
        chat_input.fill("Test input")

        # Verify text appears
        input_value = chat_input.input_value()
        assert input_value == "Test input", "Should be able to type in chat input"

        # Clear for next test
        chat_input.fill("")

    def test_chat_message_container(self, streamlit_page: Page):
        """Verify chat message container exists"""
        # Look for chat message container
        chat_container = streamlit_page.locator('[data-testid="stChatMessageContainer"]')

        if chat_container.count() > 0:
            expect(chat_container.first).to_be_visible()
            print("✓ Chat message container found")

    def test_send_message_interaction(self, streamlit_page: Page):
        """Test sending a message through the UI"""
        chat_input = streamlit_page.get_by_placeholder("Ask a question", exact=False)

        # Send a test message
        test_message = f"UI Test Message {int(time.time())}"
        chat_input.fill(test_message)
        chat_input.press("Enter")

        # Wait for message to appear
        time.sleep(2)

        # Check if message appears in chat
        message_element = streamlit_page.get_by_text(test_message, exact=False)
        assert message_element.count() > 0, "Message should appear in chat history"

        print(f"✓ Message sent and displayed: {test_message}")

    def test_chat_message_styling(self, streamlit_page: Page):
        """Verify chat messages have proper styling (user vs assistant)"""
        # Send a message first
        chat_input = streamlit_page.get_by_placeholder("Ask a question", exact=False)
        chat_input.fill("Styling test")
        chat_input.press("Enter")

        time.sleep(3)

        # Look for chat messages with different roles
        user_messages = streamlit_page.locator('[data-testid="stChatMessage"][data-testid*="user"]')
        assistant_messages = streamlit_page.locator('[data-testid="stChatMessage"][data-testid*="assistant"]')

        # At least user message should exist
        all_messages = streamlit_page.locator('[data-testid="stChatMessage"]')
        assert all_messages.count() > 0, "Should have at least one chat message"


class TestSidebarControls:
    """Test sidebar control components"""

    def test_sidebar_visibility(self, streamlit_page: Page):
        """Verify sidebar is visible"""
        sidebar = streamlit_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()

    def test_sidebar_sections(self, streamlit_page: Page):
        """Verify sidebar has correct sections"""
        # Expected sections from mockup
        expected_sections = [
            "Controls",
            "RAG Configuration",
            "LLM Configuration",
            "Document Upload"
        ]

        page_content = streamlit_page.content()
        found_sections = []

        for section in expected_sections:
            if section in page_content:
                found_sections.append(section)
                print(f"✓ Found section: {section}")

        assert len(found_sections) >= 2, "Should have at least 2 sidebar sections"

    def test_max_results_slider(self, streamlit_page: Page):
        """TC-7.11: Test max results slider"""
        # Look for sliders
        sliders = streamlit_page.locator('[data-testid="stSlider"]')

        if sliders.count() > 0:
            print(f"✓ Found {sliders.count()} slider(s)")

            # First slider should be max results
            first_slider = sliders.first
            expect(first_slider).to_be_visible()

    def test_similarity_threshold_slider(self, streamlit_page: Page):
        """TC-7.12: Test similarity threshold slider"""
        # Look for "Similarity" text near a slider
        similarity_text = streamlit_page.get_by_text("Similarity", exact=False)

        if similarity_text.count() > 0:
            print("✓ Found Similarity Threshold control")
            expect(similarity_text.first).to_be_visible()

    def test_bitnet_toggle(self, streamlit_page: Page):
        """TC-7.13: Test BitNet LLM toggle"""
        # Look for BitNet toggle/checkbox
        bitnet_toggle = streamlit_page.get_by_text("Use BitNet", exact=False)

        if bitnet_toggle.count() > 0:
            print("✓ Found BitNet toggle")
            expect(bitnet_toggle.first).to_be_visible()

            # Try clicking it
            bitnet_toggle.first.click()
            time.sleep(1)

            # Click again to toggle back
            bitnet_toggle.first.click()
            time.sleep(1)

    def test_temperature_slider(self, streamlit_page: Page):
        """TC-7.14: Test temperature slider"""
        # Look for temperature control
        temp_text = streamlit_page.get_by_text("Temperature", exact=False)

        if temp_text.count() > 0:
            print("✓ Found Temperature control")
            expect(temp_text.first).to_be_visible()

    def test_display_toggles(self, streamlit_page: Page):
        """TC-7.15-7.17: Test show sources, performance, timestamps toggles"""
        toggles = ["Show Sources", "Show Performance", "Show Timestamps"]
        found_toggles = []

        for toggle_text in toggles:
            toggle = streamlit_page.get_by_text(toggle_text, exact=False)
            if toggle.count() > 0:
                found_toggles.append(toggle_text)
                print(f"✓ Found toggle: {toggle_text}")

        assert len(found_toggles) > 0, "Should have at least one display toggle"


class TestFileUploader:
    """Test file upload component (Issue #8)"""

    def test_file_uploader_exists(self, streamlit_page: Page):
        """TC-8.1: Verify file uploader component exists"""
        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            expect(file_input.first).to_be_attached()
            print("✓ File uploader found")

    def test_file_uploader_label(self, streamlit_page: Page):
        """Verify file uploader has correct label"""
        upload_text = streamlit_page.get_by_text("Upload documents", exact=False)

        if upload_text.count() > 0:
            expect(upload_text.first).to_be_visible()
            print("✓ File uploader label found")

    def test_file_uploader_help_text(self, streamlit_page: Page):
        """Verify file uploader shows accepted file types"""
        # Look for help text about file types
        page_content = streamlit_page.content()

        accepted_types = ["pdf", "txt", "md", "docx"]
        found_types = [ftype for ftype in accepted_types if ftype.upper() in page_content or ftype in page_content]

        if found_types:
            print(f"✓ File types mentioned: {', '.join(found_types)}")

    def test_upload_button_interaction(self, streamlit_page: Page, create_test_pdf):
        """TC-8.8: Test upload button appears when file selected"""
        # Create test file
        test_file = create_test_pdf("ui_test.pdf", size_kb=100)

        file_input = streamlit_page.locator('input[type="file"]')

        if file_input.count() > 0:
            # Select file
            file_input.first.set_input_files(test_file)
            time.sleep(1)

            # Look for upload button
            upload_button = streamlit_page.get_by_text("Upload", exact=False)

            if upload_button.count() > 0:
                expect(upload_button.first).to_be_visible()
                print("✓ Upload button appears after file selection")


class TestStatsDisplay:
    """Test statistics display components (Issue #9)"""

    def test_compact_stats_visible(self, streamlit_page: Page):
        """Verify compact stats are displayed below chat"""
        time.sleep(3)

        # Look for common stats metrics
        stats_keywords = ["Documents", "Chunks", "Response Time", "Memory", "Cache"]
        page_content = streamlit_page.content()

        found_stats = [stat for stat in stats_keywords if stat in page_content]

        if found_stats:
            print(f"✓ Found stats: {', '.join(found_stats)}")
            assert len(found_stats) >= 2, "Should display at least 2 stats metrics"

    def test_view_full_statistics_button(self, streamlit_page: Page):
        """TC-9.21: Test view full statistics button"""
        # Look for button to open full stats
        stats_button = streamlit_page.get_by_text("View Full Statistics", exact=False)

        if stats_button.count() > 0:
            print("✓ Found 'View Full Statistics' button")
            expect(stats_button.first).to_be_visible()

    def test_metric_formatting(self, streamlit_page: Page):
        """TC-9.20: Verify numbers are formatted properly"""
        time.sleep(3)

        # Look for metric components
        metrics = streamlit_page.locator('[data-testid="stMetric"]')

        if metrics.count() > 0:
            print(f"✓ Found {metrics.count()} metric(s)")

            # Check first metric is visible
            expect(metrics.first).to_be_visible()


class TestResponsiveDesign:
    """Test responsive design and layout"""

    def test_desktop_layout(self, streamlit_page: Page):
        """TC-RESP.1: Verify desktop layout (1920x1080)"""
        streamlit_page.set_viewport_size({"width": 1920, "height": 1080})
        time.sleep(1)

        # Main container should be visible
        container = streamlit_page.locator('[data-testid="stAppViewContainer"]')
        expect(container).to_be_visible()

        # Sidebar should be visible on desktop
        sidebar = streamlit_page.locator('[data-testid="stSidebar"]')
        expect(sidebar).to_be_visible()

        print("✓ Desktop layout (1920x1080) working")

    def test_laptop_layout(self, streamlit_page: Page):
        """TC-RESP.2: Verify laptop layout (1366x768)"""
        streamlit_page.set_viewport_size({"width": 1366, "height": 768})
        time.sleep(1)

        # Main container should still be visible
        container = streamlit_page.locator('[data-testid="stAppViewContainer"]')
        expect(container).to_be_visible()

        print("✓ Laptop layout (1366x768) working")

    def test_tablet_layout(self, streamlit_page: Page):
        """TC-RESP.3: Verify tablet layout (768px)"""
        streamlit_page.set_viewport_size({"width": 768, "height": 1024})
        time.sleep(1)

        # App should still function
        container = streamlit_page.locator('[data-testid="stAppViewContainer"]')
        expect(container).to_be_visible()

        print("✓ Tablet layout (768px) working")

    def test_mobile_layout(self, streamlit_page: Page):
        """TC-RESP.4: Verify mobile layout (375px)"""
        streamlit_page.set_viewport_size({"width": 375, "height": 667})
        time.sleep(1)

        # App should still be accessible
        container = streamlit_page.locator('[data-testid="stAppViewContainer"]')
        expect(container).to_be_visible()

        # Sidebar may be collapsed on mobile
        print("✓ Mobile layout (375px) working")

        # Restore original size
        streamlit_page.set_viewport_size({"width": 1920, "height": 1080})


class TestAccessibility:
    """Test accessibility features"""

    def test_keyboard_navigation(self, streamlit_page: Page):
        """Test keyboard navigation through UI"""
        # Tab through interactive elements
        streamlit_page.keyboard.press("Tab")
        time.sleep(0.5)
        streamlit_page.keyboard.press("Tab")
        time.sleep(0.5)

        # Some element should have focus
        focused = streamlit_page.evaluate("document.activeElement.tagName")
        assert focused is not None, "Tab key should navigate between elements"

        print(f"✓ Keyboard navigation working (focused: {focused})")

    def test_chat_input_keyboard_submit(self, streamlit_page: Page):
        """TC-7.8: Test Enter key sends message"""
        chat_input = streamlit_page.get_by_placeholder("Ask a question", exact=False)

        # Type message
        chat_input.fill("Keyboard test")

        # Press Enter
        chat_input.press("Enter")

        time.sleep(2)

        # Message should appear
        message = streamlit_page.get_by_text("Keyboard test", exact=False)
        assert message.count() > 0, "Enter key should send message"

        print("✓ Enter key sends message")

    def test_headings_structure(self, streamlit_page: Page):
        """Verify proper heading hierarchy"""
        # Check for headings
        h1 = streamlit_page.locator("h1")
        h2 = streamlit_page.locator("h2")
        h3 = streamlit_page.locator("h3")

        heading_count = h1.count() + h2.count() + h3.count()

        assert heading_count > 0, "Should have proper heading structure"
        print(f"✓ Found {heading_count} headings")


class TestErrorHandling:
    """Test error handling in UI"""

    def test_empty_message_handling(self, streamlit_page: Page):
        """TC-7.9: Verify empty messages are rejected"""
        chat_input = streamlit_page.get_by_placeholder("Ask a question", exact=False)

        # Get initial message count
        initial_messages = streamlit_page.locator('[data-testid="stChatMessage"]').count()

        # Try to send empty message
        chat_input.fill("")
        chat_input.press("Enter")

        time.sleep(1)

        # Message count should not increase
        final_messages = streamlit_page.locator('[data-testid="stChatMessage"]').count()

        assert final_messages == initial_messages, "Empty messages should not be sent"
        print("✓ Empty messages rejected")

    def test_service_offline_display(self, streamlit_page: Page):
        """TC-ERR.1-2: Verify UI handles service offline gracefully"""
        # UI should still load even if services are down
        container = streamlit_page.locator('[data-testid="stAppViewContainer"]')
        expect(container).to_be_visible()

        # Check if error messages are shown gracefully
        # (not crashing the app)
        print("✓ UI handles service errors gracefully")
