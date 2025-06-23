import json
import ast
from function_calling.fc_utils import convert_output_to_json, load_and_prepare_data
from function_calling.FCsimple import main


def parse_output(output:dict):
    """
    Parse the output of the function call and return the function name and arguments
    """
    function_name = output["function_name"]
    arguments = output["arguments"]
    return function_name, arguments


def parse_query_response_FC(api_response: any) -> dict:
    return {
        "model_responses": api_response,
        "input_token": api_response.usage.prompt_tokens,      # ← API provides this
        "output_token": api_response.usage.completion_tokens, # ← API provides this
    }
