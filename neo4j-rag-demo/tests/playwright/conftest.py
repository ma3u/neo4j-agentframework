"""
Playwright Test Configuration for Issue #12
Comprehensive test suite for Streamlit Chat UI
"""

import pytest
from playwright.sync_api import Page, expect, Browser
import time
import os

# Test configuration
BASE_URL = os.getenv("STREAMLIT_URL", "http://localhost:8501")
RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8000")
TIMEOUT = 30000  # 30 seconds


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Playwright Testing"
    }


@pytest.fixture
def streamlit_page(page: Page):
    """Navigate to Streamlit app and wait for it to load"""
    page.goto(BASE_URL)

    # Wait for Streamlit to be ready
    page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=TIMEOUT)

    # Wait for initial render
    time.sleep(2)

    return page


@pytest.fixture
def test_files_dir():
    """Directory containing test files"""
    base_dir = os.path.dirname(os.path.dirname(__file__))
    test_files = os.path.join(base_dir, "test_files")
    os.makedirs(test_files, exist_ok=True)
    return test_files


@pytest.fixture
def create_test_pdf(test_files_dir):
    """Create a test PDF file"""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter

    def _create_pdf(filename: str, size_kb: int = 100, content: str = None):
        filepath = os.path.join(test_files_dir, filename)
        c = canvas.Canvas(filepath, pagesize=letter)

        # Add content
        if content:
            c.drawString(100, 750, content)
        else:
            c.drawString(100, 750, f"Test PDF: {filename}")
            c.drawString(100, 730, "This is a test document for Neo4j RAG system.")
            c.drawString(100, 710, f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        # Add more pages if needed to reach target size
        pages_needed = max(1, size_kb // 10)
        for i in range(pages_needed):
            if i > 0:
                c.showPage()
            c.drawString(100, 750, f"Page {i+1} of {pages_needed}")
            for j in range(20):
                c.drawString(100, 700 - j*20, f"Content line {j+1} " * 10)

        c.save()
        return filepath

    return _create_pdf


@pytest.fixture
def create_test_txt(test_files_dir):
    """Create a test TXT file"""
    def _create_txt(filename: str, content: str = None):
        filepath = os.path.join(test_files_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            if content:
                f.write(content)
            else:
                f.write(f"Test TXT file: {filename}\n")
                f.write(f"Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("This is a test document for Neo4j RAG system.\n")
        return filepath

    return _create_txt


def expect_element_visible(page: Page, selector: str, timeout: int = TIMEOUT):
    """Helper to check element visibility with custom timeout"""
    expect(page.locator(selector)).to_be_visible(timeout=timeout)


def wait_for_streamlit_rerun(page: Page):
    """Wait for Streamlit to complete a rerun"""
    # Wait for spinner to appear and disappear
    try:
        page.wait_for_selector('[data-testid="stSpinner"]', timeout=1000)
        page.wait_for_selector('[data-testid="stSpinner"]', state="hidden", timeout=TIMEOUT)
    except:
        # No spinner appeared, wait briefly for rerun
        time.sleep(0.5)
