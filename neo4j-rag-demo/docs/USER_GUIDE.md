# Neo4j BitNet RAG User Guide

## Overview
Complete BitNet RAG usage guide with API reference.

## Using the API
The API provides the following endpoints:

### Health Check
- **GET** `/health` - Check system health and status

### Query RAG
- **POST** `/query` - Query the RAG system
- **POST** `/search` - Vector similarity search

### Statistics  
- **GET** `/stats` - Get system statistics
- **GET** `/model-info` - Get model information

## Configuration
Environment variables and settings for the RAG system:

- `NEO4J_URI` - Neo4j database URI
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `PYTHONPATH` - Python path configuration

## Troubleshooting
Common issues and solutions:

### Connection Issues
- Check Docker containers are running
- Verify Neo4j is accessible on port 7687
- Ensure network connectivity between containers

### Performance Issues  
- Check memory usage with `/stats` endpoint
- Review query cache hit rates
- Monitor embedding coverage

### Data Issues
- Use Data Quality Check queries from Neo4j Browser
- Verify document uploads completed successfully
- Check chunk embedding coverage

## Examples
See the `/examples` directory for code samples and usage patterns.

---

*This is a placeholder file. Complete documentation will be added in future updates.*