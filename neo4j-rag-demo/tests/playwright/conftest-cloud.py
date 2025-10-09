"""
Playwright Test Configuration for Cloud Testing
Tests local Streamlit UI or direct cloud endpoints
"""

import pytest
from playwright.sync_api import Page, expect
import time
import os

# Cloud configuration
CLOUD_MODE = os.getenv("TEST_MODE", "local") == "cloud"
RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8000")
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
STREAMLIT_URL = os.getenv("STREAMLIT_URL", "http://localhost:8501")

# Timeout for cloud services (longer than local)
TIMEOUT = 60000 if CLOUD_MODE else 30000

print(f"Test Configuration:")
print(f"  Mode: {'CLOUD' if CLOUD_MODE else 'LOCAL'}")
print(f"  RAG API: {RAG_API_URL}")
print(f"  Neo4j: {NEO4J_URI}")
print(f"  Streamlit: {STREAMLIT_URL}")
print(f"  Timeout: {TIMEOUT}ms")


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context with cloud-friendly settings"""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Playwright Cloud Testing",
        # Ignore HTTPS certificate errors for self-signed certs (dev only)
        "ignore_https_errors": CLOUD_MODE,
    }


@pytest.fixture
def streamlit_page(page: Page):
    """Navigate to Streamlit app (local) or cloud service"""
    page.goto(STREAMLIT_URL)

    # Wait for Streamlit to be ready
    page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=TIMEOUT)

    # Wait for initial render (longer for cloud)
    time.sleep(5 if CLOUD_MODE else 2)

    return page


@pytest.fixture
def cloud_rag_api():
    """Direct access to cloud RAG API for testing"""
    import requests

    class CloudRAGClient:
        def __init__(self):
            self.base_url = RAG_API_URL
            self.timeout = 30 if CLOUD_MODE else 10

        def health(self):
            """Check RAG service health"""
            response = requests.get(f"{self.base_url}/health", timeout=self.timeout)
            return response.json()

        def query(self, question: str, **kwargs):
            """Query RAG service"""
            payload = {
                "question": question,
                "max_results": kwargs.get("max_results", 5),
                "similarity_threshold": kwargs.get("similarity_threshold", 0.7),
                "use_llm": kwargs.get("use_llm", False)  # Skip LLM for faster tests
            }
            response = requests.post(
                f"{self.base_url}/query",
                json=payload,
                timeout=self.timeout
            )
            return response.json()

        def upload_document(self, content: str, metadata: dict = None):
            """Upload document to RAG service"""
            payload = {
                "content": content,
                "metadata": metadata or {}
            }
            response = requests.post(
                f"{self.base_url}/documents",
                json=payload,
                timeout=self.timeout
            )
            return response.json()

        def stats(self):
            """Get RAG service statistics"""
            response = requests.get(f"{self.base_url}/stats", timeout=self.timeout)
            return response.json()

    return CloudRAGClient()


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
            c.drawString(100, 730, "Cloud Testing - Neo4j RAG System")
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
                f.write("Cloud Testing - Neo4j RAG System\n")
        return filepath

    return _create_txt


def expect_element_visible(page: Page, selector: str, timeout: int = TIMEOUT):
    """Helper to check element visibility with cloud timeout"""
    expect(page.locator(selector)).to_be_visible(timeout=timeout)


def wait_for_streamlit_rerun(page: Page):
    """Wait for Streamlit to complete a rerun (cloud-aware)"""
    try:
        page.wait_for_selector('[data-testid="stSpinner"]', timeout=2000)
        page.wait_for_selector('[data-testid="stSpinner"]', state="hidden", timeout=TIMEOUT)
    except:
        # No spinner appeared, wait briefly for rerun
        time.sleep(2 if CLOUD_MODE else 0.5)


# Cloud-specific pytest markers
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "cloud: mark test as cloud-only (requires cloud services)"
    )
    config.addinivalue_line(
        "markers", "local: mark test as local-only"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running (>30s)"
    )


def pytest_collection_modifyitems(config, items):
    """Skip tests based on environment"""
    skip_cloud = pytest.mark.skip(reason="Cloud mode required (set TEST_MODE=cloud)")
    skip_local = pytest.mark.skip(reason="Local mode required")

    for item in items:
        if "cloud" in item.keywords and not CLOUD_MODE:
            item.add_marker(skip_cloud)
        if "local" in item.keywords and CLOUD_MODE:
            item.add_marker(skip_local)


# Cloud health check before tests
@pytest.fixture(scope="session", autouse=True)
def verify_cloud_services():
    """Verify cloud services are reachable before running tests"""
    if not CLOUD_MODE:
        return

    import requests

    print("\n=== Verifying Cloud Services ===")

    services = {
        "RAG Service": f"{RAG_API_URL}/health",
    }

    all_healthy = True
    for name, url in services.items():
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✓ {name}: Healthy")
            else:
                print(f"✗ {name}: Unhealthy (status {response.status_code})")
                all_healthy = False
        except Exception as e:
            print(f"✗ {name}: Unreachable ({str(e)[:50]})")
            all_healthy = False

    if not all_healthy:
        pytest.exit("Cloud services not healthy. Aborting tests.")

    print("=== All Cloud Services Healthy ===\n")
