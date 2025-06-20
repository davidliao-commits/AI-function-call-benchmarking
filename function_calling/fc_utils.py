from openai import OpenAI
import json
from typing import List, Dict, Any

# Shared OpenAI client
client = OpenAI(
    api_key = "sk-wosxiisuzqcpwbnmaobpgflmgxzpumvxsuvusoduscvhcdoc",
    base_url = "https://api.siliconflow.cn/v1"
)

def convert_functions_to_tools(functions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert function definitions to OpenAI tools format
    
    Args:
        functions: List of function definitions
        
    Returns:
        List of tools in OpenAI format
    """
    tools = []
    for func in functions:
        tool = {
            "type": "function",
            "function": {
                "name": func["name"],
                "description": func["description"],
                "parameters": func["parameters"]
            }
        }
        tools.append(tool)
    return tools

def load_and_prepare_data(json_file: str) -> tuple:
    """
    Load JSON data and pre-convert all functions to tools format for efficiency
    
    Args:
        json_file: Path to the JSON file
        
    Returns:
        Tuple of (data, all_tools_dict, function_names_dict)
    """
    # Load data once
    with open(json_file, "r") as f:
        data = json.load(f)
    
    # Pre-convert all functions to tools format for efficiency
    print(f"Pre-converting functions to tools format from {json_file}...")
    all_tools = {}
    function_names = {}
    
    for i, item in enumerate(data):
        try:
            functions = item["function"]
            # Convert functions to tools once per item
            tools = convert_functions_to_tools(functions)
            all_tools[i] = tools
            
            # Extract function names for tool_choice
            if functions:
                # For single function examples, use the first function name
                function_names[i] = functions[0]["name"]
            else:
                function_names[i] = None
                
        except Exception as e:
            print(f"Error converting functions for example {i+1}: {e}")
            all_tools[i] = []
            function_names[i] = None
    
    print(f"Successfully converted {len(all_tools)} examples to tools format\n")
    return data, all_tools, function_names

def make_function_call(prompt: str, tools: List[Dict[str, Any]], function_name: str = None, system_message: str = None) -> Any:
    """
    Make a function call to the OpenAI API
    
    Args:
        prompt: The user prompt
        tools: Pre-converted tools in OpenAI format
        function_name: Specific function name to use for tool_choice
        system_message: Optional custom system message
        
    Returns:
        OpenAI response message
    """
    if system_message is None:
        system_message = "you are a helpful assistant that can answer questions by calling on given functions. Always use a function if one is available."
    
    messages = [
        {
            "role": "system",
            "content": system_message
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    # Set tool_choice based on function name
    if function_name and tools:
        tool_choice = {
            "type": "function",
            "function": {
                "name": function_name
            }
        }
    else:
        tool_choice = "auto"
    
    response = client.chat.completions.create(
        model = "THUDM/glm-4-9b-chat",
        messages = messages,
        tools = tools,
        tool_choice = tool_choice,
        temperature = 0.0,
        top_p = 0.95,
        stream = False
    )
    return response.choices[0].message

def print_tool_calls(response: Any) -> None:
    """
    Print tool calls from the response
    
    Args:
        response: OpenAI response message
    """
    if response.tool_calls:
        print("Tool calls made:")
        for tool_call in response.tool_calls:
            print(f"  Function: {tool_call.function.name}")
            print(f"  Arguments: {tool_call.function.arguments}")
    else:
        print("No tool calls made") 

def convert_output_to_json(response: Any) -> dict:
    """
    Convert the function call response to a JSON format for comparison
    
    Args:
        response: OpenAI response message with tool calls
        
    Returns:
        Dictionary containing the function call information
    """
    try:
        if not response.tool_calls:
            return {"error": "No tool calls found in response"}
        
        # Extract function call information
        tool_call = response.tool_calls[0]  # Get the first tool call
        function_name = tool_call.function.name
        arguments = json.loads(tool_call.function.arguments)
        
        # Create structured output for comparison
        result = {
            "function_name": function_name,
            "arguments": arguments
        }
        
        return result
        
    except Exception as e:
        print(f"Error converting response to JSON: {e}")
        return {"error": str(e)}