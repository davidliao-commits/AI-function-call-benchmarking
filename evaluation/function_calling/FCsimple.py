from fc_utils import load_and_prepare_data, make_function_call, print_tool_calls, convert_output_to_json
# may be disused, but good example of function calling
def main(category: str):
    # Load data and pre-convert functions to tools format
    if category == "simple":
        data, all_tools, function_names = load_and_prepare_data("../FC-samples/simple_FC.json")
        
    elif category == "multiple":
        data, all_tools, function_names = load_and_prepare_data("../FC-samples/multiple_FC.json")
    elif category == "parallel":
        data, all_tools, function_names = load_and_prepare_data("../FC-samples/parallel_FC.json")
        
    for i, item in enumerate(data):
            try:
                prompt = item["question"][0][0]["content"]
                tools = all_tools[i]
                function_name = function_names[i]
                
                print(f"\n--- Example {i+1}: {item['id']} ---")
                print(f"Prompt: {prompt}")
                print(f"Target Function: {function_name}")
                
                full_response = make_function_call(category, prompt, tools, function_name)
                print_tool_calls(full_response)
                
                # Extract message for conversion
                response_message = full_response.choices[0].message
                converted_output = convert_output_to_json(response_message)
                print("converted output:",converted_output)
                
                           
            except Exception as e:
                print(f"Error processing example {i+1}: {e}")
                print(f"Full error: {type(e).__name__}: {str(e)}")
    


