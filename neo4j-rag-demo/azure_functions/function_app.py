import azure.functions as func
import logging
import json
import requests
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Azure RAG Service URL
AZURE_RAG_URL = "https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io"

@app.route(route="search_knowledge_base")
def search_knowledge_base(req: func.HttpRequest) -> func.HttpResponse:
    """Search the Neo4j knowledge base"""
    logging.info('Search knowledge base function triggered.')
    
    try:
        # Get request data
        req_body = req.get_json()
        question = req_body.get('question', '')
        max_results = req_body.get('max_results', 5)
        
        if not question:
            return func.HttpResponse(
                json.dumps({"error": "Question parameter is required"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Call Azure RAG service
        response = requests.post(
            f"{AZURE_RAG_URL}/search_knowledge_base",
            json={
                "question": question,
                "max_results": max_results
            },
            timeout=30
        )
        
        response.raise_for_status()
        result = response.json()
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except requests.exceptions.RequestException as e:
        logging.error(f"RAG service error: {e}")
        return func.HttpResponse(
            json.dumps({"error": f"RAG service error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Function error: {e}")
        return func.HttpResponse(
            json.dumps({"error": f"Function error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="get_knowledge_base_statistics")
def get_knowledge_base_statistics(req: func.HttpRequest) -> func.HttpResponse:
    """Get knowledge base statistics"""
    logging.info('Get knowledge base statistics function triggered.')
    
    try:
        # Call Azure RAG service
        response = requests.get(
            f"{AZURE_RAG_URL}/get_knowledge_base_statistics",
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except requests.exceptions.RequestException as e:
        logging.error(f"RAG service error: {e}")
        return func.HttpResponse(
            json.dumps({"error": f"RAG service error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Function error: {e}")
        return func.HttpResponse(
            json.dumps({"error": f"Function error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="check_knowledge_base_health")
def check_knowledge_base_health(req: func.HttpRequest) -> func.HttpResponse:
    """Check knowledge base health"""
    logging.info('Check knowledge base health function triggered.')
    
    try:
        # Call Azure RAG service
        response = requests.get(
            f"{AZURE_RAG_URL}/check_knowledge_base_health",
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return func.HttpResponse(
            json.dumps(result),
            status_code=200,
            mimetype="application/json"
        )
        
    except requests.exceptions.RequestException as e:
        logging.error(f"RAG service error: {e}")
        return func.HttpResponse(
            json.dumps({"error": f"RAG service error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Function error: {e}")
        return func.HttpResponse(
            json.dumps({"error": f"Function error: {str(e)}"}),
            status_code=500,
            mimetype="application/json"
        )