# Local Testing Discussion: Streamlit Chat UI for Neo4j RAG + BitNet

## Testing Approach Overview

This document discusses the comprehensive local testing strategy for the Streamlit Chat UI that interfaces with our Neo4j RAG system and BitNet LLM. The testing approach focuses on ensuring robust functionality, optimal performance, and excellent user experience.

## Testing Environment Architecture

### Local Stack Setup
```
┌─────────────────────────────────────────────┐
│         Testing Environment                 │
├─────────────────────────────────────────────┤
│ 🌐 Streamlit App (Port 8501)               │
│    ├─ Chat Interface                        │
│    ├─ Document Upload                       │
│    └─ System Monitoring                     │
├─────────────────────────────────────────────┤
│ 🔄 RAG Service (Port 8000)                 │
│    ├─ /query (Chat queries)                │
│    ├─ /upload (Document processing)        │
│    ├─ /health (System status)              │
│    └─ /stats (Performance metrics)         │
├─────────────────────────────────────────────┤
│ 🤖 BitNet LLM (Port 8001)                  │
│    ├─ /generate (Text generation)          │
│    └─ /health (Model status)               │
├─────────────────────────────────────────────┤
│ 🗃️  Neo4j Database (Ports 7474/7687)       │
│    ├─ Graph Browser (7474)                 │
│    └─ Bolt Protocol (7687)                 │
└─────────────────────────────────────────────┘
```

## Testing Strategy

### 1. Unit Testing

#### Streamlit Components Testing
```python
# tests/test_streamlit_components.py
import pytest
import streamlit as st
from unittest.mock import patch, MagicMock
import sys
sys.path.append('../')
from streamlit_chat_app import query_rag_system, stream_response, render_system_stats

class TestStreamlitComponents:
    
    def test_query_rag_system_success(self):
        """Test successful RAG system query"""
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "answer": "Neo4j is a graph database",
                "sources": [{"source": "test.pdf", "score": 0.9}],
                "processing_time": 0.045
            }
            mock_response.status_code = 200
            mock_post.return_value = mock_response
            
            result = query_rag_system("What is Neo4j?")
            
            assert result["answer"] == "Neo4j is a graph database"
            assert len(result["sources"]) == 1
            assert result["sources"][0]["score"] == 0.9
    
    def test_query_rag_system_failure(self):
        """Test RAG system query failure handling"""
        with patch('requests.post', side_effect=requests.RequestException("Connection error")):
            result = query_rag_system("What is Neo4j?")
            
            assert "Sorry, I'm having trouble" in result["answer"]
            assert result["sources"] == []
    
    def test_stream_response_generator(self):
        """Test response streaming functionality"""
        test_text = "This is a test response"
        
        # Mock streamlit placeholder
        placeholder = MagicMock()
        
        stream_response(test_text, placeholder)
        
        # Verify write_stream was called
        placeholder.write_stream.assert_called_once()
```

