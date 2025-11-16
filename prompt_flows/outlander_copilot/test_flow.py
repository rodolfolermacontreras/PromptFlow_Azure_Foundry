"""
Test the Prompt Flow locally without using pf CLI
This simulates the flow execution for testing and screenshots
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment variables
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# Import the search function
from prompt_flows.outlander_copilot.search_products import search_products

# Import OpenAI for generation
from openai import AzureOpenAI


def generate_response(question: str, context: str, chat_history: list = None) -> str:
    """Generate response using GPT-4o"""
    
    client = AzureOpenAI(
        azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
        api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        api_version=os.getenv('AZURE_OPENAI_API_VERSION')
    )
    
    # Build the system message
    system_message = f"""You are an AI assistant for Outlander Gear Co., a company that sells high-quality outdoor equipment.
Your role is to help customers find product information, compare products, and answer questions about pricing, features, warranties, and specifications.

Be helpful, friendly, and accurate. Base your responses ONLY on the product information provided in the context below.
If you don't know the answer or the information isn't in the context, say so politely.

Context from product catalog:
{context}"""
    
    messages = [{"role": "system", "content": system_message}]
    
    # Add chat history if provided
    if chat_history:
        for msg in chat_history:
            messages.append(msg)
    
    # Add current question
    messages.append({"role": "user", "content": question})
    
    response = client.chat.completions.create(
        model=os.getenv('AZURE_DEPLOYMENT_NAME'),
        messages=messages,
        temperature=0.7,
        max_tokens=500
    )
    
    return response.choices[0].message.content


def test_flow(question: str, chat_history: list = None):
    """Test the complete flow"""
    
    print("\n" + "="*80)
    print("OUTLANDER GEAR CO. - PROMPT FLOW TEST")
    print("="*80)
    
    print(f"\n📝 Question: {question}")
    print("\n" + "-"*80)
    
    # Step 1: Search
    print("\n🔍 Step 1: Searching products...")
    context = search_products(question)
    print(f"\n   Retrieved {len(context.split('## Product')) - 1} products")
    print(f"\n   Context preview:")
    print(f"   {context[:200]}..." if len(context) > 200 else f"   {context}")
    
    print("\n" + "-"*80)
    
    # Step 2: Generate
    print("\n🤖 Step 2: Generating response with GPT-4o...")
    answer = generate_response(question, context, chat_history)
    
    print("\n" + "="*80)
    print("📤 ANSWER:")
    print("="*80)
    print(answer)
    print("\n" + "="*80)
    
    return {
        "question": question,
        "context": context,
        "answer": answer
    }


def run_interactive_test():
    """Run interactive testing"""
    
    print("\n" + "="*80)
    print("OUTLANDER GEAR CO. - INTERACTIVE PROMPT FLOW")
    print("="*80)
    print("\nTest the copilot with your own questions!")
    print("Type 'quit' to exit\n")
    
    chat_history = []
    
    while True:
        question = input("\n💬 Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!\n")
            break
        
        if not question:
            continue
        
        result = test_flow(question, chat_history)
        
        # Update chat history
        chat_history.append({"role": "user", "content": question})
        chat_history.append({"role": "assistant", "content": result["answer"]})
        
        # Keep only last 4 messages (2 exchanges)
        if len(chat_history) > 4:
            chat_history = chat_history[-4:]


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # Test with provided question
        question = " ".join(sys.argv[1:])
        test_flow(question)
    else:
        # Run some default tests
        print("\n🧪 Running test questions...\n")
        
        test_questions = [
            "Which tent is the most waterproof?",
            "How much do the TrailWalker Hiking Shoes cost?",
            "What is the floor area for TrailMaster X4 Tent?",
        ]
        
        for q in test_questions:
            test_flow(q)
            input("\n\nPress Enter to continue to next question...")
        
        print("\n\n" + "="*80)
        print("Would you like to try interactive mode? (y/n): ", end="")
        if input().lower() == 'y':
            run_interactive_test()
