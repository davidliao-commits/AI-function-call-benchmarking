from function_calling.fc_utils import load_and_prepare_data, make_function_call, print_tool_calls, convert_output_to_json
import json

PYTHON_TYPE_MAPPING = {
    "string":str,
    "integer":int,
    "float":float,
    "boolean":bool,
    "array":list,
    "object":dict,
    "null":None,
    "any":str,
    "tuple":list,
    "dict":dict
}

def check_ast(function_description:dict, output:dict, possible_answer, test_category:str):
    """
    Check if the output matches the expected AST structure
    
    Args:
        function_description: The function description from the JSON file
        output: The output from the function call
        possible_answer: The possible answer from the JSON file
        test_category: The test category from the JSON file
    """

    if "simple" in test_category:
        return check_simple_ast(function_description, output, possible_answer)
    






def check_simple_ast(function_description:dict, output:dict, possible_answer:dict):
    """
    Check if the output matches the expected AST structure for simple tests
    
    Args:
        function_description: The function description from the JSON file
        output: The output from the function call
        possible_answer: The possible answer from the JSON file
    """
    