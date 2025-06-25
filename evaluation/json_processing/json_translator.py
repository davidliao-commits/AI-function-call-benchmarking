import json
from keyword import kwlist
from typing import Dict, Any, List, Tuple, Union

# Updated TYPE_MAP to match the validation expectations
TYPE_MAP = {
    "int": dict,
    "float": dict,
    "str": dict,
    "bool": dict,
    "list": dict,
    "dict": dict,
    "tuple": dict,
    "boolean": dict,
    "Boolean": dict,
    "Number": dict,
    "number": dict,
    "string": dict,
    "String": dict,
    "array": dict,
    "Array": dict,
    "object": dict,
    "Object": dict,
    "null": dict,
    "integer": dict,
    "any": dict,
}

AVAILABLE_TYPES = {
    "boolean",
    "array",
    "string",
    "integer",
    "float",
    "tuple",
    "any",
    "dict",
    "number",
}

def fix_validation_logic():
    """
    The original validation logic has several issues:
    1. It checks if value is TYPE_MAP[key] but then immediately checks if it's a dict
    2. It returns early after checking the first property
    3. The type checking logic is inconsistent
    """
    pass

def translate_function_call(input_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Translate a JSON function call into the format expected by the validation.
    
    Expected input format:
    {
        "name": "function_name",
        "description": "function description",
        "parameters": {
            "properties": {
                "param1": {
                    "type": "string",
                    "description": "param description"
                },
                "param2": {
                    "type": "number", 
                    "description": "param description"
                }
            },
            "required": ["param1", "param2"]
        }
    }
    
    Returns the properly formatted function description.
    """
    
    # Validate input structure
    if not isinstance(input_json, dict):
        raise ValueError("Input must be a dictionary")
    
    required_fields = ["name", "description", "parameters"]
    for field in required_fields:
        if field not in input_json:
            raise ValueError(f"Missing required field: {field}")
    
    # Extract components
    name = input_json["name"]
    description = input_json["description"]
    parameters = input_json["parameters"]
    
    # Validate parameters structure
    if not isinstance(parameters, dict):
        raise ValueError("Parameters must be a dictionary")
    
    if "properties" not in parameters:
        raise ValueError("Parameters must contain 'properties' field")
    
    if "required" not in parameters:
        raise ValueError("Parameters must contain 'required' field")
    
    properties = parameters["properties"]
    required = parameters["required"]
    
    if not isinstance(properties, dict):
        raise ValueError("Properties must be a dictionary")
    
    if not isinstance(required, list):
        raise ValueError("Required must be a list")
    
    # Validate and transform properties
    transformed_properties = {}
    for param_name, param_info in properties.items():
        if not isinstance(param_info, dict):
            raise ValueError(f"Property {param_name} must be a dictionary")
        
        if "type" not in param_info:
            raise ValueError(f"Property {param_name} must contain 'type' field")
        
        param_type = param_info["type"]
        if param_type not in AVAILABLE_TYPES:
            raise ValueError(f"Property {param_name} has invalid type: {param_type}")
        
        # Check if parameter name is a reserved keyword
        if param_name in kwlist:
            raise ValueError(f"Property name '{param_name}' is a reserved Python keyword")
        
        # Transform the property to match expected format
        transformed_properties[param_name] = {
            "type": param_type,
            "description": param_info.get("description", f"Parameter {param_name}")
        }
    
    # Validate required parameters exist in properties
    for req_param in required:
        if req_param not in properties:
            raise ValueError(f"Required parameter '{req_param}' not found in properties")
    
    # Construct the final format
    result = {
        "name": name,
        "description": description,
        "parameters": {
            "type": "dict",
            "properties": transformed_properties,
            "required": required
        }
    }
    
    return result

def translate_batch(input_file: str) -> List[Dict[str, Any]]:
    """
    Translate a batch of function calls from a JSON file.
    
    Args:
        input_file: Path to input JSON file
    
    Returns:
        List of translated function descriptions
    """
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    translated_functions = []
    
    if isinstance(data, list):
        # Handle array of function calls
        for item in data:
            if "function" in item:
                # Handle the format with id, question, function
                for func in item["function"]:
                    try:
                        translated = translate_function_call(func)
                        translated_functions.append(translated)
                    except ValueError as e:
                        print(f"Error translating function: {e}")
                        continue
            else:
                # Handle direct function calls
                try:
                    translated = translate_function_call(item)
                    translated_functions.append(translated)
                except ValueError as e:
                    print(f"Error translating function: {e}")
                    continue
    else:
        # Handle single function call
        try:
            translated = translate_function_call(data)
            translated_functions.append(translated)
        except ValueError as e:
            print(f"Error translating function: {e}")
    
    return translated_functions

def validate_translated_function(function_desc: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate a translated function using the original validation logic (with fixes).
    """
    if type(function_desc) != dict:
        return False, "function description must be a dictionary"
    
    if "name" not in function_desc:
        return False, "function description must contain a name"
    
    if "description" not in function_desc:
        return False, "function description must contain a description"
    
    if "parameters" not in function_desc:
        return False, "function description must contain at least one parameter"
    
    if len(function_desc) != 3:
        return False, "function description must contain exactly three fields: name, description, and parameters"
    
    parameters = function_desc["parameters"]
    if type(parameters) != dict:
        return False, "parameters must be a dictionary"
    
    if "type" not in parameters:
        return False, "parameters must contain a type field"
    
    if "required" not in parameters:
        return False, "parameters must contain a required field"
    
    if type(parameters["required"]) != list:
        return False, "required field must be a list"
    
    if "properties" not in parameters:
        return False, "parameters must contain a properties field"
    
    if len(parameters) != 3:
        return False, "parameters must contain exactly three fields: type, required, and properties"
    
    properties = parameters["properties"]
    if type(properties) != dict:
        return False, "properties must be a dictionary"
    
    for key, value in properties.items():
        if key in kwlist:
            return False, f"property {key} is a reserved keyword"
        
        if type(value) != dict:
            return False, f"property {key} must be a dictionary"
        
        if "type" not in value:
            return False, f"property {key} must contain a type field"
        
        if value["type"] not in AVAILABLE_TYPES:
            return False, f"property {key} must contain a valid type"
    
    return True, "function is correctly formatted"

def main():
    """Example usage of the translator."""
    
    # Example 1: Translate existing files (without saving)
    print("Translating simple_FC.json...")
    try:
        translated = translate_batch("simple_FC.json")
        print(f"Successfully translated {len(translated)} functions")
        
        # Validate the translated functions
        valid_count = 0
        for func in translated:
            is_valid, message = validate_translated_function(func)
            if is_valid:
                valid_count += 1
            else:
                print(f"Invalid function '{func['name']}': {message}")
        
        print(f"Validation results: {valid_count}/{len(translated)} functions are valid")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nTranslating multiple_FC.json...")
    try:
        translated = translate_batch("multiple_FC.json")
        print(f"Successfully translated {len(translated)} functions")
        
        # Validate the translated functions
        valid_count = 0
        for func in translated:
            is_valid, message = validate_translated_function(func)
            if is_valid:
                valid_count += 1
            else:
                print(f"Invalid function '{func['name']}': {message}")
        
        print(f"Validation results: {valid_count}/{len(translated)} functions are valid")
        
    except Exception as e:
        print(f"Error: {e}")
    
    # Example 2: Translate a single function call
    example_function = {
        "name": "calculate_area",
        "description": "Calculate the area of a shape",
        "parameters": {
            "properties": {
                "width": {
                    "type": "number",
                    "description": "Width of the shape"
                },
                "height": {
                    "type": "number", 
                    "description": "Height of the shape"
                }
            },
            "required": ["width", "height"]
        }
    }
    
    print("\nTranslating example function...")
    try:
        translated_func = translate_function_call(example_function)
        is_valid, message = validate_translated_function(translated_func)
        print(f"Translation successful: {is_valid}")
        print(f"Message: {message}")
        print("Translated function:")
        print(json.dumps(translated_func, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 