"""
Evaluate metrics for Outlander Copilot responses
Evaluates: relevance, accuracy, completeness, groundedness, fluency
"""

from promptflow.core import tool
from pathlib import Path
from dotenv import load_dotenv
import os
import json
from openai import AzureOpenAI

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


@tool
def evaluate_metrics(question: str, ground_truth: str, prediction: str, context: str = "") -> dict:
    """
    Evaluate the quality of the copilot's answer using GPT-4o as a judge.
    
    Args:
        question: User's question
        ground_truth: Expected answer or key information
        prediction: Generated answer from copilot
        context: Retrieved product context (optional)
    
    Returns:
        Dictionary with evaluation metrics (0-5 scale):
        - relevance: Does it address the question?
        - accuracy: Is information factually correct?
        - completeness: Sufficient detail provided?
        - groundedness: Based on context only?
        - fluency: Well-written and clear?
    """
    
    # Initialize Azure OpenAI client
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )
    
    deployment_name = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
    
    # Build evaluation prompt
    eval_prompt = f"""You are an expert evaluator for AI chatbot responses. Evaluate the following answer on 5 criteria using a scale of 0-5 (where 5 is excellent and 0 is poor).

**Question:** {question}

**Ground Truth (Expected Answer):** {ground_truth}

**Generated Answer:** {prediction}

**Context Used:** {context if context else "No context provided"}

**Evaluation Criteria:**

1. **Relevance (0-5):** Does the answer directly address the question?
2. **Accuracy (0-5):** Is the information factually correct compared to ground truth?
3. **Completeness (0-5):** Does the answer provide sufficient detail?
4. **Groundedness (0-5):** Is the answer based solely on the provided context (if applicable)?
5. **Fluency (0-5):** Is the answer well-written, clear, and professional?

**Instructions:**
- Provide a score (0-5) for each criterion
- Be objective and fair
- Consider that ground truth may be a summary, not the exact expected answer
- Return ONLY valid JSON with this structure:

{{
    "relevance": <score 0-5>,
    "accuracy": <score 0-5>,
    "completeness": <score 0-5>,
    "groundedness": <score 0-5>,
    "fluency": <score 0-5>,
    "reasoning": "<brief explanation of scores>"
}}
"""
    
    try:
        # Call GPT-4o for evaluation
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": "You are an expert AI evaluator. Return only valid JSON."},
                {"role": "user", "content": eval_prompt}
            ],
            temperature=0.1,  # Low temperature for consistent evaluation
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        # Parse the evaluation result
        evaluation = json.loads(response.choices[0].message.content)
        
        # Ensure all required fields are present
        required_fields = ["relevance", "accuracy", "completeness", "groundedness", "fluency"]
        for field in required_fields:
            if field not in evaluation:
                evaluation[field] = 3.0  # Default to middle score if missing
        
        # Add metadata
        evaluation["question"] = question
        evaluation["prediction"] = prediction[:200] + "..." if len(prediction) > 200 else prediction
        
        # Return as JSON string (required for Prompt Flow string output type)
        return json.dumps(evaluation)
        
    except Exception as e:
        # Return default scores if evaluation fails (as JSON string)
        default_result = {
            "relevance": 3.0,
            "accuracy": 3.0,
            "completeness": 3.0,
            "groundedness": 3.0,
            "fluency": 3.0,
            "reasoning": f"Evaluation failed: {str(e)}",
            "error": str(e),
            "question": question,
            "prediction": prediction[:200] + "..." if len(prediction) > 200 else prediction
        }
        return json.dumps(default_result)
