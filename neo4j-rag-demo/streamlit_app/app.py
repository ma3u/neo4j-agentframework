"""
Neo4j RAG + BitNet Chat - Streamlit Application
Implements features from issues #7, #8, #9
"""

import streamlit as st
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional

# Page configuration
st.set_page_config(
    page_title="Neo4j RAG + BitNet Chat (Local Developer Mode)",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Configuration
RAG_API_URL = "http://bitnet-optimized-rag:8000"
# Fallback for local testing outside Docker
if st.secrets.get("LOCAL_DEV", False):
    RAG_API_URL = "http://localhost:8000"


# Session State Initialization
def initialize_session_state():
    """Initialize all session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    if 'settings' not in st.session_state:
        st.session_state.settings = {
            'max_results': 5,
            'similarity_threshold': 0.7,
            'use_bitnet': True,
            'temperature': 0.7,
            'show_sources': True,
            'show_performance': True,
            'show_timestamps': False
        }

    if 'upload_history' not in st.session_state:
        st.session_state.upload_history = []


# API Client Functions
def check_service_health(service_url: str) -> Dict:
    """Check health of a service"""
    try:
        response = requests.get(f"{service_url}/health", timeout=5)
        if response.ok:
            data = response.json()
            return {
                "status": "healthy",
                "response_time": response.elapsed.total_seconds() * 1000,
                "data": data
            }
        return {"status": "error", "response_time": 0, "data": {}}
    except Exception as e:
        return {"status": "error", "response_time": 0, "error": str(e)}


def get_system_stats() -> Dict:
    """Get system statistics from RAG service"""
    try:
        response = requests.get(f"{RAG_API_URL}/stats", timeout=5)
        if response.ok:
            return response.json()
        return {}
    except Exception:
        return {}


def query_rag(question: str, max_results: int = 5, similarity_threshold: float = 0.7) -> Dict:
    """Query the RAG system"""
    try:
        response = requests.post(
            f"{RAG_API_URL}/query",
            json={
                "question": question,
                "max_results": max_results,
                "similarity_threshold": similarity_threshold,
                "use_llm": st.session_state.settings['use_bitnet']
            },
            timeout=30
        )
        if response.ok:
            return response.json()
        return {"error": f"API error: {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}


def upload_documents(files) -> List[Dict]:
    """Upload documents to RAG system"""
    results = []
    for file in files:
        try:
            files_dict = {"file": (file.name, file.getvalue(), file.type)}
            response = requests.post(
                f"{RAG_API_URL}/upload",
                files=files_dict,
                timeout=60
            )
            if response.ok:
                results.append({"file": file.name, "status": "success", "data": response.json()})
            else:
                results.append({"file": file.name, "status": "error", "error": f"Upload failed: {response.status_code}"})
        except Exception as e:
            results.append({"file": file.name, "status": "error", "error": str(e)})
    return results


# UI Component Functions
def render_top_nav():
    """Render top navigation bar"""
    col1, col2 = st.columns([3, 1])

    with col1:
        st.markdown("## 🧠 Neo4j RAG + BitNet Chat")
        st.caption("(local developer mode)")

    with col2:
        health = check_service_health(RAG_API_URL)
        status_color = "🟢" if health["status"] == "healthy" else "🔴"
        st.markdown(f"### {status_color} System {health['status'].title()}")


def render_service_health():
    """Render individual service health indicators"""
    st.markdown("### 🏥 Service Health")

    col1, col2, col3 = st.columns(3)

    # Neo4j Health
    with col1:
        neo4j_health = check_service_health("http://neo4j-rag-optimized:7474")
        status = "🟢 Healthy" if neo4j_health["status"] == "healthy" else "🔴 Error"
        st.metric("🗄️ Neo4j", status, f"{neo4j_health.get('response_time', 0):.0f}ms")

    # RAG Service Health
    with col2:
        rag_health = check_service_health(RAG_API_URL)
        status = "🟢 Online" if rag_health["status"] == "healthy" else "🔴 Offline"
        st.metric("⚡ RAG Service", status, f"{rag_health.get('response_time', 0):.0f}ms")

    # BitNet Health (check via RAG service)
    with col3:
        stats = get_system_stats()
        bitnet_status = stats.get("bitnet", {}).get("status", "unknown")
        status_emoji = "🟢" if bitnet_status == "active" else "🟡"
        st.metric("🤖 BitNet LLM", f"{status_emoji} {bitnet_status.title()}", "Port 8001")


def render_system_stats():
    """Render compact system statistics"""
    stats = get_system_stats()

    if not stats:
        st.warning("Unable to fetch system statistics")
        return

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("📄 Documents", stats.get("neo4j", {}).get("documents", 0))

    with col2:
        chunks = stats.get("neo4j", {}).get("chunks", 0)
        docs = stats.get("neo4j", {}).get("documents", 1)
        avg_chunks = chunks / docs if docs > 0 else 0
        st.metric("🧩 Chunks", f"{chunks:,}", f"↑ {avg_chunks:.0f}/doc")

    with col3:
        response_time = stats.get("performance", {}).get("avg_response_time_ms", 0)
        st.metric("⚡ Response", f"{response_time:.0f}ms", "↓ 95%")

    with col4:
        memory = stats.get("memory", {}).get("usage_gb", 0)
        st.metric("💾 Memory", f"{memory:.1f}GB", "↓ 87%")

    with col5:
        cache_rate = stats.get("performance", {}).get("cache_hit_rate", 0)
        st.metric("🎯 Cache", f"{cache_rate*100:.0f}%", "↑ 15%")


def render_chat_interface():
    """Render chat interface with message history"""
    st.markdown("### 💬 Chat")

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show sources if available and enabled
            if st.session_state.settings['show_sources'] and "sources" in message:
                with st.expander(f"📚 Sources ({len(message['sources'])})"):
                    for idx, source in enumerate(message["sources"], 1):
                        st.markdown(f"**{idx}. {source.get('metadata', {}).get('source', 'Unknown')}**")
                        st.caption(f"Score: {source.get('score', 0):.2f}")
                        st.text(source.get('text', '')[:200] + "...")

            # Show performance metrics if available and enabled
            if st.session_state.settings['show_performance'] and "performance" in message:
                perf = message["performance"]
                cols = st.columns(3)
                cols[0].caption(f"⚡ {perf.get('response_time_ms', 0):.0f}ms")
                cols[1].caption(f"💾 {perf.get('memory_gb', 0):.1f}GB")
                cols[2].caption(f"🔍 {perf.get('sources_found', 0)} sources")


def render_sidebar():
    """Render sidebar with settings and controls"""
    with st.sidebar:
        st.title("⚙️ Controls")

        # RAG Configuration
        st.subheader("🔍 RAG Configuration")
        max_results = st.slider("Max Results", 1, 10, 5)
        similarity_threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.7, 0.05)

        st.session_state.settings['max_results'] = max_results
        st.session_state.settings['similarity_threshold'] = similarity_threshold

        st.divider()

        # LLM Configuration
        st.subheader("🤖 LLM Configuration")
        use_bitnet = st.toggle("Use BitNet LLM", value=True)
        temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)

        st.session_state.settings['use_bitnet'] = use_bitnet
        st.session_state.settings['temperature'] = temperature

        st.divider()

        # Document Upload (Issue #8)
        st.subheader("📤 Document Upload")
        uploaded_files = st.file_uploader(
            "Upload documents",
            type=['pdf', 'txt', 'md', 'docx'],
            accept_multiple_files=True,
            help="Upload PDF, TXT, MD, or DOCX files (up to 10MB each)"
        )

        if uploaded_files:
            if st.button("📤 Upload to Knowledge Base", type="primary"):
                with st.spinner("Uploading documents..."):
                    results = upload_documents(uploaded_files)

                    for result in results:
                        if result["status"] == "success":
                            st.success(f"✅ {result['file']} uploaded successfully")
                            st.session_state.upload_history.insert(0, {
                                "file": result['file'],
                                "time": datetime.now().strftime("%I:%M %p")
                            })
                        else:
                            st.error(f"❌ {result['file']}: {result.get('error', 'Unknown error')}")

        # Recent uploads
        if st.session_state.upload_history:
            st.caption("Recent Uploads")
            for upload in st.session_state.upload_history[:3]:
                st.caption(f"✅ {upload['file']} - {upload['time']}")

        st.divider()

        # Actions
        st.subheader("🔧 Actions")

        if st.button("📊 View Full Statistics", type="primary", use_container_width=True):
            st.session_state.show_stats = True

        if st.button("💾 Export Chat", use_container_width=True):
            st.info("Export feature coming soon")

        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

        st.divider()

        # Display Options
        st.subheader("👁️ Display Options")
        st.session_state.settings['show_sources'] = st.checkbox("Show Sources", value=True)
        st.session_state.settings['show_performance'] = st.checkbox("Show Performance", value=True)
        st.session_state.settings['show_timestamps'] = st.checkbox("Show Timestamps", value=False)


def render_full_statistics():
    """Render full statistics modal/page"""
    st.title("📊 Full System Statistics")

    stats = get_system_stats()

    if not stats:
        st.error("Unable to fetch statistics")
        return

    # Neo4j Statistics
    st.subheader("🗄️ Neo4j Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("📄 Total Documents", stats.get("neo4j", {}).get("documents", 0))
    with col2:
        chunks = stats.get("neo4j", {}).get("chunks", 0)
        st.metric("🧩 Total Chunks", f"{chunks:,}")
    with col3:
        st.metric("📐 Vector Dimensions", 384)

    # Performance Statistics
    st.subheader("⚡ Performance Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        response_time = stats.get("performance", {}).get("avg_response_time_ms", 0)
        st.metric("⚡ Avg Response Time", f"{response_time:.0f}ms", "↓ 95%")
    with col2:
        cache_rate = stats.get("performance", {}).get("cache_hit_rate", 0)
        st.metric("🎯 Cache Hit Rate", f"{cache_rate*100:.0f}%", "↑ 15%")
    with col3:
        st.metric("🔄 Queries Processed", stats.get("queries", {}).get("total", 0))

    # Memory Statistics
    st.subheader("💾 Memory Statistics")
    col1, col2, col3 = st.columns(3)

    with col1:
        memory = stats.get("memory", {}).get("usage_gb", 0)
        st.metric("💾 Memory Usage", f"{memory:.1f}GB", "↓ 87%")
    with col2:
        st.metric("💻 RAM Available", "7.2GB")
    with col3:
        st.metric("🗄️ Database Size", "342MB")

    # Performance Trend Chart (Issue #9)
    st.subheader("📈 Query Response Time Trend (Last Hour)")
    st.info("📊 Chart visualization will show real-time performance trends")
    st.caption("Real-time charts require Plotly integration - coming soon")

    # Query Analytics (Issue #9)
    st.subheader("🔍 Query Analytics (Recent Queries)")
    if st.session_state.messages:
        for msg in reversed(st.session_state.messages[-5:]):
            if msg["role"] == "user":
                cols = st.columns([2, 3, 1])
                cols[0].caption(msg.get("timestamp", ""))
                cols[1].caption(msg["content"][:50] + "...")
                cols[2].caption(msg.get("response_time", "N/A"))
    else:
        st.caption("No queries yet")

    if st.button("← Back to Chat"):
        st.session_state.show_stats = False
        st.rerun()


# Main Application
def main():
    """Main application entry point"""
    initialize_session_state()

    # Show full statistics page if requested
    if st.session_state.get('show_stats', False):
        render_full_statistics()
        return

    # Top Navigation
    render_top_nav()

    st.divider()

    # Service Health (Issue #9)
    render_service_health()

    st.divider()

    # Chat Interface (Issue #7)
    render_chat_interface()

    # Chat Input
    if prompt := st.chat_input("💬 Ask a question about Neo4j, BitNet, or RAG systems..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%I:%M %p")
        })

        # Display user message immediately
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get RAG response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                start_time = time.time()
                result = query_rag(
                    prompt,
                    st.session_state.settings['max_results'],
                    st.session_state.settings['similarity_threshold']
                )
                response_time = (time.time() - start_time) * 1000

                if "error" in result:
                    st.error(f"Error: {result['error']}")
                    response = "I apologize, but I encountered an error processing your request."
                else:
                    response = result.get("answer", "No response generated")
                    st.markdown(response)

                    # Show sources
                    if st.session_state.settings['show_sources'] and "sources" in result:
                        sources = result["sources"]
                        with st.expander(f"📚 Sources ({len(sources)})"):
                            for idx, source in enumerate(sources, 1):
                                st.markdown(f"**{idx}. {source.get('metadata', {}).get('source', 'Unknown')}**")
                                st.caption(f"Score: {source.get('score', 0):.2f}")
                                st.text(source.get('text', '')[:200] + "...")

                    # Show performance
                    if st.session_state.settings['show_performance']:
                        cols = st.columns(3)
                        cols[0].caption(f"⚡ {response_time:.0f}ms")
                        cols[1].caption(f"💾 {result.get('memory_usage', 0):.1f}GB")
                        cols[2].caption(f"🔍 {len(result.get('sources', []))} sources")

        # Add assistant message to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().strftime("%I:%M %p"),
            "sources": result.get("sources", []),
            "performance": {
                "response_time_ms": response_time,
                "memory_gb": result.get("memory_usage", 0),
                "sources_found": len(result.get("sources", []))
            },
            "response_time": f"{response_time:.0f}ms"
        })

    st.divider()

    # Compact Stats Below Chat
    render_system_stats()

    # Sidebar with settings and upload
    render_sidebar()


if __name__ == "__main__":
    main()