#### RAG Integration Testing
```python
# tests/test_rag_integration.py
import pytest
import requests
import time

class TestRAGIntegration:
    
    @pytest.fixture(autouse=True)
    def setup_services(self):
        """Ensure all services are running before tests"""
        services = [
            ("http://localhost:8000/health", "RAG Service"),
            ("http://localhost:8001/health", "BitNet Service"),
            ("http://localhost:7474", "Neo4j Browser")
        ]
        
        for url, service in services:
            try:
                response = requests.get(url, timeout=5)
                assert response.status_code == 200, f"{service} not available"
            except requests.RequestException:
                pytest.skip(f"{service} not running")
    
    def test_end_to_end_query_flow(self):
        """Test complete query flow from Streamlit to Neo4j"""
        # 1. Test knowledge base has data
        stats_response = requests.get("http://localhost:8000/stats")
        stats = stats_response.json()
        assert stats["documents"] > 0, "No documents in knowledge base"
        
        # 2. Test query processing
        query_payload = {
            "question": "What is a graph database?",
            "k": 3
        }
        
        start_time = time.time()
        response = requests.post("http://localhost:8000/query", json=query_payload)
        end_time = time.time()
        
        # 3. Verify response structure
        result = response.json()
        assert "answer" in result
        assert "sources" in result
        assert len(result["sources"]) <= 3
        
        # 4. Verify performance
        processing_time = end_time - start_time
        assert processing_time < 2.0, f"Query too slow: {processing_time}s"
        
        # 5. Verify source quality
        for source in result["sources"]:
            assert "text" in source
            assert "score" in source
            assert 0 <= source["score"] <= 1
    
    def test_document_upload_flow(self):
        """Test document upload functionality"""
        # Create test document
        test_content = "This is a test document about graph databases and Neo4j."
        
        files = {
            "file": ("test_doc.txt", test_content, "text/plain")
        }
        
        # Upload document
        upload_response = requests.post("http://localhost:8000/upload", files=files)
        assert upload_response.status_code == 200
        
        # Verify document was processed
        time.sleep(2)  # Allow processing time
        
        # Query for the uploaded content
        query_response = requests.post(
            "http://localhost:8000/query",
            json={"question": "test document graph databases", "k": 5}
        )
        
        result = query_response.json()
        
        # Check if our content appears in results
        found_content = any(
            "test document" in source["text"].lower() 
            for source in result["sources"]
        )
        assert found_content, "Uploaded document not found in search results"
```

### 2. Integration Testing

#### Multi-Service Integration Tests
```python
# tests/test_integration.py
import pytest
import requests
import concurrent.futures
import time

class TestIntegration:
    
    def test_concurrent_queries(self):
        """Test system under concurrent load"""
        def make_query(question):
            response = requests.post(
                "http://localhost:8000/query",
                json={"question": question, "k": 3},
                timeout=10
            )
            return response.status_code, response.json()
        
        questions = [
            "What is Neo4j?",
            "How does graph database work?",
            "What are the benefits of Neo4j?",
            "Explain Cypher query language",
            "What is graph traversal?"
        ]
        
        # Execute concurrent queries
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_query, q) for q in questions]
            results = [future.result() for future in futures]
        
        # Verify all requests succeeded
        for status_code, result in results:
            assert status_code == 200
            assert "answer" in result
            assert len(result.get("sources", [])) > 0
    
    def test_service_failure_handling(self):
        """Test graceful degradation when services fail"""
        # Test BitNet failure simulation
        # This would require a way to temporarily disable BitNet
        
        # Query with BitNet unavailable
        query_payload = {
            "question": "What is Neo4j?",
            "k": 3,
            "use_llm": True
        }
        
        response = requests.post("http://localhost:8000/query", json=query_payload)
        result = response.json()
        
        # Should still return sources even if LLM fails
        assert "sources" in result
        assert len(result["sources"]) > 0
    
    def test_large_document_upload(self):
        """Test upload of large documents"""
        # Create a large test document
        large_content = "Graph databases are powerful. " * 10000  # ~300KB
        
        files = {
            "file": ("large_doc.txt", large_content, "text/plain")
        }
        
        start_time = time.time()
        response = requests.post("http://localhost:8000/upload", files=files)
        upload_time = time.time() - start_time
        
        assert response.status_code == 200
        assert upload_time < 30, f"Upload too slow: {upload_time}s"
        
        # Wait for processing
        time.sleep(5)
        
        # Verify document is searchable
        query_response = requests.post(
            "http://localhost:8000/query",
            json={"question": "graph databases powerful", "k": 3}
        )
        
        result = query_response.json()
        assert len(result["sources"]) > 0
```

### 3. User Experience Testing

