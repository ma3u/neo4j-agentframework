import azure.functions as func
import json
import logging
import aiohttp
import asyncio

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

# Configuration
CONTAINER_APP_BASE_URL = "https://neo4j-rag-agent.yellowtree-8fdce811.swedencentral.azurecontainerapps.io"

@app.route(route="search_knowledge_base", methods=["POST"])
async def search_knowledge_base(req: func.HttpRequest) -> func.HttpResponse:
    """Route search_knowledge_base calls to Container App"""
    
    logging.info('Processing search_knowledge_base request')
    
    try:
        # Get request data from Azure OpenAI Assistant
        req_body = req.get_json()
        question = req_body.get('question', req_body.get('query', ''))
        max_results = req_body.get('max_results', req_body.get('k', 5))
        use_llm = req_body.get('use_llm', False)
        
        # Forward to Container App
        async with aiohttp.ClientSession() as session:
            payload = {
                "question": question,
                "max_results": max_results,
                "use_llm": use_llm
            }
            
            async with session.post(
                f"{CONTAINER_APP_BASE_URL}/search_knowledge_base",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                
                # Return result in format expected by Azure OpenAI
                return func.HttpResponse(
                    json.dumps(result),
                    status_code=200,
                    mimetype="application/json"
                )
                
    except Exception as e:
        logging.error(f"Error in search_knowledge_base: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="add_document_to_knowledge_base", methods=["POST"])
async def add_document_to_knowledge_base(req: func.HttpRequest) -> func.HttpResponse:
    """Route add_document_to_knowledge_base calls to Container App"""
    
    logging.info('Processing add_document_to_knowledge_base request')
    
    try:
        req_body = req.get_json()
        content = req_body.get('content', '')
        source = req_body.get('source', 'user_upload')
        metadata = req_body.get('metadata', {})
        
        # Forward to Container App
        async with aiohttp.ClientSession() as session:
            payload = {
                "content": content,
                "source": source,
                "metadata": metadata
            }
            
            async with session.post(
                f"{CONTAINER_APP_BASE_URL}/add_document_to_knowledge_base",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                
                return func.HttpResponse(
                    json.dumps(result),
                    status_code=200,
                    mimetype="application/json"
                )
                
    except Exception as e:
        logging.error(f"Error in add_document_to_knowledge_base: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="get_knowledge_base_statistics", methods=["GET", "POST"])
async def get_knowledge_base_statistics(req: func.HttpRequest) -> func.HttpResponse:
    """Route get_knowledge_base_statistics calls to Container App"""
    
    logging.info('Processing get_knowledge_base_statistics request')
    
    try:
        # Forward to Container App
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{CONTAINER_APP_BASE_URL}/get_knowledge_base_statistics",
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                
                return func.HttpResponse(
                    json.dumps(result),
                    status_code=200,
                    mimetype="application/json"
                )
                
    except Exception as e:
        logging.error(f"Error in get_knowledge_base_statistics: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="check_knowledge_base_health", methods=["GET", "POST"])
async def check_knowledge_base_health(req: func.HttpRequest) -> func.HttpResponse:
    """Route check_knowledge_base_health calls to Container App"""
    
    logging.info('Processing check_knowledge_base_health request')
    
    try:
        # Forward to Container App
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{CONTAINER_APP_BASE_URL}/check_knowledge_base_health",
                headers={"Content-Type": "application/json"}
            ) as response:
                result = await response.json()
                
                return func.HttpResponse(
                    json.dumps(result),
                    status_code=200,
                    mimetype="application/json"
                )
                
    except Exception as e:
        logging.error(f"Error in check_knowledge_base_health: {str(e)}")
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )