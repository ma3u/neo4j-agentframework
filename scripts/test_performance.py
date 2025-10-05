#!/usr/bin/env python3
"""
Performance Test Script for Ultra-High-Performance BitNet RAG
Tests the system against the documented 38ms response time target
"""

import asyncio
import time
import statistics
import requests
import json
from typing import List, Dict, Any
import sys

# Test configuration
BASE_URL = "http://localhost:8000"
TARGET_RESPONSE_TIME = 38  # ms
ACCEPTABLE_RESPONSE_TIME = 50  # ms

# Test queries designed to test different aspects
TEST_QUERIES = [
    "What is BitNet?",
    "How does Neo4j work?",
    "Explain graph databases",
    "What are the benefits of 1.58-bit quantization?",
    "How do embeddings work?",
    "What is artificial intelligence?",
    "Explain machine learning",
    "What are neural networks?",
    "How do transformers work?",
    "What is deep learning?"
]

SAMPLE_DOCUMENTS = [
    {
        "id": "doc1",
        "content": "BitNet b1.58 achieves 87% memory reduction with true 1.58-bit quantization using native BitNet.cpp. It provides lossless inference with optimized CPU kernels for maximum efficiency."
    },
    {
        "id": "doc2", 
        "content": "Neo4j is a high-performance graph database for connected data. It uses nodes and relationships to store and query complex data structures efficiently."
    },
    {
        "id": "doc3",
        "content": "Graph databases like Neo4j excel at handling connected data and complex relationships. They provide fast traversal and pattern matching capabilities."
    },
    {
        "id": "doc4",
        "content": "Artificial Intelligence (AI) encompasses machine learning, neural networks, and deep learning. These technologies enable computers to perform tasks that typically require human intelligence."
    },
    {
        "id": "doc5",
        "content": "Embeddings are numerical representations of text that capture semantic meaning. They enable similarity search and are fundamental to modern NLP applications."
    }
]


