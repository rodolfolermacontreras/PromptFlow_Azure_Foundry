"""
Run copilot on existing evaluation dataset and evaluate with GPT-4o judge
"""
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Load environment variables
load_dotenv(project_root / ".env")

from promptflow.client import PFClient
from promptflow.core import Prompty


def run_copilot_flow(question: str, chat_history: list = None) -> str:
    """
    Run the outlander copilot flow and return the answer.
    
    Args:
        question: User's question
        chat_history: Optional chat history
        
    Returns:
        Generated answer from the copilot
    """
    pf = PFClient()
    
    flow_path = project_root / "prompt_flows" / "outlander_copilot"
    
    try:
        result = pf.flows.test(
            flow=str(flow_path),
            inputs={
                "chat_input": question,
                "chat_history": chat_history or []
            }
        )
        
        # Extract answer from result
        if hasattr(result, 'answer'):
            return result.answer
        elif isinstance(result, dict) and 'answer' in result:
            return result['answer']
        else:
            return str(result)
            
    except Exception as e:
        print(f"Error running copilot: {e}")
        return f"Error: {str(e)}"


def run_evaluation_flow(question: str, ground_truth: str, prediction: str, context: str = "") -> dict:
    """
    Run the evaluation flow to score a prediction.
    
    Args:
        question: Original question
        ground_truth: Expected answer
        prediction: Generated answer from copilot
        context: Retrieved context (optional)
        
    Returns:
        Dictionary with evaluation_result and overall_score
    """
    pf = PFClient()
    
    flow_path = project_root / "prompt_flows" / "outlander_evaluation"
    
    try:
        result = pf.flows.test(
            flow=str(flow_path),
            inputs={
                "question": question,
                "ground_truth": ground_truth,
                "prediction": prediction,
                "context": context
            }
        )
        
        # Parse the result
        if isinstance(result, dict):
            eval_result = result.get('evaluation_result', '{}')
            overall_score = result.get('overall_score', '0.0')
        else:
            eval_result = '{}'
            overall_score = '0.0'
        
        # Parse JSON strings if needed
        if isinstance(eval_result, str):
            eval_result = json.loads(eval_result)
        if isinstance(overall_score, str):
            overall_score = float(overall_score)
            
        return {
            "evaluation_result": eval_result,
            "overall_score": overall_score
        }
        
    except Exception as e:
        print(f"Error running evaluation: {e}")
        return {
            "evaluation_result": {"error": str(e)},
            "overall_score": 0.0
        }


def main():
    """
    Main function to run copilot and evaluate responses.
    """
    # Paths
    dataset_path = project_root / "evaluation" / "evaluation_dataset.jsonl"
    output_dir = project_root / "evaluation" / "results"
    output_dir.mkdir(exist_ok=True)
    
    # Generate timestamp for output file
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"llm_judge_evaluation_{timestamp}.json"
    
    print(f"Loading dataset from: {dataset_path}")
    print(f"Output will be saved to: {output_path}")
    print("-" * 80)
    
    # Load dataset
    test_cases = []
    with open(dataset_path, 'r', encoding='utf-8') as f:
        for line in f:
            test_cases.append(json.loads(line.strip()))
    
    print(f"Loaded {len(test_cases)} test cases")
    print("-" * 80)
    
    # Process each test case
    results = []
    total_score = 0.0
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case['chat_input']
        ground_truth = test_case['truth']
        chat_history = test_case.get('chat_history', [])
        
        print(f"\n[{i}/{len(test_cases)}] Question: {question}")
        
        # Step 1: Run copilot to get prediction
        print("  → Running copilot...")
        prediction = run_copilot_flow(question, chat_history)
        print(f"  → Prediction: {prediction[:100]}..." if len(prediction) > 100 else f"  → Prediction: {prediction}")
        
        # Step 2: Evaluate the prediction
        print("  → Evaluating with GPT-4o judge...")
        evaluation = run_evaluation_flow(question, ground_truth, prediction)
        
        eval_result = evaluation['evaluation_result']
        overall_score = evaluation['overall_score']
        
        print(f"  → Overall Score: {overall_score}/5.0")
        if 'relevance' in eval_result:
            print(f"     - Relevance: {eval_result['relevance']}")
            print(f"     - Accuracy: {eval_result['accuracy']}")
            print(f"     - Completeness: {eval_result['completeness']}")
            print(f"     - Groundedness: {eval_result['groundedness']}")
            print(f"     - Fluency: {eval_result['fluency']}")
        
        # Store result
        result = {
            "test_number": i,
            "question": question,
            "ground_truth": ground_truth,
            "prediction": prediction,
            "evaluation": eval_result,
            "overall_score": overall_score,
            "status": "success" if overall_score > 0 else "failed"
        }
        results.append(result)
        total_score += overall_score
    
    # Calculate summary statistics
    avg_score = total_score / len(test_cases) if test_cases else 0.0
    pass_threshold = 3.5  # 70%
    passed = sum(1 for r in results if r['overall_score'] >= pass_threshold)
    pass_rate = (passed / len(test_cases)) * 100 if test_cases else 0.0
    
    # Prepare final output
    output_data = {
        "timestamp": timestamp,
        "dataset": str(dataset_path),
        "total_questions": len(test_cases),
        "average_score": round(avg_score, 2),
        "pass_rate": f"{pass_rate:.1f}%",
        "passed_cases": passed,
        "pass_threshold": pass_threshold,
        "evaluation_method": "GPT-4o LLM Judge (5 metrics: relevance, accuracy, completeness, groundedness, fluency)",
        "results": results
    }
    
    # Save results
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print("EVALUATION COMPLETE")
    print("=" * 80)
    print(f"Total test cases: {len(test_cases)}")
    print(f"Average score: {avg_score:.2f}/5.0")
    print(f"Pass rate (≥{pass_threshold}): {pass_rate:.1f}% ({passed}/{len(test_cases)})")
    print(f"\nResults saved to: {output_path}")
    print("=" * 80)


if __name__ == "__main__":
    main()
