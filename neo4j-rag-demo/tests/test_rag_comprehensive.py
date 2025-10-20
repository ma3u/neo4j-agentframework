#!/usr/bin/env python3
"""
Comprehensive Test Suite for Neo4j RAG System
Tests 20 different scenarios covering functionality, performance, and edge cases
"""

import requests
import json
import time
from typing import Dict, List, Tuple
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_RESULTS = []

class TestResult:
    def __init__(self, test_id: int, name: str, category: str):
        self.test_id = test_id
        self.name = name
        self.category = category
        self.status = "NOT_RUN"
        self.response_time = 0
        self.details = {}
        self.error = None

    def to_dict(self):
        return {
            "test_id": self.test_id,
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "response_time_ms": self.response_time,
            "details": self.details,
            "error": self.error
        }

def run_test(test_id: int, name: str, category: str, test_func):
    """Run a single test and record results"""
    result = TestResult(test_id, name, category)
    print(f"\n{'='*80}")
    print(f"Test {test_id}: {name}")
    print(f"Category: {category}")
    print(f"{'='*80}")

    try:
        start_time = time.time()
        test_func(result)
        result.response_time = (time.time() - start_time) * 1000
        if result.status == "NOT_RUN":
            result.status = "PASS"
        print(f"✅ PASS - {result.response_time:.2f}ms")
    except Exception as e:
        result.status = "FAIL"
        result.error = str(e)
        result.response_time = (time.time() - start_time) * 1000
        print(f"❌ FAIL - {str(e)}")

    TEST_RESULTS.append(result)
    return result

# ============================================================================
# Test Cases
# ============================================================================

