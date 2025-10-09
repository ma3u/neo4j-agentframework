# Fix UI Issues - Step-by-Step Guide

**Addresses**: Design differences and non-functional live data display

## Issues Identified

1. ❌ Live data not showing (document/chunk counts show "N/A")
2. ❌ Stats API returns wrong data structure
3. ❌ Health cards use wrong hostnames for local testing
4. ⚠️ Design differs from mockup (Streamlit framework limitations)
5. ❌ No sample data loaded in database

## Step-by-Step Fixes

### Fix 1: Update Streamlit to Read Correct Stats Format

The stats API currently returns:
```json
{
  "profiler_stats": {
    "total_query": { "avg_ms": 124.67 }
  },
  "cache_stats": { "hit_rate_percent": 35.71 },
  "system_stats": { "memory_usage_mb": 515.4 }
}
```

**File**: `streamlit_app/app.py:178-217`

**Current (Broken)**:
```python
doc_count = stats.get("document_count", 0)  # ❌ Doesn't exist
chunk_count = stats.get("chunk_count", 0)   # ❌ Doesn't exist
response_time = stats.get("avg_response_time_ms", 0)  # ❌ Wrong path
memory_mb = stats.get("memory_mb", 0)       # ❌ Wrong path
cache_rate = stats.get("cache_hit_rate", 0) # ❌ Wrong path
```

**Fixed**:
```python
# Read from nested structure
doc_count = stats.get("neo4j_stats", {}).get("documents", 0)
chunk_count = stats.get("neo4j_stats", {}).get("chunks", 0)
response_time = stats.get("profiler_stats", {}).get("total_query", {}).get("avg_ms", 0)
memory_mb = stats.get("system_stats", {}).get("memory_usage_mb", 0)
cache_rate = stats.get("cache_stats", {}).get("hit_rate_percent", 0)
```

---

### Fix 2: Update app_local.py Stats Endpoint

**File**: `app_local.py:108-158`

**Add document/chunk counts to response**:

```python
@app.get("/stats")
async def get_stats():
    # Get Neo4j stats (includes documents and chunks)
    neo4j_stats = rag_engine.rag.get_stats()  # Returns {documents, chunks, avg_chunks_per_doc}

    return {
        # ... existing stats ...
        "neo4j_stats": neo4j_stats,  # ✅ Add this
        "document_count": neo4j_stats.get("documents", 0),  # ✅ Flat access
        "chunk_count": neo4j_stats.get("chunks", 0),        # ✅ Flat access
    }
```

---

### Fix 3: Fix Service Hostnames for Local Testing

**File**: `streamlit_app/app.py:152-204`

**Current (Broken)**:
```python
neo4j_health = check_service_health("http://neo4j-rag-optimized:7474")  # ❌ Docker hostname
```

**Fixed**:
```python
# Try localhost first for local development
neo4j_health = check_service_health("http://localhost:7474")
```

**Or use auto-detection**:
```python
def get_service_url(service_name, local_port, docker_hostname):
    # Try localhost first
    try:
        response = requests.get(f"http://localhost:{local_port}", timeout=1)
        if response.ok:
            return f"http://localhost:{local_port}"
    except:
        return f"http://{docker_hostname}:{local_port}"
```

---

### Fix 4: Load Sample Data

**No data in database = no stats to display**

**Run**:
```bash
cd scripts
python load_sample_data.py
```

**Or add documents manually**:
```bash
curl -X POST http://localhost:8000/upload \
  -F "file=@path/to/document.pdf"
```

**Or via Streamlit UI**:
1. Open http://localhost:8501
2. Sidebar → Document Upload
3. Select file
4. Click "Upload to Knowledge Base"

---

### Fix 5: Add Custom Theme

**Create**: `streamlit_app/.streamlit/config.toml`

```toml
[theme]
base = "dark"
primaryColor = "#FF4B4B"
backgroundColor = "#0E1117"
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
font = "sans serif"

[server]
headless = true
port = 8501
```

This will match the mockup colors:
- Background: #0E1117 ✅
- Secondary: #262730 ✅
- Accent: #FF4B4B ✅

---

## Design Limitations (Streamlit vs Custom HTML)

### What Streamlit Can't Do:

1. **Glassmorphic Effects**
   - Mockup: Blur, transparency, backdrop-filter
   - Streamlit: No native support
   - Workaround: Custom CSS (limited)

2. **Custom Animations**
   - Mockup: Pulsing dots, floating emojis, smooth transitions
   - Streamlit: Basic transitions only
   - Workaround: Minimal CSS animations

3. **Gradient Backgrounds**
   - Mockup: Linear gradients on messages
   - Streamlit: Solid colors only
   - Workaround: CSS gradients (limited scope)

4. **Custom Typography**
   - Mockup: Custom font families and weights
   - Streamlit: System fonts
   - Workaround: config.toml font setting (limited options)

### What Can Be Matched:

1. ✅ **Layout Structure**: Same component organization
2. ✅ **Color Scheme**: Via config.toml theme
3. ✅ **Functionality**: All features implemented
4. ✅ **Responsive Design**: Works across viewports
5. ✅ **Component Placement**: Matches mockup

---

## Testing After Fixes

### 1. Verify Stats API
```bash
curl http://localhost:8000/stats | python3 -m json.tool

# Should show:
# - document_count: <number>
# - chunk_count: <number>
# - avg_response_time_ms: <number>
# - cache_hit_rate: <number>
# - memory_mb: <number>
```

### 2. Verify Streamlit Displays Live Data
```bash
open http://localhost:8501

# Check stats row shows:
# - 📄 Documents: <number> (not "N/A")
# - 🧩 Chunks: <number> (not "N/A")
# - ⚡ Response: <number>ms
# - 💾 Memory: <number>GB
# - 🎯 Cache: <number>%
```

### 3. Test Health Cards
```bash
# Should show:
# - 🗄️ Neo4j: 🟢 Connected (Port 7687 or response time)
# - ⚡ RAG Service: 🟢 Online (<number>ms)
# - 🤖 BitNet LLM: Status (Port 8001 or response time)
```

### 4. Test Chat with Data
```bash
# Send query via UI:
"What is Neo4j?"

# Should return:
# - Answer from documents
# - Sources displayed
# - Performance metrics shown
```

---

## Automated Fix Script

I'll create `fix_ui_and_test.sh` that will:

1. ✅ Update app_local.py stats endpoint
2. ✅ Update Streamlit app data mapping
3. ✅ Create theme config file
4. ✅ Load sample data
5. ✅ Restart services
6. ✅ Run tests to verify
7. ✅ Generate updated comparison report

**Run**:
```bash
./fix_ui_and_test.sh
```

---

## Manual Fix Checklist

If you want to fix manually:

- [ ] Update `app_local.py:108-158` - Add document_count, chunk_count to stats response
- [ ] Update `streamlit_app/app.py:178-217` - Read from correct nested paths
- [ ] Update `streamlit_app/app.py:152-204` - Use localhost hostnames
- [ ] Create `streamlit_app/.streamlit/config.toml` - Add mockup theme colors
- [ ] Run `scripts/load_sample_data.py` - Load test data
- [ ] Restart RAG API: `python app_local.py`
- [ ] Restart Streamlit: `streamlit run streamlit_app/app.py`
- [ ] Test: Open http://localhost:8501 and verify live data shows

---

## Expected Result After Fixes

### Stats Display (Before → After)
```
Before:
📄 Documents: N/A
🧩 Chunks: N/A
⚡ Response: N/A
💾 Memory: N/A
🎯 Cache: N/A

After:
📄 Documents: 8
🧩 Chunks: 247
⚡ Response: 125ms ↓ 95%
💾 Memory: 0.5GB ↓ 87%
🎯 Cache: 36% ↑ Good
```

### Health Cards (Before → After)
```
Before:
🗄️ Neo4j: 🔴 Error (0ms)
⚡ RAG Service: 🟢 Online (0ms)
🤖 BitNet LLM: 🟡 Unknown (Port 8001)

After:
🗄️ Neo4j: 🟢 Connected (Port 7687)
⚡ RAG Service: 🟢 Online (45ms)
🤖 BitNet LLM: 🟡 Offline (Port 8001)
```

---

**Created**: 2025-10-08
**Status**: Issues documented, fixes ready to apply
**Next**: Run automated fix script or apply manual fixes