#### Streamlit UI Testing
```python
# tests/test_ui_behavior.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class TestStreamlitUI:
    
    @pytest.fixture
    def driver(self):
        """Setup Chrome WebDriver for UI testing"""
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
        driver = webdriver.Chrome(options=options)
        driver.get("http://localhost:8501")
        yield driver
        driver.quit()
    
    def test_chat_input_functionality(self, driver):
        """Test chat input and message display"""
        # Wait for page to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "input"))
        )
        
        # Find chat input
        chat_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='stChatInput'] input")
        
        # Type message
        test_message = "What is Neo4j?"
        chat_input.send_keys(test_message)
        
        # Submit message
        submit_button = driver.find_element(By.CSS_SELECTOR, "[data-testid='stChatInput'] button")
        submit_button.click()
        
        # Wait for response
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='stChatMessage']"))
        )
        
        # Verify messages appear
        messages = driver.find_elements(By.CSS_SELECTOR, "[data-testid='stChatMessage']")
        assert len(messages) >= 2  # User + Assistant message
    
    def test_file_upload_widget(self, driver):
        """Test document upload functionality"""
        # Create a test file
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a test document for upload testing.")
            temp_file_path = f.name
        
        try:
            # Find file upload widget
            file_input = driver.find_element(By.CSS_SELECTOR, "[data-testid='stFileUploader'] input[type='file']")
            
            # Upload file
            file_input.send_keys(temp_file_path)
            
            # Find and click upload button
            upload_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Upload')]"))
            )
            upload_button.click()
            
            # Wait for success message
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'uploaded successfully')]"))
            )
            
        finally:
            # Clean up
            os.unlink(temp_file_path)
    
    def test_system_stats_display(self, driver):
        """Test system statistics display"""
        # Wait for stats to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'Documents:')]"))
        )
        
        # Check for key metrics
        stats_elements = [
            "Documents:",
            "Chunks:",
            "Avg Query",
            "Cache Hit",
            "Neo4j:",
            "BitNet:"
        ]
        
        for stat in stats_elements:
            element = driver.find_element(By.XPATH, f"//*[contains(text(), '{stat}')]")
            assert element.is_displayed()
```

### 4. Performance Testing

#### Load Testing Script
```python
# tests/test_performance.py
import pytest
import requests
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

class TestPerformance:
    
    def test_response_time_benchmarks(self):
        """Benchmark response times for different query types"""
        test_queries = [
            "What is Neo4j?",
            "How does graph traversal work?",
            "Explain Cypher query syntax",
            "What are the benefits of graph databases?",
            "How to create nodes in Neo4j?"
        ]
        
        response_times = []
        
        for query in test_queries:
            start_time = time.time()
            
            response = requests.post(
                "http://localhost:8000/query",
                json={"question": query, "k": 3}
            )
            
            end_time = time.time()
            
            assert response.status_code == 200
            response_time = end_time - start_time
            response_times.append(response_time)
            
            print(f"Query: '{query}' - Time: {response_time:.3f}s")
        
        # Performance assertions
        avg_time = statistics.mean(response_times)
        max_time = max(response_times)
        
        assert avg_time < 2.0, f"Average response time too high: {avg_time:.3f}s"
        assert max_time < 5.0, f"Maximum response time too high: {max_time:.3f}s"
        
        print(f"Performance Summary:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Maximum: {max_time:.3f}s")
        print(f"  Minimum: {min(response_times):.3f}s")
    
    def test_concurrent_user_simulation(self):
        """Simulate multiple users using the chat interface"""
        def simulate_user_session(user_id):
            """Simulate a single user's chat session"""
            session_queries = [
                f"User {user_id}: What is Neo4j?",
                f"User {user_id}: How does it store data?",
                f"User {user_id}: What is Cypher?"
            ]
            
            session_times = []
            
            for query in session_queries:
                start = time.time()
                response = requests.post(
                    "http://localhost:8000/query",
                    json={"question": query, "k": 3}
                )
                end = time.time()
                
                session_times.append(end - start)
                assert response.status_code == 200
                
                # Brief pause between queries
                time.sleep(0.5)
            
            return user_id, session_times
        
        # Simulate 10 concurrent users
        num_users = 10
        
        with ThreadPoolExecutor(max_workers=num_users) as executor:
            futures = [
                executor.submit(simulate_user_session, user_id) 
                for user_id in range(num_users)
            ]
            
            results = []
            for future in as_completed(futures):
                user_id, times = future.result()
                results.append((user_id, times))
                print(f"User {user_id} completed - Avg: {statistics.mean(times):.3f}s")
        
        # Analyze results
        all_times = [time for _, times in results for time in times]
        overall_avg = statistics.mean(all_times)
        
        assert overall_avg < 3.0, f"Concurrent performance degraded: {overall_avg:.3f}s"
        print(f"Concurrent Performance: {overall_avg:.3f}s average")
```

