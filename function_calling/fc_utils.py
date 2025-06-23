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

def make_function_call(category: str, prompt: str, tools: List[Dict[str, Any]] = None, function_name: str = None, system_message: str = None) -> Any:
    """
    Make a function call using BFCL (Best Function Calling Language) format
    
    Args:
        category: Type of function calling (simple, parallel, multiple)
        prompt: The user prompt
        tools: Pre-converted tools in OpenAI format (used to inform system message)
        function_name: Specific function name (not used in BFCL)
        system_message: Optional custom system message
        
    Returns:
        Full OpenAI response object (to access token usage)
    """
    if system_message is None:
        # Create system message that includes information about available functions
        tools_info = ""
        if tools:
            tools_info = "\n\nAvailable functions:\n"
            for tool in tools:
                func = tool["function"]
                tools_info += f"- {func['name']}: {func['description']}\n"
                if "parameters" in func and "properties" in func["parameters"]:
                    tools_info += "  Parameters:\n"
                    for param_name, param_info in func["parameters"]["properties"].items():
                        tools_info += f"    - {param_name} ({param_info['type']}): {param_info['description']}\n"
        
        system_message = f"""You are an expert in composing functions. You are given a question and a set of possible functions. Based on the question, you will need to make one or more function/tool calls to achieve the purpose.
    If none of the functions can be used, point it out. If the given question lacks the parameters required by the function, also point it out.
    You should only return the function calls in your response.

    If you decide to invoke any of the function(s), you MUST put it in the format of [func_name1(params_name1=params_value1, params_name2=params_value2...), func_name2(params)]
    You SHOULD NOT include any other text in the response. You SHOULD NOT change the function name or parameter names.

    At each turn, you should try your best to complete the tasks requested by the user within the current turn. Continue to output functions to call until you have fulfilled the user's request to the best of your ability. Once you have no more functions to call, the system will consider the current turn complete and proceed to the next turn or task.{tools_info}"""

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
    
    # For BFCL, we use regular text completion without tools (SiliconFlow API limitation)
    response = client.chat.completions.create(
        model = "THUDM/glm-4-9b-chat",
        messages = messages,
        temperature = 0.0,
        top_p = 0.95,
        stream = False
    )
    return response

def print_tool_calls(response: Any) -> None:
    """
    Print function calls from the response (BFCL format)
    
    Args:
        response: Full OpenAI response object or response message
    """
    # Handle both full response object and message object
    if hasattr(response, 'choices'):
        # Full response object
        message = response.choices[0].message
    else:
        # Message object
        message = response
    
    if message.content:
        print("Function calls made:")
        print(f"  {message.content}")
    else:
        print("No function calls made")

def convert_output_to_json(response: Any) -> dict:
    """
    Convert the BFCL function call response to a JSON format for comparison
    
    Args:
        response: OpenAI response message with BFCL text
        
    Returns:
        Dictionary containing the function call information
    """
    try:
        if not response.content:
            return {"error": "No content found in response"}
        
        content = response.content.strip()
        
        # Parse BFCL format: [func_name1(params_name1=params_value1, params_name2=params_value2...), func_name2(params)]
        if not content.startswith('[') or not content.endswith(']'):
            return {"error": f"Invalid BFCL format: {content}"}
        
        # Remove outer brackets
        content = content[1:-1]
        
        # Split by function calls (comma-separated)
        function_calls = []
        current_call = ""
        bracket_count = 0
        
        for char in content:
            if char == '(':
                bracket_count += 1
            elif char == ')':
                bracket_count -= 1
            
            if char == ',' and bracket_count == 0:
                # End of function call
                function_calls.append(current_call.strip())
                current_call = ""
            else:
                current_call += char
        
        # Add the last function call
        if current_call.strip():
            function_calls.append(current_call.strip())
        
        # Parse each function call
        parsed_calls = []
        for call in function_calls:
            if '(' not in call or ')' not in call:
                continue
                
            func_name = call.split('(')[0].strip()
            params_str = call.split('(', 1)[1].rstrip(')')
            
            # Parse parameters
            arguments = {}
            if params_str:
                param_pairs = params_str.split(',')
                for pair in param_pairs:
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Try to convert value to appropriate type
                        try:
                            if value.lower() == 'true':
                                value = True
                            elif value.lower() == 'false':
                                value = False
                            elif '.' in value:
                                value = float(value)
                            else:
                                value = int(value)
                        except ValueError:
                            # Keep as string if conversion fails
                            pass
                        
                        arguments[key] = value
            
            parsed_calls.append({
                "function_name": func_name,
                "arguments": arguments
            })
        
        # Return single call or list of calls
        if len(parsed_calls) == 1:
            return parsed_calls[0]
        else:
            return parsed_calls
        
    except Exception as e:
        print(f"Error converting response to JSON: {e}")
        return {"error": str(e)}