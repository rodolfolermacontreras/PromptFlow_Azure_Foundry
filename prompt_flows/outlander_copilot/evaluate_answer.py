"""
Evaluation node for Prompt Flow
Evaluates the quality of generated answers
"""

from promptflow.core import tool
from openai import AzureOpenAI
import os
from pathlib import Path
from dotenv import load_dotenv
import json

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


@tool
def evaluate_answer(question: str, answer: str, ground_truth: str, context: str) -> dict:
    """
    Evaluate the quality of the generated answer using GPT-4o.
    
    Args:
        question: Original user question
        answer: Generated answer from the flow
        ground_truth: Expected correct answer
        context: Retrieved context used for generation
    
    Returns:
        Dictionary with evaluation metrics
    """
    try:
        # Initialize Azure OpenAI client
        client = AzureOpenAI(
            azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
            api_key=os.getenv('AZURE_OPENAI_API_KEY'),
            api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview')
        )
        
        # Build evaluation prompt
        eval_prompt = f"""You are an AI evaluator assessing the quality of answers provided by an AI assistant for an outdoor gear company.

Question: {question}

Generated Answer: {answer}

Ground Truth/Expected Answer: {ground_truth}

Context Used: {context}

Evaluate the generated answer on the following criteria (score each from 0-5):
1. **Relevance**: Does the answer address the question?
2. **Accuracy**: Is the answer factually correct based on the context?
3. **Completeness**: Does the answer provide sufficient detail?
4. **Groundedness**: Is the answer based on the provided context?
5. **Fluency**: Is the answer well-written and clear?

Provide your evaluation in JSON format:
{{
    "relevance_score": <0-5>,
    "accuracy_score": <0-5>,
    "completeness_score": <0-5>,
    "groundedness_score": <0-5>,
    "fluency_score": <0-5>,
    "overall_score": <average of all scores>,
    "pass": <true if overall_score >= 3.5, false otherwise>,
    "reasoning": "<brief explanation of scores>"
}}"""
        
        # Call GPT-4o for evaluation
        response = client.chat.completions.create(
            model=os.getenv('AZURE_DEPLOYMENT_NAME', 'gpt-4o'),
            messages=[
                {"role": "system", "content": "You are an expert evaluator. Provide evaluations in valid JSON format only."},
                {"role": "user", "content": eval_prompt}
            ],
            temperature=0.1,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        # Parse evaluation result
        eval_result = json.loads(response.choices[0].message.content)
        
        # Add metadata
        eval_result["question"] = question
        eval_result["answer_length"] = len(answer)
        eval_result["context_used"] = len(context) > 0
        
        return eval_result
        
    except Exception as e:
        # Return error information
        return {
            "relevance_score": 0,
            "accuracy_score": 0,
            "completeness_score": 0,
            "groundedness_score": 0,
            "fluency_score": 0,
            "overall_score": 0,
            "pass": False,
            "reasoning": f"Evaluation failed: {str(e)}",
            "error": str(e)
        }
