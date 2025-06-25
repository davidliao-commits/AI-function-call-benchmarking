import json
import ast
from function_calling.fc_utils import convert_output_to_json, load_and_prepare_data
from function_calling.FCsimple import main
from json_processing.parse_output import parse_output

PYTHON_TYPE_MAPPING = {
    "string":str,
    "integer":int,
    "float":float,
    "boolean":bool,
    "array":list,
    "tuple":list,
    "dict":dict,
    "any":str,
    "int":int,
    "object":dict,
    "number":float
}

PYTHON_RECURSIVE_CHECK_TYPES = [ "array", "tuple", "dict", "object"]

def ast_checker(
        function_description,
        model_output,
        possible_answer,
        test_category,
):
    if "simple" in test_category:
        return simple_ast_checker(function_description, model_output, possible_answer, test_category)
    elif "parallel" in test_category:
        return parallel_ast_checker(function_description, model_output, possible_answer )
    elif "multiple" in test_category:
        return multiple_ast_checker(function_description, model_output, possible_answer)
    else:
        return {
            "isValid": False,
            "error": f"Unknown test category: {test_category}",
            "error_type": "unknown_category"
        }

def simple_ast_checker(
        function_description,
        model_output,
        possible_answer,
        test_category,
):
    function_name = None
    function_arguments = None
    required_parameters = None
    if test_category == "parallel":
        possible_answer = possible_answer[0]
    elif test_category == "multiple":
        possible_answer = possible_answer[0]
    else:
        possible_answer = possible_answer
    if test_category == "parallel" or test_category == "simple":
        function_name = function_description["function"][0]["name"]
        function_arguments = function_description["function"][0]["parameters"]["properties"]
        required_parameters = function_description["function"][0]["parameters"]["required"]
    elif test_category == "multiple":
        function_name = function_description["name"]
        function_arguments = function_description["parameters"]["properties"]
        required_parameters = function_description["parameters"]["required"]

    result = {
        "isValid": True,
        "error": None,
        "type": "simple_function_call"
    }


    # Check if function name matches
    if function_name != model_output["function_name"]:
        result["isValid"] = False
        result["error"] = f"Function name mismatch: expected {function_name}, got {model_output['function_name']}"
        return result
    
    model_arguments = model_output["arguments"]


    # Get the function-specific possible answer
    
    if function_name not in possible_answer:
        result["isValid"] = False
        result["error"] = f"Function {function_name} not found in possible answers"
        return result
    
    function_possible_answer = possible_answer[function_name]


    # Check for missing required parameters
    for param in required_parameters:
        if param not in model_arguments:
            result["isValid"] = False
            result["error"] = f"Missing required parameter: {param}"
            return result
    
    # Check each parameter in model output
    for param, value in model_arguments.items():

        
        # Check if parameter is expected
        if param not in function_arguments:
            result["isValid"] = False
            result["error"] = f"Unexpected argument: {param}"
            return result
        
        # Check if parameter exists in possible answers
        if param not in function_possible_answer:
            result["isValid"] = False
            result["error"] = f"Parameter {param} not found in possible answers. Available keys: {list(function_possible_answer.keys())}"
            return result
        
        # Get expected values for this parameter
        expected_values = function_possible_answer[param]
        
        # Handle both array and direct value formats
        if isinstance(expected_values, list):
            # If it's already a list, use it as is
            expected_values_list = expected_values
        else:
            # If it's a direct value, wrap it in a list
            expected_values_list = [expected_values]
        
        # Check if the value matches any of the expected values
        value_matches = False
        for expected_value in expected_values_list:
           
            
            # Try direct comparison first
            if value == expected_value:
                value_matches = True
                break
            
            # Handle quotation marks for string comparisons
            if isinstance(value, str) and isinstance(expected_value, str):
                # Strip quotes from both values for comparison
                clean_value = value.strip('"\'')
                clean_expected = expected_value.strip('"\'')
                if clean_value == clean_expected:
                    value_matches = True
                    break
            
            # Handle type conversions for numeric values
            if isinstance(expected_value, (int, float)):
                # Try to convert value to numeric if it's a string
                if isinstance(value, str):
                    try:
                        # Handle scientific notation and regular numbers
                        converted_value = float(value)
                        if abs(converted_value - expected_value) < 1e-10:  # Small epsilon for float comparison
                            value_matches = True
                            break
                    except (ValueError, TypeError):
                        pass
                elif isinstance(value, (int, float)):
                    # Both are numeric, use epsilon comparison
                    if abs(value - expected_value) < 1e-10:
                        value_matches = True
                        break
        
        if not value_matches:
            result["isValid"] = False
            result["error"] = f"Value mismatch for {param}: expected one of {expected_values_list}, got {value} (type: {type(value)})"
            return result
        
        # Check type compatibility
        full_param_details = function_arguments[param]
        expected_type_description = full_param_details["type"]
        expected_type = PYTHON_TYPE_MAPPING[expected_type_description]

        if expected_type_description in PYTHON_RECURSIVE_CHECK_TYPES:
            if "items" in full_param_details:
                recursive_type = full_param_details["items"]["type"]
                expected_type = PYTHON_TYPE_MAPPING[recursive_type]

        # Type checking - be more flexible for numeric types
        if expected_type in [int, float]:
            if not isinstance(value, (int, float)):
                result["isValid"] = False
                result["error"] = f"Type mismatch for {param}: expected numeric type, got {type(value)}"
                return result
        else:
            if not isinstance(value, expected_type):
                result["isValid"] = False
                result["error"] = f"Type mismatch for {param}: expected {expected_type_description}, got {type(value)}"
                return result

    return result

