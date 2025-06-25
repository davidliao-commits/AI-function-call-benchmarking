import json
from keyword import kwlist

TYPE_MAP = {
    "int": int,
    "float": float,
    "str": str,
    "bool": bool,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "boolean": bool,
    "Boolean": bool,
    "Number": int,
    "number": int,
    "string": str,
    "String": str,
    "array": list,
    "Array": list,
    "object": dict,
    "Object": dict,
    "null": None,
    "integer": int,
    "any": object,
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

def function_format_check(function_description: dict):
    """
    Fixed version of the function format checker.
    The original had several logical issues that have been corrected.
    """
    if type(function_description) != dict:
        return False, "function description must be a dictionary"
    
    if "name" not in function_description:
        return False, "function description must contain a name"
    
    if "description" not in function_description:
        return False, "function description must contain a description"
    
    if "parameters" not in function_description:
        return False, "function description must contain at least one parameter"
    
    if len(function_description) != 3:
        return False, "function description must contain exactly three fields: name, description, and parameters"
    
    parameters = function_description["parameters"]
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
    
    # Check each property
    for key, value in properties.items():
        # Check if property name is a reserved keyword
        if key in kwlist:
            return False, f"property {key} is a reserved keyword"
        
        # Check if value is a dictionary
        if type(value) != dict:
            return False, f"property {key} must be a dictionary"
        
        # Check if value contains a type field
        if "type" not in value:
            return False, f"property {key} must contain a type field"
        
        # Check if the type is valid
        if value["type"] not in AVAILABLE_TYPES:
            return False, f"property {key} must contain a valid type"
    
    return True, "function is correctly formatted"

def main():
    """Test the fixed validation function with the existing JSON files."""
    
    # Test with simple_FC.json
    print("Testing simple_FC.json...")
    try:
        with open("simple_FC.json", "r") as f:
            data = json.load(f)
        
        # Extract functions from the data structure
        for item in data:
            if "function" in item:
                for func in item["function"]:
                    is_valid, message = function_format_check(func)
                    if is_valid:
                        print(f"✓ Function '{func['name']}' is correctly formatted")
                    else:
                        print(f"✗ Function '{func['name']}': {message}")
    except Exception as e:
        print(f"Error reading simple_FC.json: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test with multiple_FC.json
    print("Testing multiple_FC.json...")
    try:
        with open("multiple_FC.json", "r") as f:
            data = json.load(f)
        
        # Extract functions from the data structure
        for item in data:
            if "function" in item:
                for func in item["function"]:
                    is_valid, message = function_format_check(func)
                    if is_valid:
                        print(f"✓ Function '{func['name']}' is correctly formatted")
                    else:
                        print(f"✗ Function '{func['name']}': {message}")
    except Exception as e:
        print(f"Error reading multiple_FC.json: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test with parallel_FC.json
    print("Testing parallel_FC.json...")
    try:
        with open("parallel_FC.json", "r") as f:
            data = json.load(f)
        
        # Extract functions from the data structure
        for item in data:
            if "function" in item:
                for func in item["function"]:
                    is_valid, message = function_format_check(func)
                    if is_valid:
                        print(f"✓ Function '{func['name']}' is correctly formatted")
                    else:
                        print(f"✗ Function '{func['name']}': {message}")
    except Exception as e:
        print(f"Error reading parallel_FC.json: {e}")

if __name__ == "__main__":
    main() 