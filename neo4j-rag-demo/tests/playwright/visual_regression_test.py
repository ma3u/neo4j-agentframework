#!/usr/bin/env python3
"""
Visual Regression Testing
Captures screenshots and compares UI changes over time
Run with: python visual_regression_test.py
"""

from playwright.sync_api import sync_playwright, Page
import os
import time
from PIL import Image, ImageChops, ImageDraw
from pathlib import Path


class VisualRegressionTester:
    """Visual regression testing for Streamlit UI"""

    def __init__(self, url="http://localhost:8501", baseline_dir="baseline_screenshots", test_dir="test_screenshots"):
        self.url = url
        self.baseline_dir = Path(baseline_dir)
        self.test_dir = Path(test_dir)
        self.diff_dir = Path("diff_screenshots")

        # Create directories
        self.baseline_dir.mkdir(exist_ok=True)
        self.test_dir.mkdir(exist_ok=True)
        self.diff_dir.mkdir(exist_ok=True)

        self.page = None
        self.browser = None
        self.context = None

    def start_browser(self):
        """Start Playwright browser"""
        print("🚀 Starting Visual Regression Testing...")
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=True)
        self.context = self.browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        self.page = self.context.new_page()

        print(f"📱 Navigating to {self.url}...")
        self.page.goto(self.url)
        self.page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=30000)
        time.sleep(3)  # Wait for all components to load
        print("✅ App loaded!\n")

    def capture_baseline(self):
        """Capture baseline screenshots"""
        print("=" * 60)
        print("📸 CAPTURING BASELINE SCREENSHOTS")
        print("=" * 60)
        print()

        screenshots = self._capture_all_views()

        for name, path in screenshots.items():
            baseline_path = self.baseline_dir / path.name
            # Copy to baseline directory
            import shutil
            shutil.copy(path, baseline_path)
            print(f"   ✅ Baseline saved: {baseline_path.name}")

        print(f"\n✅ {len(screenshots)} baseline screenshots captured!")
        print()

    def capture_test(self):
        """Capture test screenshots"""
        print("=" * 60)
        print("📸 CAPTURING TEST SCREENSHOTS")
        print("=" * 60)
        print()

        screenshots = self._capture_all_views()

        for name, path in screenshots.items():
            print(f"   ✅ Test captured: {path.name}")

        print(f"\n✅ {len(screenshots)} test screenshots captured!")
        print()

    def _capture_all_views(self):
        """Capture screenshots of all views"""
        screenshots = {}

        # 1. Full page
        print("   📄 Full page...")
        full_path = self.test_dir / "01_full_page.png"
        self.page.screenshot(path=str(full_path), full_page=True)
        screenshots["full_page"] = full_path

        # 2. Header only
        print("   📋 Header...")
        header_path = self.test_dir / "02_header.png"
        header = self.page.locator("h1, h2").first
        if header.count() > 0:
            header.screenshot(path=str(header_path))
            screenshots["header"] = header_path

        # 3. Health cards
        print("   🏥 Health cards...")
        health_path = self.test_dir / "03_health_cards.png"
        # Take screenshot of area with health cards
        self.page.locator('[data-testid="stAppViewContainer"]').first.screenshot(
            path=str(health_path)
        )
        screenshots["health_cards"] = health_path

        # 4. Chat interface
        print("   💬 Chat interface...")
        chat_path = self.test_dir / "04_chat.png"
        chat_input = self.page.get_by_placeholder("Ask a question", exact=False)
        if chat_input.count() > 0:
            chat_input.screenshot(path=str(chat_path))
            screenshots["chat"] = chat_path

        # 5. Sidebar
        print("   📁 Sidebar...")
        sidebar_path = self.test_dir / "05_sidebar.png"
        sidebar = self.page.locator('[data-testid="stSidebar"]')
        if sidebar.count() > 0:
            sidebar.screenshot(path=str(sidebar_path))
            screenshots["sidebar"] = sidebar_path

        # 6. Mobile view
        print("   📱 Mobile view...")
        self.page.set_viewport_size({"width": 375, "height": 667})
        time.sleep(1)
        mobile_path = self.test_dir / "06_mobile.png"
        self.page.screenshot(path=str(mobile_path), full_page=True)
        screenshots["mobile"] = mobile_path

        # Restore desktop view
        self.page.set_viewport_size({"width": 1920, "height": 1080})
        time.sleep(1)

        return screenshots

    def compare_screenshots(self):
        """Compare baseline and test screenshots"""
        print("=" * 60)
        print("🔍 COMPARING SCREENSHOTS")
        print("=" * 60)
        print()

        if not list(self.baseline_dir.glob("*.png")):
            print("❌ No baseline screenshots found!")
            print("   Run with --baseline first to create baseline")
            return False

        differences_found = False
        results = []

        for baseline_file in sorted(self.baseline_dir.glob("*.png")):
            test_file = self.test_dir / baseline_file.name

            if not test_file.exists():
                print(f"⚠️  Missing test screenshot: {baseline_file.name}")
                continue

            print(f"   Comparing {baseline_file.name}...")

            # Compare images
            diff_percent = self._compare_images(baseline_file, test_file)

            if diff_percent > 1.0:  # More than 1% difference
                differences_found = True
                status = "❌ DIFFERENT"
                print(f"      {status} ({diff_percent:.2f}% difference)")
            elif diff_percent > 0.1:
                status = "⚠️  MINOR DIFF"
                print(f"      {status} ({diff_percent:.2f}% difference)")
            else:
                status = "✅ MATCH"
                print(f"      {status}")

            results.append({
                "file": baseline_file.name,
                "status": status,
                "diff_percent": diff_percent
            })

        print()
        print("=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)

        for result in results:
            print(f"   {result['status']:<15} {result['file']:<30} ({result['diff_percent']:.2f}%)")

        print()

        if differences_found:
            print("⚠️  Visual changes detected!")
            print(f"   See diff images in: {self.diff_dir}/")
            return False
        else:
            print("✅ No significant visual changes!")
            return True

    def _compare_images(self, baseline_path, test_path):
        """Compare two images and return difference percentage"""
        # Open images
        baseline = Image.open(baseline_path).convert('RGB')
        test = Image.open(test_path).convert('RGB')

        # Resize if dimensions don't match
        if baseline.size != test.size:
            test = test.resize(baseline.size, Image.Resampling.LANCZOS)

        # Calculate difference
        diff = ImageChops.difference(baseline, test)

        # Create diff image with highlighted changes
        diff_path = self.diff_dir / f"diff_{baseline_path.name}"
        diff_highlighted = diff.copy()

        # Enhance differences for visibility
        diff_enhanced = Image.new('RGB', diff.size)
        pixels = diff.load()
        enhanced_pixels = diff_enhanced.load()

        different_pixels = 0
        total_pixels = diff.size[0] * diff.size[1]

        for y in range(diff.size[1]):
            for x in range(diff.size[0]):
                r, g, b = pixels[x, y]
                # If any channel differs significantly
                if max(r, g, b) > 10:
                    different_pixels += 1
                    # Highlight in red
                    enhanced_pixels[x, y] = (255, 0, 0)
                else:
                    enhanced_pixels[x, y] = (r, g, b)

        # Save diff image
        diff_enhanced.save(diff_path)

        # Calculate percentage
        diff_percent = (different_pixels / total_pixels) * 100

        return diff_percent

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

    parser = argparse.ArgumentParser(description="Visual Regression Testing")
    parser.add_argument("--url", default="http://localhost:8501", help="Streamlit URL")
    parser.add_argument("--baseline", action="store_true", help="Capture baseline screenshots")
    parser.add_argument("--compare", action="store_true", help="Compare against baseline")

    args = parser.parse_args()

    tester = VisualRegressionTester(url=args.url)

    try:
        tester.start_browser()

        if args.baseline:
            tester.capture_baseline()
            print("✅ Baseline screenshots captured!")
            print("   Run with --compare to test for visual changes")

        elif args.compare:
            tester.capture_test()
            success = tester.compare_screenshots()

            if success:
                print("\n✅ VISUAL REGRESSION TEST PASSED")
                return 0
            else:
                print("\n⚠️  VISUAL REGRESSION TEST FAILED")
                return 1

        else:
            # Default: capture test screenshots
            tester.capture_test()
            print("✅ Test screenshots captured!")
            print("   Use --baseline to set baseline")
            print("   Use --compare to compare against baseline")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

    finally:
        tester.cleanup()

    return 0


if __name__ == "__main__":
    exit(main())
