"""
Run batch evaluation on the test dataset using the local Prompt Flow
"""

import json
from pathlib import Path
from datetime import datetime
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from test_flow import test_flow


def run_batch_evaluation():
    """Run evaluation on all test questions"""
    
    print("\n" + "="*80)
    print("OUTLANDER GEAR CO. - BATCH EVALUATION")
    print("="*80)
    
    # Load evaluation dataset
    eval_file = Path(__file__).parent.parent.parent / "evaluation" / "evaluation_dataset.jsonl"
    
    print(f"\nLoading test dataset: {eval_file}")
    
    test_cases = []
    with open(eval_file, 'r', encoding='utf-8') as f:
        for line in f:
            test_cases.append(json.loads(line))
    
    print(f"Found {len(test_cases)} test questions")
    
    # Run evaluation
    results = []
    successful = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        question = test_case['chat_input']
        expected = test_case['truth']
        
        print(f"\n\n{'='*80}")
        print(f"TEST {i}/{len(test_cases)}")
        print(f"{'='*80}")
        
        try:
            result = test_flow(question)
            
            results.append({
                "test_number": i,
                "question": question,
                "expected_answer": expected,
                "actual_answer": result["answer"],
                "context_retrieved": result["context"],
                "status": "success"
            })
            successful += 1
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            results.append({
                "test_number": i,
                "question": question,
                "expected_answer": expected,
                "actual_answer": f"ERROR: {str(e)}",
                "context_retrieved": "",
                "status": "error"
            })
            failed += 1
        
        # Pause between questions to avoid rate limiting
        if i < len(test_cases):
            print("\n⏸️  Pausing 2 seconds before next question...")
            import time
            time.sleep(2)
    
    # Save results
    results_dir = Path(__file__).parent.parent.parent / "evaluation" / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"promptflow_evaluation_{timestamp}.json"
    
    summary = {
        "timestamp": timestamp,
        "total_questions": len(test_cases),
        "successful": successful,
        "failed": failed,
        "success_rate": f"{(successful/len(test_cases)*100):.1f}%",
        "results": results
    }
    
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    print("\n\n" + "="*80)
    print("EVALUATION SUMMARY")
    print("="*80)
    print(f"\n📊 Total Questions: {len(test_cases)}")
    print(f"✅ Successful: {successful}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(successful/len(test_cases)*100):.1f}%")
    print(f"\n💾 Results saved to: {results_file}")
    print("\n" + "="*80)
    
    # Show sample results
    print("\n📋 SAMPLE RESULTS:\n")
    for i, result in enumerate(results[:3], 1):
        print(f"Question {i}: {result['question']}")
        print(f"Expected: {result['expected_answer'][:80]}...")
        print(f"Actual: {result['actual_answer'][:80]}...")
        print(f"Status: {result['status']}")
        print()
    
    return summary


if __name__ == "__main__":
    run_batch_evaluation()
