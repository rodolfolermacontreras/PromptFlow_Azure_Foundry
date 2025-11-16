"""
Test script for outlander_evaluation flow
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evaluate_metrics import evaluate_metrics
from calculate_score import calculate_score


def test_evaluation():
    """Test the evaluation flow with a sample case"""
    
    # Test case
    question = "Which tent is the most waterproof?"
    ground_truth = "Alpine Explorer Tent and SkyView 2-Person Tent are the most waterproof"
    prediction = "All three tents in the catalog offer waterproof features for reliable protection against rain and moisture. The Alpine Explorer Tent (item 8) is specifically stated to be waterproof. The SkyView 2-Person Tent (item 15) is described as durable and waterproof. The TrailMaster X4 Tent (item 1) is mentioned as water-resistant, which typically provides less protection than fully waterproof materials. Based on the descriptions, the Alpine Explorer Tent and SkyView 2-Person Tent are the most waterproof."
    context = "Product info about tents..."
    
    print("Testing Outlander Evaluation Flow")
    print("=" * 60)
    print(f"\nQuestion: {question}")
    print(f"\nGround Truth: {ground_truth}")
    print(f"\nPrediction: {prediction[:150]}...")
    print("\n" + "=" * 60)
    
    # Step 1: Evaluate metrics
    print("\nStep 1: Evaluating metrics...")
    evaluation_result = evaluate_metrics(
        question=question,
        ground_truth=ground_truth,
        prediction=prediction,
        context=context
    )
    
    print("\nEvaluation Result:")
    for key, value in evaluation_result.items():
        if key not in ["question", "prediction", "reasoning"]:
            print(f"  {key}: {value}")
    
    if "reasoning" in evaluation_result:
        print(f"\nReasoning: {evaluation_result['reasoning']}")
    
    # Step 2: Calculate overall score
    print("\nStep 2: Calculating overall score...")
    overall_score = calculate_score(evaluation_result)
    
    print(f"\nOverall Score: {overall_score}/5.0")
    
    # Determine pass/fail
    pass_threshold = 3.5
    status = "PASS ✓" if overall_score >= pass_threshold else "FAIL ✗"
    print(f"Status: {status} (threshold: {pass_threshold})")
    
    print("\n" + "=" * 60)
    print("Evaluation test complete!")


if __name__ == "__main__":
    test_evaluation()
