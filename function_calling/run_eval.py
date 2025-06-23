import json
import sys
import os

# Add parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from function_calling.fc_utils import load_and_prepare_data, make_function_call, print_tool_calls, convert_output_to_json, convert_functions_to_tools
from function_calling.FCsimple import main
from json_processing.parse_output import parse_output, parse_query_response_FC
from json_processing.ast_checker import ast_checker

def eval_runner(
        test_category,
        function_description,
        possible_answer
):
    """
    Run the evaluation for a given test category and function description
    """
    prompt = function_description["question"][0][0]["content"]
    tools = function_description["function"]  # This is already a list
    tools = convert_functions_to_tools(tools)  # Convert to tools format for system message
    function_name = function_description["function"][0]["name"]  # Get the first function's name
    full_response = make_function_call(test_category, prompt, tools, function_name)
    
    # Extract the message from the full response
    response_message = full_response.choices[0].message
    
    # Extract token information from the full response
    token_info = parse_query_response_FC(full_response)
    
    converted_output = convert_output_to_json(response_message)
    ast_result = ast_checker(function_description, converted_output, possible_answer, test_category)
    
    # Add token information to the result
    result = {
        "ast_result": ast_result,
        "token_usage": {
            "input_tokens": token_info["input_token"],
            "output_tokens": token_info["output_token"],
            "total_tokens": token_info["input_token"] + token_info["output_token"]
        }
    }
    
    return result


def get_possible_answer(function_description, test_category):
    if test_category == "simple":
        answer_table = json.load(open("../FC-answers/simple_FC_answers.json"))
    elif test_category == "multiple":
        answer_table = json.load(open("../FC-answers/multiple_FC_answers.json"))
    elif test_category == "parallel":
        answer_table = json.load(open("../FC-answers/parallel_FC_answers.json"))
    else:
        raise ValueError(f"Invalid test category: {test_category}")
    
    # Find the matching answer by ID
    function_id = function_description["id"]
    for answer in answer_table:
        if answer["id"] == function_id:
            return answer["ground_truth"]
    
    raise ValueError(f"No answer found for function ID: {function_id}")



def run_evaluation(test_category):
    correct_count = 0
    total_count = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_tokens = 0
    
    if test_category == "simple":
        function_descriptions = json.load(open("../FC-samples/simple_FC.json"))
    elif test_category == "multiple":
        function_descriptions = json.load(open("../FC-samples/multiple_FC.json"))
    elif test_category == "parallel":
        function_descriptions = json.load(open("../FC-samples/parallel_FC.json"))
    else:
        raise ValueError(f"Invalid test category: {test_category}")
    
    for function_description in function_descriptions:
        possible_answer = get_possible_answer(function_description, test_category)
        eval_result = eval_runner(test_category, function_description, possible_answer)
        
        # Extract AST result and token usage
        ast_result = eval_result["ast_result"]
        token_usage = eval_result["token_usage"]
        
        # Update token counters
        total_input_tokens += token_usage["input_tokens"]
        total_output_tokens += token_usage["output_tokens"]
        total_tokens += token_usage["total_tokens"]
        
        if ast_result["isValid"] == True:
            correct_count += 1
        total_count += 1
    
    result = {
        "accuracy": correct_count / total_count, 
        "total_count": total_count, 
        "error_count": total_count - correct_count,
        "token_usage": {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_tokens,
            "average_tokens_per_call": total_tokens / total_count if total_count > 0 else 0
        }
    }
    return result

