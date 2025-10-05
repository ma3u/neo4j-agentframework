# System Architecture

**Complete technical architecture for Neo4j RAG + BitNet + Azure Agent Framework**

---

## 📐 High-Level Architecture

```mermaid
graph TB
    subgraph "Document Processing Layer"
        PDF[PDF Documents]
        Docling[Docling Loader<br/>Advanced PDF Processing]
        Parser[Document Parser<br/>Tables, Images, Structure]
        Chunker[Text Chunker<br/>300 chars, 50 overlap]

        PDF -->|Upload| Docling
        Docling -->|Extract| Parser
        Parser -->|Split| Chunker
        Chunker -->|Chunks| Store
    end

    subgraph "Storage Layer"
        Store[Document Store]
        Neo4j[(Neo4j Graph DB<br/>5.11+)]
        DocNode[Document Nodes]
        ChunkNode[Chunk Nodes]

        Store -->|Create| DocNode
        DocNode -->|HAS_CHUNK| ChunkNode
        Neo4j -.->|Contains| DocNode
        Neo4j -.->|Contains| ChunkNode
    end

    subgraph "Indexing Layer"
        Embedder[SentenceTransformer<br/>all-MiniLM-L6-v2]
        VectorIdx[Vector Index<br/>384-dimensional]
        FullTextIdx[Full-Text Index<br/>Keyword Search]

        ChunkNode -->|Embed| Embedder
        Embedder -->|384-dim vector| VectorIdx
        ChunkNode -->|Index Text| FullTextIdx
    end

    subgraph "Query Processing Layer"
        UserQuery[User Query]
        QueryEmbed[Query Embedding]
        VectorSearch[Vector Search<br/>Cosine Similarity]
        KeywordSearch[Keyword Search<br/>Full-Text]
        HybridSearch[Hybrid Search<br/>Alpha = 0.5]
        Cache[Query Cache<br/>FIFO 100 entries]

        UserQuery -->|Check| Cache
        Cache -->|Miss| QueryEmbed
        QueryEmbed -->|Search| VectorSearch
        QueryEmbed -->|Search| KeywordSearch
        VectorSearch -->|Results| HybridSearch
        KeywordSearch -->|Results| HybridSearch
        Cache -->|Hit| Context
    end

    subgraph "Retrieval Layer"
        VectorIdx -.->|Top-K| VectorSearch
        FullTextIdx -.->|Match| KeywordSearch
        HybridSearch -->|Rerank| Context[Retrieved Context<br/>Top-K Chunks]
    end

    subgraph "LLM Inference Layer"
        Context -->|Augment| BitNet
        BitNet[BitNet.cpp<br/>1.58-bit Quantized]
        LlamaEngine[llama-cli Binary<br/>ARM TL1 Kernels]
        Model[GGUF Model<br/>1.11GB]

        BitNet -->|Invoke| LlamaEngine
        LlamaEngine -.->|Load| Model
        LlamaEngine -->|Generate| Answer[Generated Answer<br/>2-5s inference]
    end

    subgraph "Azure Integration Layer (Optional)"
        Answer -->|Optional| AgentFramework
        AgentFramework[Azure AI Agent<br/>Microsoft Agent Framework]
        AzureAI[Azure AI Foundry<br/>GPT-4o-mini]
        ManagedIdentity[Managed Identity<br/>Authentication]

        AgentFramework -->|Authenticate| ManagedIdentity
        ManagedIdentity -->|Access| AzureAI
        AzureAI -->|Enhanced Response| FinalResponse[Final Response]
    end

    UserQuery -.->|Direct| AgentFramework
    HybridSearch -->|Stats| Cache

    style Docling fill:#e1f5ff,stroke:#0066cc,stroke-width:2px
    style Neo4j fill:#4db8ff,stroke:#0066cc,stroke-width:2px
    style BitNet fill:#ffcccc,stroke:#cc0000,stroke-width:2px
    style AgentFramework fill:#ccffcc,stroke:#00cc00,stroke-width:2px
    style Cache fill:#ffffcc,stroke:#cccc00,stroke-width:2px
```

---

## 🔧 Component Architecture

### 1. Document Processing Pipeline

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI Server
    participant Docling as Docling Loader
    participant Parser as Document Parser
    participant RAG as Neo4j RAG
    participant Neo4j as Neo4j Database

    User->>API: Upload PDF
    API->>Docling: Process Document
    Docling->>Parser: Extract Content
    Parser->>Parser: Parse Tables & Images
    Parser->>Parser: Extract Structure
    Parser->>RAG: Send Chunks
    RAG->>RAG: Generate Embeddings
    RAG->>Neo4j: Store Document & Chunks
    Neo4j->>Neo4j: Create Indexes
    Neo4j-->>API: Success
    API-->>User: Upload Complete
