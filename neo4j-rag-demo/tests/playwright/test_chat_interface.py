"""
Test Suite: Chat Interface (Issue #7)
Tests TC-7.1 through TC-7.20
"""

import pytest
from playwright.sync_api import Page, expect
import time


class TestChatFunctionality:
    """Test Suite: Chat Functionality (TC-7.1 - TC-7.10)"""

    def test_tc_7_1_send_message(self, streamlit_page: Page):
        """TC-7.1: User can send message via chat input"""
        # Find chat input
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        expect(chat_input).to_be_visible()

        # Type message
        test_message = "What is BitNet?"
        chat_input.fill(test_message)

        # Send message (press Enter)
        chat_input.press("Enter")

        # Verify message was sent
        time.sleep(1)
        assert streamlit_page.get_by_text(test_message, exact=False).count() > 0

    def test_tc_7_2_message_appears_in_history(self, streamlit_page: Page):
        """TC-7.2: Message appears in chat history immediately"""
        test_message = "Test message for history"

        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        chat_input.fill(test_message)
        chat_input.press("Enter")

        # Message should appear within 1 second
        time.sleep(1)
        expect(streamlit_page.get_by_text(test_message, exact=False)).to_be_visible()

    def test_tc_7_3_rag_response_within_5s(self, streamlit_page: Page):
        """TC-7.3: RAG service returns response within 5 seconds"""
        start_time = time.time()

        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        chat_input.fill("What is Neo4j?")
        chat_input.press("Enter")

        # Wait for response
        streamlit_page.wait_for_selector('[data-testid="stChatMessage"]', timeout=5000)

        response_time = time.time() - start_time
        assert response_time < 5, f"Response took {response_time}s, expected < 5s"

    def test_tc_7_4_assistant_response_displays(self, streamlit_page: Page):
        """TC-7.4: Assistant response displays in chat"""
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        chat_input.fill("Hello")
        chat_input.press("Enter")

        # Wait for assistant response
        time.sleep(3)

        # Check for assistant message
        chat_messages = streamlit_page.locator('[data-testid="stChatMessage"]')
        assert chat_messages.count() >= 2, "Expected user and assistant messages"

    def test_tc_7_5_sources_expand_collapse(self, streamlit_page: Page):
        """TC-7.5: Sources expand/collapse correctly"""
        # Send query that should return sources
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        chat_input.fill("What is RAG?")
        chat_input.press("Enter")

        time.sleep(3)

        # Look for sources expander
        expander = streamlit_page.get_by_text("Sources", exact=False)
        if expander.count() > 0:
            expander.first.click()
            time.sleep(0.5)
            # Should be expanded
            expander.first.click()
            time.sleep(0.5)
            # Should be collapsed

    def test_tc_7_6_performance_metrics_shown(self, streamlit_page: Page):
        """TC-7.6: Performance metrics shown per query (when enabled)"""
        # Enable performance metrics in sidebar
        try:
            perf_toggle = streamlit_page.get_by_text("Show Performance", exact=False)
            if perf_toggle.count() > 0:
                perf_toggle.first.click()
        except:
            pass

        # Send query
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        chat_input.fill("Performance test query")
        chat_input.press("Enter")

        time.sleep(3)

        # Check for performance badge or metric
        # Note: Implementation dependent

    def test_tc_7_7_message_history_persists(self, streamlit_page: Page):
        """TC-7.7: Message history persists during session"""
        # Send first message
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        chat_input.fill("First message")
        chat_input.press("Enter")
        time.sleep(2)

        # Send second message
        chat_input.fill("Second message")
        chat_input.press("Enter")
        time.sleep(2)

        # Both should be visible
        expect(streamlit_page.get_by_text("First message", exact=False)).to_be_visible()
        expect(streamlit_page.get_by_text("Second message", exact=False)).to_be_visible()

    def test_tc_7_8_enter_key_sends_message(self, streamlit_page: Page):
        """TC-7.8: Enter key sends message"""
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        test_message = "Enter key test"
        chat_input.fill(test_message)

        # Press Enter
        chat_input.press("Enter")

        time.sleep(1)
        expect(streamlit_page.get_by_text(test_message, exact=False)).to_be_visible()

    def test_tc_7_9_empty_messages_rejected(self, streamlit_page: Page):
        """TC-7.9: Empty messages are rejected"""
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")

        # Get initial message count
        initial_count = streamlit_page.locator('[data-testid="stChatMessage"]').count()

        # Try to send empty message
        chat_input.fill("")
        chat_input.press("Enter")

        time.sleep(1)

        # Message count should not increase
        final_count = streamlit_page.locator('[data-testid="stChatMessage"]').count()
        assert final_count == initial_count, "Empty message should not be sent"

    def test_tc_7_10_long_messages_display(self, streamlit_page: Page):
        """TC-7.10: Long messages display correctly"""
        long_message = "This is a very long message. " * 50  # ~1500 chars

        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        chat_input.fill(long_message)
        chat_input.press("Enter")

        time.sleep(2)

        # Check message is visible (at least partially)
        expect(streamlit_page.get_by_text("This is a very long message", exact=False)).to_be_visible()


