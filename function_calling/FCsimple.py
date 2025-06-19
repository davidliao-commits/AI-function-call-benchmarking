from fc_utils import load_and_prepare_data, make_function_call, print_tool_calls, convert_output_to_json

def main():
    # Load data and pre-convert functions to tools format
    data, all_tools, function_names = load_and_prepare_data("../FC-samples/simple_FC.json")
    
    # Process each example with pre-converted tools
    for i, item in enumerate(data):
        try:
            prompt = item["question"][0][0]["content"]
            tools = all_tools[i]
            function_name = function_names[i]
            
            print(f"\n--- Example {i+1}: {item['id']} ---")
            print(f"Prompt: {prompt}")
            print(f"Target Function: {function_name}")
            
            response = make_function_call(prompt, tools, function_name)
            print_tool_calls(response)
            converted_output = convert_output_to_json(response)
            
        
                
        except Exception as e:
            print(f"Error processing example {i+1}: {e}")
            print(f"Full error: {type(e).__name__}: {str(e)}")
            

if __name__ == "__main__":
    main()