```

**Components:**
- **Docling Loader**: Advanced PDF processing with table/image extraction
- **Document Parser**: Extracts structure, metadata, and content
- **Text Chunker**: RecursiveCharacterTextSplitter (300 chars, 50 overlap)
- **Embedding Generator**: SentenceTransformer (all-MiniLM-L6-v2)

### 2. Query Processing Pipeline

```mermaid
sequenceDiagram
    participant User
    participant API as FastAPI Server
    participant Cache as Query Cache
    participant RAG as RAG Engine
    participant Neo4j as Neo4j Database
    participant BitNet as BitNet.cpp
    participant Agent as Azure Agent (Optional)

    User->>API: Query Request
    API->>Cache: Check Cache
    alt Cache Hit
        Cache-->>API: Cached Result
    else Cache Miss
        API->>RAG: Process Query
        RAG->>RAG: Generate Query Embedding
        RAG->>Neo4j: Vector Search
        RAG->>Neo4j: Keyword Search
        Neo4j-->>RAG: Search Results
        RAG->>RAG: Hybrid Ranking
        RAG->>Cache: Store Result
        RAG-->>API: Retrieved Context

        alt Use LLM
            API->>BitNet: Generate with Context
            BitNet-->>API: Generated Answer
        end

        alt Azure Integration
            API->>Agent: Enhance with GPT-4o
            Agent-->>API: Final Response
        end
    end
    API-->>User: Response
```

**Components:**
- **Query Cache**: FIFO cache with 100 entries (thread-safe)
- **Vector Search**: Cosine similarity on 384-dim embeddings
- **Keyword Search**: Full-text index matching
- **Hybrid Search**: Weighted combination (alpha=0.5)
- **Connection Pool**: 10 max connections to Neo4j

### 3. BitNet Inference Architecture

```mermaid
graph LR
    subgraph "BitNet Container"
        Server[FastAPI Server<br/>Port 8001]
        Wrapper[Python Wrapper]
        Binary[llama-cli Binary]
        Kernels[ARM TL1 Kernels<br/>Optimized Lookup Tables]
        Model[GGUF Model<br/>1.11GB i2_s quantized]
    end

    Input[Context + Prompt] -->|HTTP POST| Server
    Server -->|Invoke| Wrapper
    Wrapper -->|Execute| Binary
    Binary -.->|Load| Model
    Binary -.->|Use| Kernels
    Binary -->|Generate| Output[Text Generation]
    Output -->|HTTP Response| Result[Generated Answer]

    style Binary fill:#ffcccc
    style Model fill:#ffe6e6
    style Kernels fill:#fff0f0
```

**Components:**
- **FastAPI Server**: REST API for LLM inference
- **llama-cli Binary**: Compiled with clang-18, ARM optimizations
- **TL1 Kernels**: Generated by `codegen_tl1.py`
- **GGUF Model**: 1.58-bit ternary quantization (-1, 0, +1)

---

## 🏗️ Deployment Architecture

### Local Deployment

```mermaid
graph TB
    subgraph "Docker Desktop"
        subgraph "Neo4j Container"
            Neo4jDB[Neo4j Database<br/>Port 7474, 7687]
        end

        subgraph "RAG Service Container"
            RAGApp[FastAPI App<br/>Port 8000]
            SentTrans[SentenceTransformer]
            RAGEngine[RAG Engine]
        end

        subgraph "BitNet Container"
            BitNetApp[FastAPI App<br/>Port 8001]
            LlamaCLI[llama-cli]
            BitNetModel[GGUF Model 1.11GB]
        end

        Network[Docker Network<br/>rag-network]
    end

    Client[Browser/API Client] -->|HTTP| RAGApp
    RAGApp <-->|Bolt| Neo4jDB
    RAGApp -->|HTTP| BitNetApp

    Neo4jDB -.->|Network| Network
    RAGApp -.->|Network| Network
    BitNetApp -.->|Network| Network

    style Neo4jDB fill:#4db8ff
    style RAGApp fill:#e1f5ff
    style BitNetApp fill:#ffcccc