def parallel_ast_checker(
        function_description,
        model_output,
        possible_answer,
):
    """
    Check parallel function calls where the same function is called multiple times with different parameters
    """
    result = {
        "isValid": True,
        "error": None,
        "type": "parallel_function_call"
    }
    
    # For parallel calls, we expect multiple function calls with the same function name
    # but different parameters
    if not isinstance(model_output, list):
        result["isValid"] = False
        result["error"] = "Expected list of function calls for parallel execution"
        return result
    
    # Check if the number of calls matches the number of possible answers
    if len(model_output) != len(possible_answer):
        result["isValid"] = False
        result["error"] = f"Number of function calls ({len(model_output)}) does not match number of possible answers ({len(possible_answer)})"
        return result
    
    # Create a list to track which possible answers have been matched
    matched_answers = [False] * len(possible_answer)
    
    # Check each function call against all possible answers
    for i, call in enumerate(model_output):
        call_matched = False
        
        # Try to match this call with any of the possible answers
        for j, possible_call in enumerate(possible_answer):
            if matched_answers[j]:  # Skip already matched answers
                continue

                
            # Create a temporary function description with this possible answer
            temp_function_description = function_description.copy()
            temp_function_description["function"] = [temp_function_description["function"][0].copy()]
           
            # Check if this call matches the possible answer
            call_result = simple_ast_checker(temp_function_description, call, [possible_call], "parallel")
            if call_result["isValid"]:
                matched_answers[j] = True
                call_matched = True
                break
        
        # Only check for failure if no match was found
        if not call_matched:
            result["isValid"] = False
            result["error"] = f"Function {i+1} was not matched"
            return result

    # Verify all possible answers were matched
    if not all(matched_answers):
        result["isValid"] = False
        result["error"] = "Not all possible answers were matched"
        return result
    return result

def multiple_ast_checker(
        function_description,
        model_output,
        possible_answer,
):
    
    """
    Check multiple function calls where different functions are called
    """
    result = {
        "isValid": True,
        "error": None,
        "type": "multiple_function_call"
    }
    
    # For multiple calls, we expect a list of different function calls
    if not isinstance(model_output, list):
        result["isValid"] = False
        result["error"] = "Expected list of function calls for multiple execution"
        return result
    
    if len(model_output) != len(possible_answer):
        result["isValid"] = False
        result["error"] = f"Number of function calls does not match the number of possible answers"
        return result
    
    # Create a list to track which possible answers have been matched
    matched_answers = [False] * len(possible_answer)
    
    # Check each function call against all possible answers
    for call in model_output:
        call_matched = False
        
        # Try to match this call with any of the possible answers
        for j, possible_call in enumerate(possible_answer):
            if matched_answers[j]:  # Skip already matched answers
                continue
                
            function_name = list(possible_call.keys())[0]
            function_description_copy = find_function_description(function_description, function_name)
            
            # Check if function description was found
            if function_description_copy is None:
                result["isValid"] = False
                result["error"] = f"Function '{function_name}' not found in function description. Available functions: {[f['name'] for f in function_description['function']]}"
                return result
                
            call_result = simple_ast_checker(function_description_copy, call, [possible_call], "multiple")

            if call_result["isValid"] == True:
                matched_answers[j] = True
                call_matched = True
                break
        
        # If no match was found for this call
        if not call_matched:
            result["isValid"] = False
            result["error"] = f"Function call {call.get('function_name', 'unknown')} was not matched"
            return result

    # Verify all possible answers were matched
    if not all(matched_answers):
        result["isValid"] = False
        result["error"] = "Not all possible answers were matched"
        return result

    return result



def find_function_description(function_descriptions, function_name):
    for function_description in function_descriptions["function"]:
        if function_description["name"] == function_name:
            return function_description
    return None