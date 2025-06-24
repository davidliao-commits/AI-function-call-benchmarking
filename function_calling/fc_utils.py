from openai import OpenAI
import json
from typing import List, Dict, Any
from config import MODEL_NAME, SILICONFLOW_API_KEY

# Shared OpenAI client
client = OpenAI(
    api_key = SILICONFLOW_API_KEY,
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
    Make a function call
    
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

    CRITICAL FORMAT REQUIREMENTS:
    1. You MUST wrap ALL function calls in square brackets [].
    2. You MUST use the EXACT function name as provided (including namespace prefixes like "loan.calculate_monthly_payment").
    3. You MUST use the EXACT parameter names as provided.
    4. You MUST use the correct data types:
       - Percentages should be decimal (e.g., 5% = 0.05, not 5.0)
       - Strings should NOT have quotes (e.g., "almonds" should be almonds)
       - Numbers should match the expected type (integer vs float)
       - Scientific notation should be decimal (e.g., 10^10 = 10000000000.0)
       - Arrays should be in the format of [value1, value2, value3]
    5. Do NOT add any extra parameters not defined in the function.
    
    Format: [func_name1(params_name1=params_value1, params_name2=params_value2...), func_name2(params)]
    
    Examples of CORRECT format:
    - [loan.calculate_monthly_payment(principal=100000, interest_rate=0.05, years=15)]
    - [nutrition.get_calories(food_item=almonds, quantity=100)]
    - [calculate_em_force(b_field=5, area=2, d_time=4)]
    
    Examples of INCORRECT format:
    - loan.calculate_monthly_payment(principal=100000, interest_rate=5.0, years=15)  (missing brackets, wrong interest rate)
    - [nutrition.get_calories(food_item="almonds", quantity=100)]  (quotes around string)
    - [calculate_em_force(b_field=5, area=2, d_time=4, seed=123)]  (extra parameter)
    
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
        model = MODEL_NAME,
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