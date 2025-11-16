"""
Generate response node - Uses GPT-4o to create answers
"""
from promptflow.core import tool
from openai import AzureOpenAI
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


@tool
def generate_response(question: str, context: str, chat_history: list = None) -> str:
    """
    Generate a helpful answer using GPT-4o based on the retrieved context.
    
    Args:
        question: User's question
        context: Retrieved product information from search
        chat_history: Previous conversation messages (optional)
    
    Returns:
        Generated answer
    """
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
        api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        api_version=os.getenv('AZURE_OPENAI_API_VERSION')
    )
    
    # Build system message with context
    system_message = f"""You are an AI assistant for Outlander Gear Co., a company that sells high-quality outdoor equipment.
Your role is to help customers find product information, compare products, and answer questions about pricing, features, warranties, and specifications.

Be helpful, friendly, and accurate. Base your responses ONLY on the product information provided in the context below.
If you don't know the answer or the information isn't in the context, say so politely.

Context from product catalog:
{context}"""
    
    # Build messages
    messages = [{"role": "system", "content": system_message}]
    
    # Add chat history if provided
    if chat_history:
        for msg in chat_history:
            messages.append(msg)
    
    # Add current question
    messages.append({"role": "user", "content": question})
    
    # Generate response
    response = client.chat.completions.create(
        model=os.getenv('AZURE_DEPLOYMENT_NAME'),
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content
