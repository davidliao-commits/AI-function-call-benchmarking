from fc_utils import load_and_prepare_data, make_function_call, print_tool_calls, convert_output_to_json, convert_functions_to_tools
from FCsimple import main
from json_processing.parse_output import parse_output, parse_query_response_FC
from json_processing.ast_checker import ast_checker
from run_eval import run_evaluation, get_possible_answer, eval_runner
import json
import sys
import os
import statistics
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def fc_score():
    simple_result = run_evaluation("simple")
    parallel_result = run_evaluation("parallel")
    multiple_result = run_evaluation("multiple")

    simple_score = simple_result["accuracy"]
    parallel_score = parallel_result["accuracy"]
    multiple_score = multiple_result["accuracy"]

    average_score = (simple_score + parallel_score + multiple_score) / 3
    print(f"Average score: {average_score}")
    return average_score

if __name__ == "__main__":
    fc_score()