"""
Calculate overall score from evaluation metrics
"""

import json
from promptflow.core import tool


@tool
def calculate_score(evaluation_result: str) -> str:
    """
    Calculate overall score from individual metrics.
    
    Args:
        evaluation_result: JSON string with individual metric scores
    
    Returns:
        Overall score as string (average of all metrics)
    """
    
    # Parse JSON string to dictionary
    result_dict = json.loads(evaluation_result)
    
    # Extract metric scores
    metrics = ["relevance", "accuracy", "completeness", "groundedness", "fluency"]
    
    scores = []
    for metric in metrics:
        if metric in result_dict:
            scores.append(float(result_dict[metric]))
    
    # Calculate average
    if scores:
        overall_score = round(sum(scores) / len(scores), 2)
    else:
        overall_score = 0.0
    
    # Return as string (required for Prompt Flow string output type)
    return str(overall_score)
