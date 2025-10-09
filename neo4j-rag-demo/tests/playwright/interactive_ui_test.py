#!/usr/bin/env python3
"""
Interactive UI Testing Script
Uses Playwright MCP Server for exploratory testing
Run with: python interactive_ui_test.py
"""

from playwright.sync_api import sync_playwright, Page
import time
import sys


class StreamlitUIExplorer:
    """Interactive UI explorer for Streamlit app"""

    def __init__(self, url="http://localhost:8501", headless=False):
        self.url = url
        self.headless = headless
        self.page = None
        self.browser = None
        self.context = None

    def start(self):
        """Start browser and navigate to app"""
        print("🚀 Starting Playwright UI Explorer...")
        print(f"   URL: {self.url}")
        print(f"   Headless: {self.headless}")
        print()

        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        self.page = self.context.new_page()

        print("📱 Navigating to Streamlit app...")
        self.page.goto(self.url)

        # Wait for app to load
        self.page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=30000)
        time.sleep(2)

        print("✅ Streamlit app loaded!")
        print()

    def explore_structure(self):
        """Explore and print UI structure"""
        print("=" * 60)
        print("🔍 UI STRUCTURE ANALYSIS")
        print("=" * 60)

        # Check title
        print("\n📋 TITLE:")
        titles = self.page.locator("h1, h2").all_text_contents()
        for title in titles[:3]:  # First 3 headings
            print(f"   • {title}")

        # Check sidebar
        print("\n📁 SIDEBAR:")
        sidebar = self.page.locator('[data-testid="stSidebar"]')
        if sidebar.count() > 0:
            print("   ✓ Sidebar present")
            # Get sidebar sections
            sidebar_text = sidebar.inner_text()
            lines = [line.strip() for line in sidebar_text.split('\n') if line.strip()]
            print("   Sections:")
            for line in lines[:10]:  # First 10 lines
                print(f"     - {line}")
        else:
            print("   ✗ No sidebar found")

        # Check chat input
        print("\n💬 CHAT INPUT:")
        chat_input = self.page.get_by_placeholder("Ask a question", exact=False)
        if chat_input.count() > 0:
            placeholder = chat_input.get_attribute("placeholder")
            print(f"   ✓ Chat input found")
            print(f"   Placeholder: {placeholder}")
        else:
            print("   ✗ No chat input found")

        # Check health cards
        print("\n🏥 HEALTH CARDS:")
        services = ["Neo4j", "RAG", "BitNet"]
        for service in services:
            service_elem = self.page.get_by_text(service, exact=False)
            if service_elem.count() > 0:
                print(f"   ✓ {service} card found")
            else:
                print(f"   ✗ {service} card not found")

        # Check sliders
        print("\n🎚️  CONTROLS:")
        sliders = self.page.locator('[data-testid="stSlider"]')
        print(f"   Sliders: {sliders.count()}")

        checkboxes = self.page.locator('input[type="checkbox"]')
        print(f"   Checkboxes: {checkboxes.count()}")

        file_input = self.page.locator('input[type="file"]')
        print(f"   File uploader: {'✓' if file_input.count() > 0 else '✗'}")

        print()

    def test_chat_interaction(self):
        """Test sending a chat message"""
        print("=" * 60)
        print("💬 CHAT INTERACTION TEST")
        print("=" * 60)

        chat_input = self.page.get_by_placeholder("Ask a question", exact=False)

        if chat_input.count() == 0:
            print("❌ Chat input not found!")
            return

        test_message = "Hello! This is a test message."
        print(f"\n📤 Sending message: '{test_message}'")

        # Send message
        chat_input.fill(test_message)
        chat_input.press("Enter")

        print("⏳ Waiting for response...")
        time.sleep(5)

        # Check if message appears
        message_elem = self.page.get_by_text(test_message, exact=False)
        if message_elem.count() > 0:
            print("✅ Message appeared in chat!")

            # Count total messages
            messages = self.page.locator('[data-testid="stChatMessage"]')
            print(f"   Total messages in chat: {messages.count()}")
        else:
            print("❌ Message did not appear")

        print()

    def test_file_upload_ui(self):
        """Test file upload UI components"""
        print("=" * 60)
        print("📤 FILE UPLOAD UI TEST")
        print("=" * 60)

        file_input = self.page.locator('input[type="file"]')

        if file_input.count() == 0:
            print("❌ File uploader not found!")
            return

        print("✅ File uploader found!")

        # Check for upload button (should appear after file selection)
        upload_button = self.page.get_by_text("Upload", exact=False)
        if upload_button.count() > 0:
            print("   Upload button present")
        else:
            print("   Upload button not visible (normal - appears after file selection)")

        print()

    def test_health_cards(self):
        """Test health card displays"""
        print("=" * 60)
        print("🏥 HEALTH CARDS TEST")
        print("=" * 60)

        services = {
            "Neo4j": "7687",
            "RAG": "8000",
            "BitNet": "8001"
        }

        page_content = self.page.content()

        for service, port in services.items():
            service_elem = self.page.get_by_text(service, exact=False)

            if service_elem.count() > 0:
                print(f"\n✅ {service} Health Card:")

                # Check for port number
                if port in page_content:
                    print(f"   Port {port}: ✓")
                else:
                    print(f"   Port {port}: Not displayed")

                # Check for status indicators
                status_indicators = ["healthy", "unhealthy", "✓", "✗", "offline"]
                found_status = [s for s in status_indicators if s in page_content]
                if found_status:
                    print(f"   Status indicators: {', '.join(found_status[:2])}")

            else:
                print(f"\n❌ {service} Health Card: Not found")

        print()

    def test_responsive_design(self):
        """Test responsive design at different viewports"""
        print("=" * 60)
        print("📱 RESPONSIVE DESIGN TEST")
        print("=" * 60)

        viewports = [
            ("Desktop", 1920, 1080),
            ("Laptop", 1366, 768),
            ("Tablet", 768, 1024),
            ("Mobile", 375, 667)
        ]

        for name, width, height in viewports:
            print(f"\n📐 Testing {name} ({width}x{height})...")
            self.page.set_viewport_size({"width": width, "height": height})
            time.sleep(1)

            # Check if main container is visible
            container = self.page.locator('[data-testid="stAppViewContainer"]')
            if container.is_visible():
                print(f"   ✅ App visible at {name} resolution")

                # Check sidebar (may be collapsed on mobile)
                sidebar = self.page.locator('[data-testid="stSidebar"]')
                if sidebar.is_visible():
                    print(f"   ✅ Sidebar visible")
                else:
                    print(f"   ℹ️  Sidebar hidden (normal for mobile)")
            else:
                print(f"   ❌ App not properly visible")

        # Restore desktop size
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        print()

    def take_screenshot(self, filename="ui_screenshot.png"):
        """Take a screenshot of current state"""
        print(f"📸 Taking screenshot: {filename}")
        self.page.screenshot(path=filename, full_page=True)
        print(f"   ✅ Screenshot saved!")
        print()

    def interactive_mode(self):
        """Interactive mode - keep browser open"""
        print("=" * 60)
        print("🎮 INTERACTIVE MODE")
        print("=" * 60)
        print()
        print("Browser is now open for manual exploration.")
        print("Press Ctrl+C to exit and close browser.")
        print()

        try:
            # Keep browser open
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n\n👋 Closing browser...")

    def run_all_tests(self):
        """Run all automated tests"""
        self.explore_structure()
        self.test_health_cards()
        self.test_chat_interaction()
        self.test_file_upload_ui()
        self.test_responsive_design()
        self.take_screenshot()

    def cleanup(self):
        """Close browser"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Interactive Streamlit UI Testing")
    parser.add_argument("--url", default="http://localhost:8501", help="Streamlit URL")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--interactive", action="store_true", help="Keep browser open for manual testing")
    parser.add_argument("--screenshot", help="Take screenshot and save to file")

    args = parser.parse_args()

    explorer = StreamlitUIExplorer(url=args.url, headless=args.headless)

    try:
        explorer.start()

        if args.screenshot:
            explorer.take_screenshot(args.screenshot)
        elif args.interactive:
            explorer.explore_structure()
            explorer.interactive_mode()
        else:
            explorer.run_all_tests()

        print("=" * 60)
        print("✅ UI TESTING COMPLETE")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
    finally:
        explorer.cleanup()


if __name__ == "__main__":
    main()