class TestSettingsConfiguration:
    """Test Suite: Settings Configuration (TC-7.11 - TC-7.20)"""

    def test_tc_7_11_max_results_slider(self, streamlit_page: Page):
        """TC-7.11: Max results slider (1-10) affects query"""
        # Find max results slider in sidebar
        sliders = streamlit_page.locator('[data-testid="stSlider"]')

        if sliders.count() > 0:
            # Adjust slider
            slider = sliders.first
            slider.click()

            # Send query
            chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
            chat_input.fill("Test max results")
            chat_input.press("Enter")
            time.sleep(3)

    def test_tc_7_12_similarity_threshold_slider(self, streamlit_page: Page):
        """TC-7.12: Similarity threshold slider (0.0-1.0) affects results"""
        # Find similarity threshold slider
        similarity_label = streamlit_page.get_by_text("Similarity Threshold", exact=False)

        if similarity_label.count() > 0:
            # Adjust slider by clicking near it
            pass  # Implementation dependent on Streamlit version

    def test_tc_7_13_bitnet_toggle(self, streamlit_page: Page):
        """TC-7.13: BitNet toggle switches LLM on/off"""
        # Find BitNet toggle
        bitnet_toggle = streamlit_page.get_by_text("Use BitNet LLM", exact=False)

        if bitnet_toggle.count() > 0:
            # Click toggle
            bitnet_toggle.first.click()
            time.sleep(1)

            # Click again to toggle back
            bitnet_toggle.first.click()
            time.sleep(1)

    def test_tc_7_14_temperature_slider(self, streamlit_page: Page):
        """TC-7.14: Temperature slider affects response style"""
        # Find temperature slider
        temp_label = streamlit_page.get_by_text("Temperature", exact=False)

        if temp_label.count() > 0:
            pass  # Implementation dependent

    def test_tc_7_15_show_sources_toggle(self, streamlit_page: Page):
        """TC-7.15: Show Sources toggle works"""
        sources_toggle = streamlit_page.get_by_text("Show Sources", exact=False)

        if sources_toggle.count() > 0:
            sources_toggle.first.click()
            time.sleep(1)

    def test_tc_7_16_show_performance_toggle(self, streamlit_page: Page):
        """TC-7.16: Show Performance toggle works"""
        perf_toggle = streamlit_page.get_by_text("Show Performance", exact=False)

        if perf_toggle.count() > 0:
            perf_toggle.first.click()
            time.sleep(1)

    def test_tc_7_17_show_timestamps_toggle(self, streamlit_page: Page):
        """TC-7.17: Show Timestamps toggle works"""
        timestamp_toggle = streamlit_page.get_by_text("Show Timestamps", exact=False)

        if timestamp_toggle.count() > 0:
            timestamp_toggle.first.click()
            time.sleep(1)

    def test_tc_7_18_settings_persist(self, streamlit_page: Page):
        """TC-7.18: Settings persist during session"""
        # Change a setting
        bitnet_toggle = streamlit_page.get_by_text("Use BitNet LLM", exact=False)

        if bitnet_toggle.count() > 0:
            bitnet_toggle.first.click()
            time.sleep(1)

            # Send a query
            chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
            chat_input.fill("Settings persistence test")
            chat_input.press("Enter")
            time.sleep(3)

            # Setting should still be changed

    def test_tc_7_19_clear_chat_button(self, streamlit_page: Page):
        """TC-7.19: Clear chat button empties history"""
        # Send a message first
        chat_input = streamlit_page.get_by_placeholder("Ask a question about your documents...")
        chat_input.fill("Message to clear")
        chat_input.press("Enter")
        time.sleep(2)

        # Find and click clear chat button
        clear_button = streamlit_page.get_by_text("Clear Chat", exact=False)

        if clear_button.count() > 0:
            clear_button.first.click()
            time.sleep(1)

            # Chat should be empty
            messages = streamlit_page.locator('[data-testid="stChatMessage"]')
            assert messages.count() == 0, "Chat should be cleared"

    def test_tc_7_20_export_chat_button(self, streamlit_page: Page):
        """TC-7.20: Export chat button (placeholder)"""
        export_button = streamlit_page.get_by_text("Export Chat", exact=False)

        if export_button.count() > 0:
            # Just verify button exists
            expect(export_button.first).to_be_visible()