class PerformanceTester:
    """Test suite for BitNet RAG performance"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def check_health(self) -> Dict[str, Any]:
        """Check system health and get current performance metrics"""
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return {}
    
    def add_test_documents(self) -> bool:
        """Add sample documents to the knowledge base"""
        try:
            print("📄 Adding test documents...")
            response = self.session.post(
                f"{self.base_url}/add-documents",
                json={"documents": SAMPLE_DOCUMENTS},
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            print(f"✅ Added {len(SAMPLE_DOCUMENTS)} documents in {result.get('processing_time_ms', 0):.1f}ms")
            return True
        except Exception as e:
            print(f"❌ Failed to add documents: {e}")
            return False
    
    def test_single_query(self, query: str) -> Dict[str, Any]:
        """Test a single query and return performance metrics"""
        try:
            start_time = time.perf_counter()
            
            response = self.session.post(
                f"{self.base_url}/query",
                json={
                    "question": query,
                    "max_results": 3,
                    "include_sources": True,
                    "include_performance": True
                },
                timeout=10
            )
            
            end_time = time.perf_counter()
            total_time_ms = (end_time - start_time) * 1000
            
            response.raise_for_status()
            result = response.json()
            
            return {
                "query": query,
                "success": True,
                "total_time_ms": total_time_ms,
                "processing_time_ms": result.get("performance", {}).get("total_time_ms", 0),
                "cache_hit_rate": result.get("performance", {}).get("cache_hit_rate", 0),
                "contexts_found": result.get("performance", {}).get("contexts_found", 0),
                "answer": result.get("answer", "")[:100] + "..." if len(result.get("answer", "")) > 100 else result.get("answer", ""),
                "optimization_stats": result.get("optimization_stats", {})
            }
            
        except Exception as e:
            return {
                "query": query,
                "success": False,
                "error": str(e),
                "total_time_ms": 0,
                "processing_time_ms": 0
            }
    
    def run_performance_benchmark(self, queries: List[str], iterations: int = 5) -> Dict[str, Any]:
        """Run comprehensive performance benchmark"""
        print(f"🚀 Starting performance benchmark with {len(queries)} queries, {iterations} iterations each")
        print(f"🎯 Target: {TARGET_RESPONSE_TIME}ms, Acceptable: {ACCEPTABLE_RESPONSE_TIME}ms")
        print("=" * 80)
        
        all_results = []
        all_times = []
        successful_queries = 0
        
        for query in queries:
            print(f"\n📝 Testing: '{query[:50]}{'...' if len(query) > 50 else ''}'")
            query_times = []
            
            # Warm-up query (not counted in results)
            self.test_single_query(query)
            
            # Actual test iterations
            for i in range(iterations):
                result = self.test_single_query(query)
                if result["success"]:
                    query_times.append(result["processing_time_ms"])
                    all_times.append(result["processing_time_ms"])
                    successful_queries += 1
                    
                    # Print progress
                    status_icon = "🎯" if result["processing_time_ms"] <= TARGET_RESPONSE_TIME else "✅" if result["processing_time_ms"] <= ACCEPTABLE_RESPONSE_TIME else "⚠️"
                    print(f"  {status_icon} Iteration {i+1}: {result['processing_time_ms']:.1f}ms (cache: {result['cache_hit_rate']:.1f}%)")
                else:
                    print(f"  ❌ Iteration {i+1}: Failed - {result['error']}")
            
            if query_times:
                avg_time = statistics.mean(query_times)
                min_time = min(query_times)
                max_time = max(query_times)
                std_dev = statistics.stdev(query_times) if len(query_times) > 1 else 0
                
                query_result = {
                    "query": query,
                    "iterations": iterations,
                    "avg_time_ms": avg_time,
                    "min_time_ms": min_time,
                    "max_time_ms": max_time,
                    "std_dev_ms": std_dev,
                    "success_rate": len(query_times) / iterations * 100
                }
                
                all_results.append(query_result)
                
                # Performance grade
                grade = "A+" if avg_time <= 25 else "A" if avg_time <= TARGET_RESPONSE_TIME else "B" if avg_time <= ACCEPTABLE_RESPONSE_TIME else "C"
                print(f"  📊 Average: {avg_time:.1f}ms (min: {min_time:.1f}ms, max: {max_time:.1f}ms) - Grade: {grade}")
        
        # Overall summary
        if all_times:
            overall_avg = statistics.mean(all_times)
            overall_min = min(all_times)
            overall_max = max(all_times)
            overall_std = statistics.stdev(all_times) if len(all_times) > 1 else 0
            
            target_achieved = sum(1 for t in all_times if t <= TARGET_RESPONSE_TIME)
            acceptable_achieved = sum(1 for t in all_times if t <= ACCEPTABLE_RESPONSE_TIME)
            
            performance_grade = (
                "A+" if overall_avg <= 25 else
                "A" if overall_avg <= TARGET_RESPONSE_TIME else
                "B" if overall_avg <= ACCEPTABLE_RESPONSE_TIME else
                "C" if overall_avg <= 100 else "D"
            )
            
            summary = {
                "total_queries": len(all_times),
                "successful_queries": successful_queries,
                "overall_avg_ms": overall_avg,
                "overall_min_ms": overall_min,
                "overall_max_ms": overall_max,
                "overall_std_ms": overall_std,
                "target_achieved_count": target_achieved,
                "target_achieved_percent": target_achieved / len(all_times) * 100,
                "acceptable_achieved_count": acceptable_achieved,
                "acceptable_achieved_percent": acceptable_achieved / len(all_times) * 100,
                "performance_grade": performance_grade,
                "success_rate": successful_queries / (len(queries) * iterations) * 100
            }
        else:
            summary = {"error": "No successful queries"}
        
        return {
            "query_results": all_results,
            "summary": summary
        }
    
    def print_benchmark_report(self, results: Dict[str, Any]):
        """Print a comprehensive benchmark report"""
        print("\n" + "=" * 80)
        print("📊 PERFORMANCE BENCHMARK REPORT")
        print("=" * 80)
        
        summary = results.get("summary", {})
        
        if "error" in summary:
            print(f"❌ Benchmark failed: {summary['error']}")
            return
        
        # Overall performance
        print(f"🎯 Overall Performance: {summary['performance_grade']}")
        print(f"📈 Average Response Time: {summary['overall_avg_ms']:.1f}ms")
        print(f"⚡ Best Response Time: {summary['overall_min_ms']:.1f}ms")
        print(f"🐌 Worst Response Time: {summary['overall_max_ms']:.1f}ms")
        print(f"📊 Standard Deviation: {summary['overall_std_ms']:.1f}ms")
        print(f"✅ Success Rate: {summary['success_rate']:.1f}%")
        
        print(f"\n🎯 Target Performance ({TARGET_RESPONSE_TIME}ms):")
        print(f"   Achieved: {summary['target_achieved_count']}/{summary['total_queries']} ({summary['target_achieved_percent']:.1f}%)")
        
        print(f"\n✅ Acceptable Performance ({ACCEPTABLE_RESPONSE_TIME}ms):")
        print(f"   Achieved: {summary['acceptable_achieved_count']}/{summary['total_queries']} ({summary['acceptable_achieved_percent']:.1f}%)")
        
        # Performance analysis
        print(f"\n📋 Performance Analysis:")
        if summary['overall_avg_ms'] <= TARGET_RESPONSE_TIME:
            print("   🎉 EXCELLENT: Target performance achieved!")
        elif summary['overall_avg_ms'] <= ACCEPTABLE_RESPONSE_TIME:
            print("   ✅ GOOD: Acceptable performance achieved")
        elif summary['overall_avg_ms'] <= 100:
            print("   ⚠️  NEEDS OPTIMIZATION: Performance below target")
        else:
            print("   ❌ POOR: Significant optimization required")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if summary['overall_avg_ms'] > ACCEPTABLE_RESPONSE_TIME:
            print("   - Increase embedding cache size")
            print("   - Verify Neo4j indexes are created")
            print("   - Check BitNet.cpp model loading")
            print("   - Consider system resource allocation")
        else:
            print("   - System performing well!")
            print("   - Monitor cache hit rates")
            print("   - Consider load testing for production")


async def main():
    """Main test execution"""
    print("🚀 Ultra-High-Performance BitNet RAG Performance Test")
    print("=" * 60)
    
    tester = PerformanceTester()
    
    # Check system health
    print("🔍 Checking system health...")
    health = tester.check_health()
    
    if not health:
        print("❌ Cannot connect to the system. Is it running on http://localhost:8000?")
        sys.exit(1)
    
    print(f"✅ System healthy:")
    print(f"   Model: {health.get('model', 'Unknown')}")
    print(f"   Native BitNet: {health.get('native_bitnet', False)}")
    print(f"   Current Avg Response Time: {health.get('avg_response_time_ms', 0):.1f}ms")
    print(f"   Cache Hit Rate: {health.get('cache_hit_rate', 0):.1f}%")
    print(f"   Memory Usage: {health.get('memory_mb', 0):.1f}MB")
    
    # Add test documents
    if not tester.add_test_documents():
        print("❌ Failed to add test documents")
        sys.exit(1)
    
    # Run benchmark
    results = tester.run_performance_benchmark(TEST_QUERIES, iterations=3)
    
    # Print report
    tester.print_benchmark_report(results)
    
    # Final recommendation
    summary = results.get("summary", {})
    if summary.get("overall_avg_ms", 1000) <= TARGET_RESPONSE_TIME:
        print(f"\n🎉 SUCCESS: System achieves target performance of {TARGET_RESPONSE_TIME}ms!")
        sys.exit(0)
    elif summary.get("overall_avg_ms", 1000) <= ACCEPTABLE_RESPONSE_TIME:
        print(f"\n✅ GOOD: System achieves acceptable performance of {ACCEPTABLE_RESPONSE_TIME}ms")
        sys.exit(0)
    else:
        print(f"\n⚠️ NEEDS IMPROVEMENT: System performance below acceptable threshold")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())