## Testing Execution Plan

### Phase 1: Environment Setup (Day 1)
1. **Service Startup Verification**
   ```bash
   # Start all services
   docker-compose -f docker-compose-bitnet.yml up -d
   
   # Verify services are healthy
   curl http://localhost:8000/health
   curl http://localhost:8001/health
   curl http://localhost:7474
   
   # Load test data
   python scripts/load_sample_data.py
   ```

2. **Test Dependencies Installation**
   ```bash
   # Install testing dependencies
   pip install pytest selenium requests plotly pandas streamlit
   
   # Download ChromeDriver for UI tests
   # (Platform specific instructions)
   ```

### Phase 2: Functional Testing (Days 2-3)
1. **Unit Tests**: Test individual components
2. **Integration Tests**: Test service interactions
3. **UI Tests**: Test Streamlit interface
4. **End-to-End Tests**: Complete user workflows

### Phase 3: Performance Testing (Day 4)
1. **Response Time Benchmarks**
2. **Load Testing**: Concurrent user simulation
3. **Stress Testing**: Resource limits
4. **Memory Usage Analysis**

### Phase 4: User Experience Testing (Day 5)
1. **Usability Testing**: Interface intuitiveness
2. **Error Handling**: Failure scenarios
3. **Mobile Responsiveness**: Different screen sizes
4. **Accessibility**: Screen reader compatibility

## Continuous Testing Setup

### GitHub Actions Workflow
```yaml
# .github/workflows/streamlit-test.yml
name: Streamlit Chat UI Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test-local-stack:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.11'
    
    - name: Start services
      run: |
        docker-compose -f docker-compose-bitnet.yml up -d
        sleep 30  # Allow services to start
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest selenium requests
    
    - name: Load test data
      run: python scripts/load_sample_data.py
    
    - name: Run tests
      run: |
        pytest tests/test_rag_integration.py -v
        pytest tests/test_performance.py -v
    
    - name: Cleanup
      if: always()
      run: docker-compose -f docker-compose-bitnet.yml down
```

## Success Metrics

### Performance Benchmarks
- **Query Response Time**: < 2 seconds average
- **Document Upload**: < 30 seconds for 1MB files
- **Concurrent Users**: Handle 10+ simultaneous users
- **System Availability**: > 99% uptime during testing

### Functionality Metrics
- **Test Coverage**: > 80% code coverage
- **Integration Success**: 100% service communication
- **UI Responsiveness**: All interactions < 1 second
- **Error Recovery**: Graceful handling of all failure modes

### User Experience Metrics
- **Interface Intuitiveness**: No training required
- **Response Streaming**: Smooth typewriter effect
- **Mobile Compatibility**: Full functionality on mobile
- **Accessibility**: WCAG 2.1 AA compliance

## Risk Mitigation

### Potential Issues & Solutions

1. **Service Startup Time**
   - **Risk**: BitNet takes time to load model
   - **Mitigation**: Health check retries, loading indicators

2. **Memory Consumption**
   - **Risk**: Multiple services consume significant RAM
   - **Mitigation**: Resource monitoring, container limits

3. **Concurrent Access**
   - **Risk**: Database locks under load
   - **Mitigation**: Connection pooling, query optimization

4. **File Upload Limits**
   - **Risk**: Large files cause timeouts
   - **Mitigation**: File size limits, chunked uploads

## Next Steps

1. **Implementation Phase**: Develop Streamlit application
2. **Testing Phase**: Execute comprehensive test suite
3. **Optimization Phase**: Performance tuning based on results
4. **Documentation Phase**: User guides and API documentation
5. **Deployment Phase**: Production readiness checklist

---

**Testing Status**: 📋 Plan Complete - Ready for Execution  
**Estimated Testing Time**: 5 days  
**Key Dependencies**: Docker services, Sample data, Test environment