def test_1_health_check(result: TestResult):
    """Test 1: Basic Health Check - System Status"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    result.details = data

    assert data["status"] == "healthy", f"Service not healthy: {data['status']}"
    assert data["mode"] == "production", f"Expected production mode, got {data['mode']}"
    assert "stats" in data, "Missing stats in health response"

    print(f"   Status: {data['status']}")
    print(f"   Mode: {data['mode']}")
    print(f"   Documents: {data['stats'].get('documents', 'N/A')}")
    print(f"   Chunks: {data['stats'].get('chunks', 'N/A')}")

def test_2_stats_endpoint(result: TestResult):
    """Test 2: Stats Endpoint - Database Statistics"""
    response = requests.get(f"{BASE_URL}/stats")
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    result.details = data

    assert "documents" in data, "Missing documents count"
    assert "chunks" in data, "Missing chunks count"
    assert data["documents"] > 0, "No documents in database"
    assert data["chunks"] > 0, "No chunks in database"

    print(f"   Documents: {data['documents']}")
    print(f"   Chunks: {data['chunks']}")
    print(f"   Avg chunks/doc: {data.get('avg_chunks_per_doc', 'N/A')}")

def test_3_simple_query(result: TestResult):
    """Test 3: Simple Query - What is Neo4j?"""
    query = {"question": "What is Neo4j?", "k": 3}
    response = requests.post(f"{BASE_URL}/query", json=query)

    assert response.status_code == 200, f"Expected 200, got {response.status_code}"

    data = response.json()
    result.details = {
        "num_results": len(data.get("results", [])),
        "first_score": data["results"][0]["score"] if data.get("results") else None
    }

    assert "results" in data, "Missing results in response"
    assert len(data["results"]) > 0, "No results returned"
    assert len(data["results"]) <= 3, f"Expected max 3 results, got {len(data['results'])}"

    print(f"   Results returned: {len(data['results'])}")
    print(f"   First result score: {data['results'][0]['score']:.4f}")
    print(f"   First result text: {data['results'][0]['text'][:80]}...")

def test_4_graph_database_query(result: TestResult):
    """Test 4: Graph Database Specific Query"""
    query = {"question": "How does graph database work?", "k": 5}
    response = requests.post(f"{BASE_URL}/query", json=query)

    assert response.status_code == 200
    data = response.json()

    result.details = {
        "num_results": len(data["results"]),
        "avg_score": sum(r["score"] for r in data["results"]) / len(data["results"]) if data["results"] else 0
    }

    assert len(data["results"]) > 0, "No results for graph database query"

    print(f"   Results: {len(data['results'])}")
    print(f"   Average score: {result.details['avg_score']:.4f}")

def test_5_rag_specific_query(result: TestResult):
    """Test 5: RAG System Query"""
    query = {"question": "What is Retrieval-Augmented Generation?", "k": 5}
    response = requests.post(f"{BASE_URL}/query", json=query)

    assert response.status_code == 200
    data = response.json()

    result.details = {
        "num_results": len(data["results"]),
        "has_rag_content": any("RAG" in r["text"] or "retrieval" in r["text"].lower() for r in data["results"])
    }

    assert len(data["results"]) > 0, "No results for RAG query"

    print(f"   Results: {len(data['results'])}")
    print(f"   Contains RAG content: {result.details['has_rag_content']}")

def test_6_performance_single_result(result: TestResult):
    """Test 6: Performance Test - Single Result (k=1)"""
    query = {"question": "What is a knowledge graph?", "k": 1}

    start = time.time()
    response = requests.post(f"{BASE_URL}/query", json=query)
    query_time = (time.time() - start) * 1000

    assert response.status_code == 200
    data = response.json()

    result.details = {
        "query_time_ms": query_time,
        "num_results": len(data["results"])
    }

    assert len(data["results"]) == 1, f"Expected 1 result, got {len(data['results'])}"
    assert query_time < 5000, f"Query too slow: {query_time}ms (expected < 5000ms)"

    print(f"   Query time: {query_time:.2f}ms")
    print(f"   Within performance target: {query_time < 5000}")

def test_7_performance_multiple_results(result: TestResult):
    """Test 7: Performance Test - Multiple Results (k=10)"""
    query = {"question": "Explain vector search", "k": 10}

    start = time.time()
    response = requests.post(f"{BASE_URL}/query", json=query)
    query_time = (time.time() - start) * 1000

    assert response.status_code == 200
    data = response.json()

    result.details = {
        "query_time_ms": query_time,
        "num_results": len(data["results"])
    }

    assert len(data["results"]) > 0, "No results returned"
    assert query_time < 10000, f"Query too slow: {query_time}ms (expected < 10000ms)"

    print(f"   Query time: {query_time:.2f}ms")
    print(f"   Results: {len(data['results'])}")

def test_8_metadata_validation(result: TestResult):
    """Test 8: Metadata Completeness Check"""
    query = {"question": "What is Neo4j?", "k": 1}
    response = requests.post(f"{BASE_URL}/query", json=query)

    assert response.status_code == 200
    data = response.json()

    assert len(data["results"]) > 0, "No results to validate metadata"

    first_result = data["results"][0]
    required_fields = ["text", "score", "doc_id", "chunk_index", "metadata"]

    for field in required_fields:
        assert field in first_result, f"Missing required field: {field}"

    result.details = {
        "has_all_fields": True,
        "metadata_keys": list(first_result.get("metadata", {}).keys())
    }

    print(f"   All required fields present: ✅")
    print(f"   Metadata keys: {', '.join(result.details['metadata_keys'][:5])}...")

def test_9_score_ordering(result: TestResult):
    """Test 9: Results Ordered by Score (Descending)"""
    query = {"question": "How does vector similarity work?", "k": 5}
    response = requests.post(f"{BASE_URL}/query", json=query)

    assert response.status_code == 200
    data = response.json()

    assert len(data["results"]) > 1, "Need multiple results to test ordering"

    scores = [r["score"] for r in data["results"]]
    is_ordered = all(scores[i] >= scores[i+1] for i in range(len(scores)-1))

    result.details = {
        "scores": scores,
        "properly_ordered": is_ordered
    }

    assert is_ordered, f"Results not properly ordered: {scores}"

    print(f"   Scores: {[f'{s:.4f}' for s in scores]}")
    print(f"   Properly ordered: ✅")

def test_10_empty_query_handling(result: TestResult):
    """Test 10: Empty Query Error Handling"""
    query = {"question": "", "k": 3}
    response = requests.post(f"{BASE_URL}/query", json=query)

    # Should either reject or return empty results
    result.details = {
        "status_code": response.status_code,
        "response": response.text[:200]
    }

    # Accept either 400 (validation error) or 200 with empty/few results
    assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"

    print(f"   Status code: {response.status_code}")
    print(f"   Handled appropriately: ✅")

def test_11_invalid_k_parameter(result: TestResult):
    """Test 11: Invalid k Parameter Handling"""
    query = {"question": "What is Neo4j?", "k": 0}
    response = requests.post(f"{BASE_URL}/query", json=query)

    result.details = {
        "status_code": response.status_code,
        "response_preview": response.text[:200]
    }

    # Should handle gracefully (either error or default to minimum)
    assert response.status_code in [200, 400, 422], f"Unexpected status: {response.status_code}"

    print(f"   Status code: {response.status_code}")
    print(f"   Error handling: ✅")

def test_12_large_k_parameter(result: TestResult):
    """Test 12: Large k Parameter (k=20)"""
    query = {"question": "Explain graph algorithms", "k": 20}
    response = requests.post(f"{BASE_URL}/query", json=query)

    assert response.status_code == 200
    data = response.json()

    result.details = {
        "requested_k": 20,
        "returned_results": len(data["results"])
    }

    assert len(data["results"]) > 0, "No results returned"

    print(f"   Requested k: 20")
    print(f"   Returned: {len(data['results'])} results")

def test_13_technical_query(result: TestResult):
    """Test 13: Technical Query - Cypher Language"""
    query = {"question": "How do you write Cypher queries?", "k": 3}
    response = requests.post(f"{BASE_URL}/query", json=query)

    assert response.status_code == 200
    data = response.json()

    result.details = {
        "num_results": len(data["results"]),
        "contains_cypher": any("cypher" in r["text"].lower() for r in data["results"])
    }

    assert len(data["results"]) > 0, "No results for Cypher query"

    print(f"   Results: {len(data['results'])}")
    print(f"   Contains Cypher content: {result.details['contains_cypher']}")

def test_14_concept_query(result: TestResult):
    """Test 14: Conceptual Query - Graph Theory"""
    query = {"question": "What are nodes and relationships in graph databases?", "k": 5}
    response = requests.post(f"{BASE_URL}/query", json=query)

    assert response.status_code == 200
    data = response.json()

    result.details = {
        "num_results": len(data["results"]),
        "avg_score": sum(r["score"] for r in data["results"]) / len(data["results"]) if data["results"] else 0
    }

    assert len(data["results"]) > 0, "No results for concept query"

    print(f"   Results: {len(data['results'])}")
    print(f"   Average relevance: {result.details['avg_score']:.4f}")

def test_15_comparison_query(result: TestResult):
    """Test 15: Comparison Query - Graph vs Relational"""
    query = {"question": "What is the difference between graph and relational databases?", "k": 5}
    response = requests.post(f"{BASE_URL}/query", json=query)

    assert response.status_code == 200
    data = response.json()

    result.details = {
        "num_results": len(data["results"]),
        "top_score": data["results"][0]["score"] if data["results"] else 0
    }

    assert len(data["results"]) > 0, "No results for comparison query"

    print(f"   Results: {len(data['results'])}")
    print(f"   Top score: {result.details['top_score']:.4f}")

def test_16_use_case_query(result: TestResult):
    """Test 16: Use Case Query - Applications"""
    query = {"question": "What are common use cases for graph databases?", "k": 5}
    response = requests.post(f"{BASE_URL}/query", json=query)

    assert response.status_code == 200
    data = response.json()

    result.details = {
        "num_results": len(data["results"]),
        "unique_docs": len(set(r["doc_id"] for r in data["results"]))
    }

    assert len(data["results"]) > 0, "No results for use case query"

    print(f"   Results: {len(data['results'])}")
    print(f"   Unique documents: {result.details['unique_docs']}")

def test_17_performance_query(result: TestResult):
    """Test 17: Performance Query - Optimization"""
    query = {"question": "How can I optimize graph database performance?", "k": 5}
    response = requests.post(f"{BASE_URL}/query", json=query)

    assert response.status_code == 200
    data = response.json()

    result.details = {
        "num_results": len(data["results"]),
        "contains_performance": any("performance" in r["text"].lower() or "optimize" in r["text"].lower() for r in data["results"])
    }

    assert len(data["results"]) > 0, "No results for performance query"

    print(f"   Results: {len(data['results'])}")
    print(f"   Contains performance content: {result.details['contains_performance']}")

def test_18_concurrent_queries(result: TestResult):
    """Test 18: Concurrent Query Handling"""
    import concurrent.futures

    queries = [
        {"question": "What is Neo4j?", "k": 3},
        {"question": "How does RAG work?", "k": 3},
        {"question": "Explain vector search", "k": 3},
        {"question": "What are graph databases?", "k": 3},
        {"question": "How to use Cypher?", "k": 3}
    ]

    def run_query(q):
        start = time.time()
        response = requests.post(f"{BASE_URL}/query", json=q)
        return {
            "status": response.status_code,
            "time": (time.time() - start) * 1000,
            "results": len(response.json().get("results", [])) if response.status_code == 200 else 0
        }

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        results = list(executor.map(run_query, queries))

    all_success = all(r["status"] == 200 for r in results)
    avg_time = sum(r["time"] for r in results) / len(results)

    result.details = {
        "concurrent_queries": len(queries),
        "all_successful": all_success,
        "avg_response_time_ms": avg_time,
        "individual_times": [r["time"] for r in results]
    }

    assert all_success, "Some concurrent queries failed"

    print(f"   Concurrent queries: {len(queries)}")
    print(f"   All successful: ✅")
    print(f"   Average time: {avg_time:.2f}ms")

def test_19_cache_performance(result: TestResult):
    """Test 19: Cache Performance - Repeat Query"""
    query = {"question": "What is a knowledge graph?", "k": 5}

    # First query (cold)
    start = time.time()
    response1 = requests.post(f"{BASE_URL}/query", json=query)
    time1 = (time.time() - start) * 1000

    # Second query (should be cached)
    start = time.time()
    response2 = requests.post(f"{BASE_URL}/query", json=query)
    time2 = (time.time() - start) * 1000

    # Third query (should be cached)
    start = time.time()
    response3 = requests.post(f"{BASE_URL}/query", json=query)
    time3 = (time.time() - start) * 1000

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert response3.status_code == 200

    result.details = {
        "first_query_ms": time1,
        "second_query_ms": time2,
        "third_query_ms": time3,
        "speedup_2nd": time1 / time2 if time2 > 0 else 0,
        "speedup_3rd": time1 / time3 if time3 > 0 else 0
    }

    print(f"   1st query (cold): {time1:.2f}ms")
    print(f"   2nd query (cached): {time2:.2f}ms")
    print(f"   3rd query (cached): {time3:.2f}ms")
    print(f"   Speedup: {result.details['speedup_2nd']:.2f}x")

def test_20_end_to_end_workflow(result: TestResult):
    """Test 20: End-to-End Workflow Test"""
    # 1. Check health
    health = requests.get(f"{BASE_URL}/health")
    assert health.status_code == 200

    # 2. Get stats
    stats = requests.get(f"{BASE_URL}/stats")
    assert stats.status_code == 200
    stats_data = stats.json()

    # 3. Run query
    query = {"question": "What is Neo4j and why should I use it?", "k": 5}
    query_response = requests.post(f"{BASE_URL}/query", json=query)
    assert query_response.status_code == 200
    query_data = query_response.json()

    result.details = {
        "health_check": "PASS",
        "stats_available": "PASS",
        "query_results": len(query_data["results"]),
        "total_documents": stats_data.get("documents"),
        "total_chunks": stats_data.get("chunks")
    }

    assert len(query_data["results"]) > 0, "End-to-end query failed"

    print(f"   Health check: ✅")
    print(f"   Stats retrieved: ✅")
    print(f"   Query executed: ✅")
    print(f"   Results: {len(query_data['results'])}")
    print(f"   Database: {stats_data.get('documents')} docs, {stats_data.get('chunks')} chunks")

# ============================================================================
# Main Test Runner
# ============================================================================

def run_all_tests():
    """Run all 20 test cases"""
    print("\n" + "="*80)
    print("NEO4J RAG SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*80)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {BASE_URL}")
    print("="*80)

    # Category 1: Health & System Tests (2 tests)
    run_test(1, "Basic Health Check", "Health & System", test_1_health_check)
    run_test(2, "Stats Endpoint", "Health & System", test_2_stats_endpoint)

    # Category 2: Functional Tests (8 tests)
    run_test(3, "Simple Query - What is Neo4j?", "Functional", test_3_simple_query)
    run_test(4, "Graph Database Query", "Functional", test_4_graph_database_query)
    run_test(5, "RAG System Query", "Functional", test_5_rag_specific_query)
    run_test(13, "Technical Query - Cypher", "Functional", test_13_technical_query)
    run_test(14, "Conceptual Query - Graph Theory", "Functional", test_14_concept_query)
    run_test(15, "Comparison Query", "Functional", test_15_comparison_query)
    run_test(16, "Use Case Query", "Functional", test_16_use_case_query)
    run_test(17, "Performance Query", "Functional", test_17_performance_query)

    # Category 3: Performance Tests (4 tests)
    run_test(6, "Performance - Single Result (k=1)", "Performance", test_6_performance_single_result)
    run_test(7, "Performance - Multiple Results (k=10)", "Performance", test_7_performance_multiple_results)
    run_test(18, "Concurrent Query Handling", "Performance", test_18_concurrent_queries)
    run_test(19, "Cache Performance Test", "Performance", test_19_cache_performance)

    # Category 4: Data Quality Tests (2 tests)
    run_test(8, "Metadata Completeness", "Data Quality", test_8_metadata_validation)
    run_test(9, "Score Ordering Validation", "Data Quality", test_9_score_ordering)

    # Category 5: Error Handling Tests (3 tests)
    run_test(10, "Empty Query Handling", "Error Handling", test_10_empty_query_handling)
    run_test(11, "Invalid k Parameter", "Error Handling", test_11_invalid_k_parameter)
    run_test(12, "Large k Parameter (k=20)", "Error Handling", test_12_large_k_parameter)

    # Category 6: Integration Test (1 test)
    run_test(20, "End-to-End Workflow", "Integration", test_20_end_to_end_workflow)

    # Generate summary
    print_summary()
    save_results()

def print_summary():
    """Print test summary"""
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    total = len(TEST_RESULTS)
    passed = sum(1 for r in TEST_RESULTS if r.status == "PASS")
    failed = sum(1 for r in TEST_RESULTS if r.status == "FAIL")

    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/total*100):.1f}%")

    # Category breakdown
    categories = {}
    for r in TEST_RESULTS:
        if r.category not in categories:
            categories[r.category] = {"pass": 0, "fail": 0}
        if r.status == "PASS":
            categories[r.category]["pass"] += 1
        else:
            categories[r.category]["fail"] += 1

    print("\nResults by Category:")
    for cat, stats in sorted(categories.items()):
        print(f"  {cat}: {stats['pass']} passed, {stats['fail']} failed")

    # Performance stats
    avg_time = sum(r.response_time for r in TEST_RESULTS) / len(TEST_RESULTS)
    max_time = max(r.response_time for r in TEST_RESULTS)
    min_time = min(r.response_time for r in TEST_RESULTS)

    print(f"\nPerformance:")
    print(f"  Average response time: {avg_time:.2f}ms")
    print(f"  Min response time: {min_time:.2f}ms")
    print(f"  Max response time: {max_time:.2f}ms")

    if failed > 0:
        print("\nFailed Tests:")
        for r in TEST_RESULTS:
            if r.status == "FAIL":
                print(f"  - Test {r.test_id}: {r.name}")
                print(f"    Error: {r.error}")

def save_results():
    """Save test results to JSON file"""
    results = {
        "timestamp": datetime.now().isoformat(),
        "base_url": BASE_URL,
        "summary": {
            "total": len(TEST_RESULTS),
            "passed": sum(1 for r in TEST_RESULTS if r.status == "PASS"),
            "failed": sum(1 for r in TEST_RESULTS if r.status == "FAIL"),
            "success_rate": sum(1 for r in TEST_RESULTS if r.status == "PASS") / len(TEST_RESULTS) * 100
        },
        "tests": [r.to_dict() for r in TEST_RESULTS]
    }

    filename = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n📄 Results saved to: {filename}")

if __name__ == "__main__":
    try:
        run_all_tests()
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        print_summary()
        save_results()
    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
