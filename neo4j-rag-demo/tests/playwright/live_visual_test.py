#!/usr/bin/env python3
"""
Live Visual Testing - Compare UI Against Mockup
Run with browser visible to manually verify each component
"""

from playwright.sync_api import sync_playwright, Page
import time
import json
from datetime import datetime


class LiveVisualTester:
    """Interactive visual testing with browser visible"""

    def __init__(self):
        self.url = "http://localhost:8501"
        self.mockup_url = "https://ma3u.github.io/neo4j-agentframework/"
        self.results = {
            "test_date": datetime.now().isoformat(),
            "streamlit_url": self.url,
            "mockup_url": self.mockup_url,
            "components": []
        }

    def run_tests(self):
        """Run visual tests with browser visible"""
        print("=" * 70)
        print("🎨 LIVE VISUAL TESTING - Streamlit vs Mockup")
        print("=" * 70)
        print()
        print("Browser will open showing:")
        print(f"  LEFT:  Streamlit App ({self.url})")
        print(f"  RIGHT: Mockup Reference ({self.mockup_url})")
        print()
        print("Press Enter after each test to continue...")
        print()

        with sync_playwright() as p:
            # Launch browser in headed mode
            browser = p.chromium.launch(
                headless=False,
                slow_mo=500  # Slow down actions for visibility
            )

            # Create context with larger viewport
            context = browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )

            # Open Streamlit page
            streamlit_page = context.new_page()
            print("📱 Opening Streamlit app...")
            streamlit_page.goto(self.url)
            streamlit_page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=30000)
            time.sleep(3)

            # Open mockup in new tab for reference
            mockup_page = context.new_page()
            print("📱 Opening mockup reference...")
            mockup_page.goto(self.mockup_url)
            time.sleep(2)

            # Arrange windows side by side
            print("✅ Both pages loaded!")
            print()

            try:
                # Test 1: Header and Title
                self._test_header(streamlit_page)

                # Test 2: Health Cards
                self._test_health_cards(streamlit_page)

                # Test 3: Chat Interface
                self._test_chat_interface(streamlit_page)

                # Test 4: Sidebar Controls
                self._test_sidebar(streamlit_page)

                # Test 5: Stats Display
                self._test_stats(streamlit_page)

                # Test 6: File Upload
                self._test_file_upload(streamlit_page)

                # Test 7: Colors and Theme
                self._test_theme(streamlit_page)

                # Test 8: Responsive Design
                self._test_responsive(streamlit_page)

                # Generate Report
                self._generate_report()

            except KeyboardInterrupt:
                print("\n\n⚠️  Testing interrupted by user")

            finally:
                print("\n\n👋 Closing browser...")
                browser.close()

    def _test_header(self, page: Page):
        """Test 1: Header and Title"""
        print("=" * 70)
        print("TEST 1: HEADER AND TITLE")
        print("=" * 70)
        print()
        print("🔍 Checking:")
        print("   ✓ Title: 'Neo4j RAG + BitNet Chat'")
        print("   ✓ Developer mode indicator: '(local developer mode)'")
        print("   ✓ Header styling and positioning")
        print()

        # Highlight header
        page.evaluate("""
            const headers = document.querySelectorAll('h1, h2');
            headers.forEach(h => {
                h.style.border = '3px solid #00ff00';
                h.style.padding = '10px';
            });
        """)

        result = {
            "component": "Header & Title",
            "checks": []
        }

        # Check title
        title = page.get_by_text("Neo4j RAG + BitNet", exact=False)
        if title.count() > 0:
            print("   ✅ Title found")
            result["checks"].append({"item": "Title text", "status": "PASS"})
        else:
            print("   ❌ Title not found")
            result["checks"].append({"item": "Title text", "status": "FAIL"})

        # Check dev mode
        dev_mode = page.get_by_text("local developer mode", exact=False)
        if dev_mode.count() > 0:
            print("   ✅ Developer mode indicator found")
            result["checks"].append({"item": "Dev mode indicator", "status": "PASS"})
        else:
            print("   ⚠️  Developer mode indicator not found")
            result["checks"].append({"item": "Dev mode indicator", "status": "WARN"})

        self.results["components"].append(result)

        print()
        input("📸 Compare header with mockup, then press Enter...")
        print()

    def _test_health_cards(self, page: Page):
        """Test 2: Health Cards"""
        print("=" * 70)
        print("TEST 2: HEALTH CARDS")
        print("=" * 70)
        print()
        print("🔍 Checking:")
        print("   ✓ Neo4j health card")
        print("   ✓ RAG Service health card")
        print("   ✓ BitNet LLM health card")
        print("   ✓ Status indicators (green/red/yellow)")
        print("   ✓ Response times displayed")
        print()

        result = {
            "component": "Health Cards",
            "checks": []
        }

        services = ["Neo4j", "RAG", "BitNet"]
        for service in services:
            service_elem = page.get_by_text(service, exact=False)
            if service_elem.count() > 0:
                print(f"   ✅ {service} card found")
                result["checks"].append({"item": f"{service} card", "status": "PASS"})
            else:
                print(f"   ❌ {service} card not found")
                result["checks"].append({"item": f"{service} card", "status": "FAIL"})

        self.results["components"].append(result)

        print()
        input("📸 Compare health cards layout with mockup, then press Enter...")
        print()

    def _test_chat_interface(self, page: Page):
        """Test 3: Chat Interface"""
        print("=" * 70)
        print("TEST 3: CHAT INTERFACE")
        print("=" * 70)
        print()
        print("🔍 Checking:")
        print("   ✓ Chat input field")
        print("   ✓ Placeholder text")
        print("   ✓ Message display area")
        print("   ✓ Send message functionality")
        print()

        result = {
            "component": "Chat Interface",
            "checks": []
        }

        # Highlight chat input
        page.evaluate("""
            const chatInput = document.querySelector('[data-testid="stChatInput"]');
            if (chatInput) {
                chatInput.style.border = '3px solid #00ff00';
            }
        """)

        # Check chat input
        chat_input = page.get_by_placeholder("Ask a question", exact=False)
        if chat_input.count() > 0:
            print("   ✅ Chat input found")
            placeholder = chat_input.get_attribute("placeholder")
            print(f"      Placeholder: '{placeholder}'")
            result["checks"].append({"item": "Chat input", "status": "PASS"})

            # Test sending a message
            print()
            print("   📤 Testing message send...")
            test_msg = "Visual test message"
            chat_input.fill(test_msg)
            chat_input.press("Enter")
            time.sleep(3)

            msg_elem = page.get_by_text(test_msg, exact=False)
            if msg_elem.count() > 0:
                print("   ✅ Message appeared in chat")
                result["checks"].append({"item": "Send message", "status": "PASS"})
            else:
                print("   ❌ Message did not appear")
                result["checks"].append({"item": "Send message", "status": "FAIL"})
        else:
            print("   ❌ Chat input not found")
            result["checks"].append({"item": "Chat input", "status": "FAIL"})

        self.results["components"].append(result)

        print()
        input("📸 Compare chat interface with mockup, then press Enter...")
        print()

    def _test_sidebar(self, page: Page):
        """Test 4: Sidebar Controls"""
        print("=" * 70)
        print("TEST 4: SIDEBAR CONTROLS")
        print("=" * 70)
        print()
        print("🔍 Checking:")
        print("   ✓ Sidebar visibility")
        print("   ✓ RAG Configuration section")
        print("   ✓ LLM Configuration section")
        print("   ✓ Document Upload section")
        print("   ✓ Sliders and toggles")
        print()

        result = {
            "component": "Sidebar",
            "checks": []
        }

        # Check sidebar
        sidebar = page.locator('[data-testid="stSidebar"]')
        if sidebar.is_visible():
            print("   ✅ Sidebar visible")
            result["checks"].append({"item": "Sidebar visibility", "status": "PASS"})

            # Count controls
            sliders = page.locator('[data-testid="stSlider"]')
            checkboxes = page.locator('input[type="checkbox"]')

            print(f"   ✅ Found {sliders.count()} sliders")
            print(f"   ✅ Found {checkboxes.count()} checkboxes")

            result["checks"].append({"item": f"{sliders.count()} sliders", "status": "PASS"})
            result["checks"].append({"item": f"{checkboxes.count()} checkboxes", "status": "PASS"})
        else:
            print("   ❌ Sidebar not visible")
            result["checks"].append({"item": "Sidebar visibility", "status": "FAIL"})

        self.results["components"].append(result)

        print()
        input("📸 Compare sidebar with mockup, then press Enter...")
        print()

    def _test_stats(self, page: Page):
        """Test 5: Stats Display"""
        print("=" * 70)
        print("TEST 5: STATISTICS DISPLAY")
        print("=" * 70)
        print()
        print("🔍 Checking:")
        print("   ✓ Compact stats below chat")
        print("   ✓ Document count")
        print("   ✓ Chunk count")
        print("   ✓ Response time")
        print("   ✓ Memory usage")
        print()

        result = {
            "component": "Statistics",
            "checks": []
        }

        page_content = page.content()

        stats_keywords = ["Documents", "Chunks", "Response Time", "Memory"]
        found_stats = []

        for stat in stats_keywords:
            if stat in page_content:
                found_stats.append(stat)
                print(f"   ✅ {stat} stat found")
                result["checks"].append({"item": stat, "status": "PASS"})
            else:
                print(f"   ⚠️  {stat} stat not found")
                result["checks"].append({"item": stat, "status": "WARN"})

        self.results["components"].append(result)

        print()
        input("📸 Compare stats display with mockup, then press Enter...")
        print()

    def _test_file_upload(self, page: Page):
        """Test 6: File Upload"""
        print("=" * 70)
        print("TEST 6: FILE UPLOAD")
        print("=" * 70)
        print()
        print("🔍 Checking:")
        print("   ✓ File uploader component")
        print("   ✓ Accepted file types (PDF, TXT, MD, DOCX)")
        print("   ✓ Upload button")
        print()

        result = {
            "component": "File Upload",
            "checks": []
        }

        file_input = page.locator('input[type="file"]')
        if file_input.count() > 0:
            print("   ✅ File uploader found")
            result["checks"].append({"item": "File uploader", "status": "PASS"})
        else:
            print("   ❌ File uploader not found")
            result["checks"].append({"item": "File uploader", "status": "FAIL"})

        self.results["components"].append(result)

        print()
        input("📸 Compare file upload section with mockup, then press Enter...")
        print()

    def _test_theme(self, page: Page):
        """Test 7: Colors and Theme"""
        print("=" * 70)
        print("TEST 7: COLORS AND THEME")
        print("=" * 70)
        print()
        print("🔍 Checking:")
        print("   ✓ Dark theme colors")
        print("   ✓ Background: #0E1117")
        print("   ✓ Secondary: #262730")
        print("   ✓ Accent: #FF4B4B")
        print()

        result = {
            "component": "Theme",
            "checks": [
                {"item": "Dark theme", "status": "VISUAL_CHECK"},
                {"item": "Color scheme", "status": "VISUAL_CHECK"}
            ]
        }

        self.results["components"].append(result)

        print()
        print("   ℹ️  Visual verification required")
        print("   Compare background, text, and accent colors")
        print()
        input("📸 Verify colors match mockup, then press Enter...")
        print()

    def _test_responsive(self, page: Page):
        """Test 8: Responsive Design"""
        print("=" * 70)
        print("TEST 8: RESPONSIVE DESIGN")
        print("=" * 70)
        print()

        result = {
            "component": "Responsive Design",
            "checks": []
        }

        viewports = [
            ("Desktop", 1920, 1080),
            ("Laptop", 1366, 768),
            ("Tablet", 768, 1024),
            ("Mobile", 375, 667)
        ]

        for name, width, height in viewports:
            print(f"   Testing {name} ({width}x{height})...")
            page.set_viewport_size({"width": width, "height": height})
            time.sleep(2)

            container = page.locator('[data-testid="stAppViewContainer"]')
            if container.is_visible():
                print(f"   ✅ {name} layout working")
                result["checks"].append({"item": f"{name} layout", "status": "PASS"})
            else:
                print(f"   ❌ {name} layout broken")
                result["checks"].append({"item": f"{name} layout", "status": "FAIL"})

            if name == "Mobile":
                input(f"   📸 Verify {name} layout, then press Enter...")

        # Restore desktop
        page.set_viewport_size({"width": 1920, "height": 1080})

        self.results["components"].append(result)
        print()

    def _generate_report(self):
        """Generate final test report"""
        print()
        print("=" * 70)
        print("📊 VISUAL TEST REPORT")
        print("=" * 70)
        print()

        total_checks = 0
        passed = 0
        failed = 0
        warnings = 0

        for component in self.results["components"]:
            print(f"\n📦 {component['component']}")
            print("-" * 50)

            for check in component["checks"]:
                total_checks += 1
                status_icon = ""

                if check["status"] == "PASS":
                    status_icon = "✅"
                    passed += 1
                elif check["status"] == "FAIL":
                    status_icon = "❌"
                    failed += 1
                elif check["status"] == "WARN":
                    status_icon = "⚠️ "
                    warnings += 1
                else:
                    status_icon = "ℹ️ "

                print(f"   {status_icon} {check['item']}: {check['status']}")

        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"   Total Checks: {total_checks}")
        print(f"   ✅ Passed: {passed}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⚠️  Warnings: {warnings}")
        print()

        if failed == 0:
            print("🎉 ALL TESTS PASSED!")
        else:
            print(f"⚠️  {failed} test(s) failed - review needed")

        # Save report
        report_file = "visual_test_report.json"
        with open(report_file, 'w') as f:
            json.dump(self.results, f, indent=2)

        print()
        print(f"📄 Report saved: {report_file}")
        print()


def main():
    """Main entry point"""
    tester = LiveVisualTester()

    try:
        tester.run_tests()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
