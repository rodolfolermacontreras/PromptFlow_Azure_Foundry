"""
Search products node for Prompt Flow
This retrieves relevant product information from Azure AI Search with vector embeddings
"""

from promptflow.core import tool
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from openai import AzureOpenAI
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


@tool
def search_products(query: str) -> str:
    """
    Search for relevant products using hybrid search (vector + keyword).
    
    Args:
        query: User's question about products
    
    Returns:
        Formatted string with relevant product information
    """
    try:
        # Get configuration from environment
        search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
        search_key = os.getenv('AZURE_SEARCH_API_KEY')
        index_name = os.getenv('AZURE_SEARCH_INDEX_NAME', 'outlander-products-index')
        
        # Initialize search client
        search_client = SearchClient(
            endpoint=search_endpoint,
            index_name=index_name,
            credential=AzureKeyCredential(search_key)
        )
        
        # Generate embedding for the query
        embedding_client = AzureOpenAI(
            azure_endpoint=os.getenv('AZURE_EMBEDDING_ENDPOINT'),
            api_key=os.getenv('AZURE_EMBEDDING_API_KEY'),
            api_version=os.getenv('AZURE_EMBEDDING_API_VERSION')
        )
        
        embedding_response = embedding_client.embeddings.create(
            input=query,
            model=os.getenv('AZURE_EMBEDDING_DEPLOYMENT_NAME')
        )
        query_embedding = embedding_response.data[0].embedding
        
        # Perform hybrid search (vector + keyword)
        results = search_client.search(
            search_text=query,
            vector_queries=[{
                "kind": "vector",
                "vector": query_embedding,
                "fields": "contentVector",
                "k": 3
            }],
            top=3,
            select=["title", "content", "category", "price"]
        )
        
        # Format results
        context = []
        for i, result in enumerate(results, 1):
            title = result.get("title", "Unknown Product")
            content = result.get("content", "")[:800]  # Limit content length
            category = result.get("category", "")
            price = result.get("price", "")
            
            product_info = f"## Product {i}: {title}\n"
            if category:
                product_info += f"**Category:** {category}\n"
            if price:
                product_info += f"**Price:** {price}\n"
            product_info += f"\n{content}\n"
            
            context.append(product_info)
        
        if not context:
            return "No relevant product information found."
        
        return "\n".join(context)
        
    except Exception as e:
        return f"Error searching products: {str(e)}"