```

**Resources:**
- **Neo4j**: 4GB heap, 2GB pagecache
- **RAG Service**: 2GB RAM, 1 CPU
- **BitNet**: 2GB RAM, 1 CPU
- **Total**: ~6GB RAM, 3 CPUs

### Azure Production Deployment

```mermaid
graph TB
    subgraph "Azure Container Apps Environment"
        subgraph "Container Registry"
            ACR[Azure Container Registry<br/>crneo4jrag*.azurecr.io]
            Neo4jImg[neo4j:5.11]
            RAGImg[neo4j-rag:v1.0]
            BitNetImg[bitnet-llm:v1.0]
            AgentImg[neo4j-agent:v1.0]
        end

        subgraph "Container Apps"
            Neo4jApp[Neo4j Database<br/>Internal Only<br/>4 CPU, 8GB]
            RAGApp[RAG Service<br/>External HTTPS<br/>2 CPU, 4GB<br/>0-10 replicas]
            BitNetApp[BitNet LLM<br/>Internal Only<br/>2 CPU, 4GB<br/>1-3 replicas]
            AgentApp[Agent Framework<br/>External HTTPS<br/>2 CPU, 4GB<br/>0-10 replicas]
        end

        subgraph "Azure AI Services"
            AzureAI[Azure AI Foundry<br/>GPT-4o-mini]
            ManagedID[Managed Identity]
        end

        LB[Azure Load Balancer]
        LogAnalytics[Log Analytics Workspace]
    end

    Internet[Internet] -->|HTTPS| LB
    LB -->|Route| RAGApp
    LB -->|Route| AgentApp

    RAGApp <-->|Bolt| Neo4jApp
    RAGApp -->|HTTP| BitNetApp
    AgentApp -->|HTTP| RAGApp
    AgentApp -->|Authenticate| ManagedID
    ManagedID -->|Access| AzureAI

    ACR -.->|Pull| Neo4jApp
    ACR -.->|Pull| RAGApp
    ACR -.->|Pull| BitNetApp
    ACR -.->|Pull| AgentApp

    Neo4jApp -->|Logs| LogAnalytics
    RAGApp -->|Logs| LogAnalytics
    BitNetApp -->|Logs| LogAnalytics
    AgentApp -->|Logs| LogAnalytics

    style AzureAI fill:#ccffcc
    style ACR fill:#e6e6ff
    style LB fill:#ffe6cc
```

**Azure Resources:**
- **Resource Group**: rg-neo4j-rag-bitnet
- **Container Registry**: Basic SKU
- **Container Apps Environment**: With Log Analytics
- **Managed Identity**: For secure authentication
- **Auto-scaling**: HTTP-based scaling (0-10 instances)

---

## 📊 Data Flow Architecture

### End-to-End Data Flow

```mermaid
flowchart LR
    subgraph Input
        PDF[PDF Document<br/>50 pages]
    end

    subgraph Processing
        Docling[Docling<br/>Extract 150 chunks]
        Embed[Embed<br/>150 × 384-dim vectors]
    end

    subgraph Storage
        Neo4j[Neo4j<br/>1 Doc + 150 Chunks<br/>+ Indexes]
    end

    subgraph Query
        Q[User Query<br/>"What is Neo4j?"]
        QEmbed[Query Vector<br/>384-dim]
        Search[Search<br/>Top-5 results]
    end

    subgraph Generation
        Context[5 chunks context<br/>~1500 chars]
        BitNet[BitNet Generate<br/>2-5s inference]
        Answer[Answer<br/>200 tokens]
    end

    PDF -->|50 pages| Docling
    Docling -->|150 chunks| Embed
    Embed -->|Store| Neo4j
    Q -->|Encode| QEmbed
    QEmbed -->|Search| Neo4j
    Neo4j -->|Retrieve| Search
    Search -->|Top-5| Context
    Context -->|Augment| BitNet
    BitNet -->|Generate| Answer

    style Docling fill:#e1f5ff
    style Neo4j fill:#4db8ff
    style BitNet fill:#ffcccc
```

**Performance Metrics:**
- **Upload**: 50-page PDF → 2-3s per page → 100-150s total
- **Storage**: 150 chunks × 384-dim → ~230KB embeddings
- **Query**: Encoding 10ms + Search 20ms + Rerank 10ms = 40ms
- **Generation**: Context 1500 chars → BitNet 2-5s → 200 tokens
- **Total**: ~3-6s end-to-end (query + generation)

---

## 🔒 Security Architecture

```mermaid
graph TB
    subgraph "Security Layers"
        subgraph "Network Security"
            HTTPS[HTTPS/TLS<br/>Encrypted Transport]
            Internal[Internal Network<br/>Container Isolation]
            Firewall[Azure Firewall<br/>IP Restrictions]
        end

        subgraph "Authentication & Authorization"
            ManagedID[Managed Identity<br/>No Credentials]
            RBAC[Azure RBAC<br/>Role-Based Access]
            Neo4jAuth[Neo4j Auth<br/>Username/Password]
        end

        subgraph "Data Security"
            Encryption[Data Encryption<br/>At Rest & In Transit]
            Secrets[Azure Key Vault<br/>Secret Management]
            Backup[Automated Backups<br/>Point-in-Time Recovery]
        end

        subgraph "Application Security"
            InputVal[Input Validation<br/>FastAPI Pydantic]
            RateLimit[Rate Limiting<br/>DDoS Protection]
            Logging[Audit Logging<br/>Log Analytics]
        end
    end

    Internet[External Traffic] -->|443| HTTPS
    HTTPS -->|Validate| InputVal
    InputVal -->|Check| RateLimit
    RateLimit -->|Route| Internal
    Internal -->|Authenticate| ManagedID
    ManagedID -->|Authorize| RBAC
    RBAC -->|Access| Secrets
    Secrets -.->|Provide| Neo4jAuth
    Internal -->|Log| Logging

    style HTTPS fill:#ccffcc
    style ManagedID fill:#e6e6ff
    style Encryption fill:#ffe6cc
```

---

## 📈 Scaling Architecture

### Horizontal Scaling

```mermaid
graph TB
    subgraph "Auto-Scaling Configuration"
        LB[Azure Load Balancer]

        subgraph "RAG Instances"
            RAG1[RAG Service #1]
            RAG2[RAG Service #2]
            RAGn[RAG Service #N<br/>Max 10]
        end

        subgraph "BitNet Instances"
            BitNet1[BitNet #1]
            BitNet2[BitNet #2]
            BitNet3[BitNet #3<br/>Max 3]
        end

        ConnectionPool[Neo4j Connection Pool<br/>10 max connections]
        Neo4jDB[(Neo4j Database<br/>Single Instance)]
    end

    LB -->|Round Robin| RAG1
    LB -->|Round Robin| RAG2
    LB -->|Round Robin| RAGn

    RAG1 -->|Pool| ConnectionPool
    RAG2 -->|Pool| ConnectionPool
    RAGn -->|Pool| ConnectionPool

    ConnectionPool <-->|Bolt| Neo4jDB

    RAG1 -->|HTTP| BitNet1
    RAG2 -->|HTTP| BitNet2
    RAGn -->|HTTP| BitNet3

    style LB fill:#ffe6cc
    style Neo4jDB fill:#4db8ff
    style ConnectionPool fill:#ffffcc
```

**Scaling Triggers:**
- **RAG Service**: HTTP concurrency > 10 requests
- **BitNet Service**: CPU > 70% or Memory > 80%
- **Scale-down**: After 5 minutes of low traffic
- **Cool-down**: 3 minutes between scale events

---

## 🔗 Integration Patterns

### API Integration

```mermaid
sequenceDiagram
    participant Client
    participant RAG as RAG Service
    participant Neo4j
    participant BitNet
    participant Agent as Azure Agent (Optional)

    Client->>RAG: POST /query
    activate RAG

    RAG->>RAG: Validate Request
    RAG->>RAG: Check Cache

    alt Cache Miss
        RAG->>Neo4j: Vector + Keyword Search
        activate Neo4j
        Neo4j-->>RAG: Top-K Results
        deactivate Neo4j

        RAG->>RAG: Hybrid Ranking

        alt Use BitNet
            RAG->>BitNet: Generate with Context
            activate BitNet
            BitNet-->>RAG: Generated Answer
            deactivate BitNet
        end

        alt Azure Enhancement
            RAG->>Agent: Enhance Response
            activate Agent
            Agent-->>RAG: Final Answer
            deactivate Agent
        end

        RAG->>RAG: Cache Result
    end

    RAG-->>Client: JSON Response
    deactivate RAG
```

---

## 📚 Related Documentation

- [**📖 Documentation Index**](README.md) - Complete documentation map
- [**🏗️ Azure Architecture**](AZURE_ARCHITECTURE.md) - Azure-specific architecture
- [**📊 Performance Analysis**](performance_analysis.md) - Performance benchmarks
- [**🚀 Quick Start Guide**](README-QUICKSTART.md) - Getting started
- [**📖 Main README**](../README.md) - Project overview

---

**Last Updated**: 2025-10-05
**Version**: 1.0
**Status**: Production Ready
