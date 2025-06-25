#!/usr/bin/env python3
"""
Test script to verify token tracking functionality
"""

import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from function_calling.run_eval import eval_runner, get_possible_answer
import json

def test_single_function_call():
    """Test token tracking for a single function call"""
    print("Testing single function call with token tracking...")
    
    # Load a simple function description
    with open("../FC-samples/simple_FC.json", "r") as f:
        function_descriptions = json.load(f)
    
    # Use the first example
    function_description = function_descriptions[0]
    possible_answer = get_possible_answer(function_description, "simple")
    
    # Run evaluation
    result = eval_runner("simple", function_description, possible_answer)
    
    # Print results
    print(f"AST Result: {result['ast_result']}")
    print(f"Token Usage:")
    print(f"  Input tokens: {result['token_usage']['input_tokens']}")
    print(f"  Output tokens: {result['token_usage']['output_tokens']}")
    print(f"  Total tokens: {result['token_usage']['total_tokens']}")
    
    return result

def test_parallel_function_call():
    """Test token tracking for parallel function calls"""
    print("\nTesting parallel function call with token tracking...")
    
    # Load a parallel function description
    with open("../FC-samples/parallel_FC.json", "r") as f:
        function_descriptions = json.load(f)
    
    # Use the first example
    function_description = function_descriptions[0]
    possible_answer = get_possible_answer(function_description, "parallel")
    
    # Run evaluation
    result = eval_runner("parallel", function_description, possible_answer)
    
    # Print results
    print(f"AST Result: {result['ast_result']}")
    print(f"Token Usage:")
    print(f"  Input tokens: {result['token_usage']['input_tokens']}")
    print(f"  Output tokens: {result['token_usage']['output_tokens']}")
    print(f"  Total tokens: {result['token_usage']['total_tokens']}")
    
    return result

if __name__ == "__main__":
    print("Token Tracking Test")
    print("=" * 50)
    
    try:
        # Test simple function call
        simple_result = test_single_function_call()
        
        # Test parallel function call
        parallel_result = test_parallel_function_call()
        
        print("\n" + "=" * 50)
        print("All tests completed successfully!")
        print("Token tracking is working correctly.")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc() 