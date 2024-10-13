import argparse
import logging

def print_banner():
    yellow = "\033[93m"
    reset = "\033[0m"
    print(yellow + r"""
            __                 
 _  ____ __/ /__  _______ _  __
| |/ / // / / _ \/ __/ _ \ |/ /
|___/\_,_/_/_//_/\__/\___/___/ 

                       """ + reset + """ v0.0.2

Made by https://linkedin.com/in/mllamazares

---
""")

def get_input_params():
    """
    Parses command-line arguments and returns them.

    Returns:
        argparse.Namespace: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description='Correlates Semgrep findings with Python test code coverage. You can either provide Semgrep and coverage JSON files directly or specify a pytest folder and target app to generate them.')

    # Common arguments
    common_group = parser.add_argument_group('Common arguments')
    common_group.add_argument('-er', '--exclude_rule_regex', default='', help='Exclude Semgrep rules which name matches the provided regex.')
    common_group.add_argument('-o', '--vulncov_output_file', default='vulncov_results.json', help='Path to save the output JSON file of Vulncov (optional).')
    common_group.add_argument('-lls', '--ollama_server', default='', help="Ollama server URL (optional). If not specified, the LLM fix suggestion will not be triggered.")
    common_group.add_argument('-llm', '--ollama_model', default='codellama:latest', help="Ollama LLM model to be used (optional).")
    common_group.add_argument('-q', '--quiet', action='store_true', help="Suppress all output.")

    # Option 1 - Generate Semgrep and Coverage files
    generate_group = parser.add_argument_group('Option 1 - To run coverage and Semgrep before')
    generate_group.add_argument('-p', '--pytest_folder', required=False, help='Path to the folder containing pytest tests.')
    generate_group.add_argument('-t', '--target_app', required=False, help='Path to the target application source code.')
    generate_group.add_argument('-req', '--req_file', default='', help="Path to the requirements file for the target app.")
    generate_group.add_argument('-ve', '--venv_path', default='./.vulncov', help="The path where the virtual environment will be created.")
    generate_group.add_argument('-sc', '--semgrep_config', default='p/python', help='Specify the rules configuration to execute Semgrep (optional).')
    generate_group.add_argument('-os', '--semgrep_output_file', default='semgrep_vulns.json', help='Path to save the output JSON file of Semgrep (optional).')
    generate_group.add_argument('-oc', '--coverage_output_file', default='coverage.json', help='Path to save the output JSON file of coverage (optional).')

    # Option 2 - Provide existing Semgrep and Coverage outputs
    input_group = parser.add_argument_group('Option 2 - To feed already existing Semgrep and coverage outputs')
    input_group.add_argument('-s', '--semgrep_json_file', required=False, help='Path to the Semgrep JSON file.')
    input_group.add_argument('-c', '--coverage_json_file', required=False, help='Path to the coverage JSON file.')

    # Parse the arguments
    args = parser.parse_args()

    # Validate argument combinations
    if not (args.semgrep_json_file and args.coverage_json_file):
        if not (args.pytest_folder and args.target_app):
            parser.error("You must provide either --pytest_folder and --target_app (Option 1) or --semgrep_json_file and --coverage_json_file (Option 2).")

    return args
