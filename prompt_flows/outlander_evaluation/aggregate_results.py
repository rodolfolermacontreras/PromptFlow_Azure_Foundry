"""
Aggregate evaluation results across all test cases
"""

from typing import List
from promptflow.core import tool, log_metric


@tool
def aggregate_results(scores: List[str]) -> dict:
    """
    Aggregate scores from all evaluated questions.
    
    Args:
        scores: List of overall scores from all test cases
    
    Returns:
        Aggregated metrics including average score, pass rate, etc.
    """
    
    if not scores:
        return {
            "average_score": 0.0,
            "pass_rate": 0.0,
            "total_cases": 0,
            "passed_cases": 0
        }
    
    # Convert string scores to floats
    float_scores = [float(score) for score in scores]
    
    # Calculate metrics
    average_score = round(sum(float_scores) / len(float_scores), 2)
    
    # Consider pass threshold as 3.5 (70%)
    pass_threshold = 3.5
    passed_cases = sum(1 for score in float_scores if score >= pass_threshold)
    pass_rate = round((passed_cases / len(float_scores)) * 100, 2)
    
    # Find min and max scores
    min_score = round(min(float_scores), 2)
    max_score = round(max(float_scores), 2)
    
    # Log metrics for Prompt Flow
    log_metric(key="average_score", value=average_score)
    log_metric(key="pass_rate", value=pass_rate)
    log_metric(key="total_cases", value=len(float_scores))
    log_metric(key="passed_cases", value=passed_cases)
    
    result = {
        "average_score": average_score,
        "pass_rate": pass_rate,
        "total_cases": len(float_scores),
        "passed_cases": passed_cases,
        "min_score": min_score,
        "max_score": max_score,
        "pass_threshold": pass_threshold
    }
    
    return result
