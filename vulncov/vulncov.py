import os
import re
import json
import argparse
import logging
from datetime import datetime
import subprocess
import uuid 
import shutil

class VulnCov:
    def __init__(self, semgrep_filepath, coverage_filepath):
        """
        Initializes VulnCov with paths to Semgrep and coverage JSON files.

        Args:
            semgrep_filepath (str): Path to the Semgrep JSON file.
            coverage_filepath (str): Path to the coverage JSON file.
        """
        logging.info("Initializing VulnCov with Semgrep and coverage data.")
        self.semgrep_data = self._load_json_file(semgrep_filepath)
        self.coverage_data = self._load_json_file(coverage_filepath)

        self.headers = {
            'semgrep_input_file': semgrep_filepath,
            'coverage_input_file': coverage_filepath
        }

        self._validate_coverage_structure()

    def _load_json_file(self, filepath):
        """
        Loads JSON data from a given file.

        Args:
            filepath (str): Path to the JSON file.

        Returns:
            dict: Parsed JSON data.
        """
        logging.info(f"Loading JSON data from {filepath}.")
        with open(filepath, 'r') as file:
            return json.load(file)

    def _validate_coverage_structure(self):
        """
        Validates the structure of the coverage data to ensure contexts are present.
        """
        logging.info("Validating coverage structure.")
        if not 'contexts' in next(iter(self.coverage_data['files'].values())):
            raise ValueError(
                "Error: contexts not found. Must enable dynamic context: "
                "https://coverage.readthedocs.io/en/latest/contexts.html#dynamic-contexts. "
                "Example:\n"
                "    coverage run -m pytest demo/tests/ -o dynamic_context=test_function\n"
                "    coverage json -o coverage.json --omit=\"*/tests/*\" --show-contexts"
            )

    def _calculate_match_percentage(self, vulnerability_lines, executed_lines):
        """
        Calculates the match percentage between vulnerability lines and executed lines.

        Args:
            vulnerability_lines (list): Lines in the code where vulnerabilities are found.
            executed_lines (list): Lines in the code that were executed.

        Returns:
            tuple: A list of matched lines and the coverage match percentage.
        """
        matched_lines = set(executed_lines).intersection(vulnerability_lines)
        match_count = len(matched_lines)
        if match_count > 0:
            coverage_match_percentage = (match_count / len(vulnerability_lines)) * 100
            return list(matched_lines), coverage_match_percentage
        return [], 0

    def _extract_test_cases(self, context_data):
        """
        Extracts test case information from coverage context data.

        Args:
            context_data (dict): Coverage context data.

        Returns:
            dict: A dictionary with test case names as keys and lists of executed lines as values.
        """
        test_cases = {}

        for line, tests in context_data.items():
            for test in tests:
                if test: 
                    if test not in test_cases:
                        test_cases[test] = []
                    test_cases[test].append(int(line))

        return test_cases

    def _match_test_cases(self, test_cases, vulnerability_lines):
        """
        Matches test cases with vulnerability lines and calculates the match percentage.

        Args:
            test_cases (dict): Test cases with executed lines.
            vulnerability_lines (list): Lines in the code where vulnerabilities are found.

        Returns:
            list: List of dictionaries containing test case match details.
        """
        matched_test_cases = []

        for test_name, executed_lines in test_cases.items():
            matched_lines, coverage_match_percentage = self._calculate_match_percentage(vulnerability_lines, executed_lines)
            test_case_match = {
                'name': test_name,
                'executed_lines': executed_lines,
                'matched_lines': matched_lines,
                'coverage_match_percentage': coverage_match_percentage,
            }
            
            if coverage_match_percentage > 0:
                matched_test_cases.append(test_case_match)
        
        return matched_test_cases

    def match_semgrep_with_coverage(self, exclude_rule=''):
        """
        Matches Semgrep results with coverage data.

        Args:
            exclude_rule (str, optional): A regex pattern to exclude from matching. Defaults to ''.

        Returns:
            dict: A dictionary with a summary and matched results.
        """
        self.headers['uid'] = str(uuid.uuid4())
        self.headers['timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.headers['number_vulnerabilities_input'] = len(self.semgrep_data['results'])

        if exclude_rule:
            logging.info("Excluding vulnerabilities which semgrep rule matches the regex: {exclude_rule}".format(exclude_rule=exclude_rule))

        logging.info("Input vulnerabilities: {vinput}".format(vinput=self.headers['number_vulnerabilities_input']))
        logging.info("Correlating semgrep findings with test code coverage...")

        matched_results = []

        for result in self.semgrep_data['results']:
            # Exclude results if the exclude_rule regex matches any part of the rule name
            if exclude_rule and re.search(exclude_rule, result['check_id']):
                continue

            file_path = result['path']
            start_line = result['start']['line']
            end_line = result['end']['line']
            vulnerability_lines = list(range(start_line, end_line + 1))

            if file_path in self.coverage_data['files']:
                test_cases = self._extract_test_cases(self.coverage_data['files'][file_path]['contexts'])
                matched_test_cases = self._match_test_cases(test_cases, vulnerability_lines)

                if matched_test_cases:
                    coverage_match = {
                        'semgrep': {
                            'fingerprint': result['extra']['fingerprint'],
                            'check_id': result['check_id'],
                            'rule_category': result['extra']['metadata']['category'],
                            'vulnerability_class': result['extra']['metadata']['vulnerability_class'],
                            'impact': result['extra']['metadata']['impact'],
                            'message': result['extra']['message'],
                            'lines': result['extra']['lines'],
                            "vuln_lines": vulnerability_lines,
                        },
                        "test_cases": matched_test_cases,
                    }
                    matched_results.append(coverage_match)

        self.headers['number_vulnerabilities_matched'] = len(matched_results)

        logging.info("Final vulnerabilities: {vinput}".format(vinput=self.headers['number_vulnerabilities_matched']))

        final_output = {
            'summary': self.headers,
            'matched_results': matched_results,
        }

        return final_output


def run_coverage_and_semgrep(pytest_folder, semgrep_output_file, coverage_output_file, target_app, semgrep_config='p/python'):
    """
    Generates the coverage and Semgrep JSON files by running the specified commands.

    Args:
        pytest_folder (str): The folder containing the pytest tests.
        semgrep_output_file (str): The file path where the output JSON files of semgrep will be saved.
        coverage_output_file (str): The file path where the output JSON files of semgrep will be saved.
        target_app (str): The target application to run Semgrep on.
        semgrep_config (str, optional): The Semgrep configuration to use. Defaults to 'p/python'.

    Returns:
        tuple: Paths to the generated Semgrep and coverage JSON files.
    """

    for utility in ['semgrep', 'coverage']:
        if not shutil.which(utility):
            raise EnvironmentError(f"Error: {utility} is not installed. Please install it using `pip install {utility}`.")

    # Run coverage
    logging.info("Executing coverage...")
    config_path = os.path.join(os.path.dirname(__file__), 'coverage.cfg')
    
    subprocess.run(['coverage', 'run', '--rcfile', config_path, '-m', 'pytest', pytest_folder], check=True, stdout=subprocess.DEVNULL)
    subprocess.run([
        'coverage', 'json', '-o', coverage_output_file, 
        f'--omit={pytest_folder}*', '--show-contexts'
    ], check=True, stdout=subprocess.DEVNULL)

    logging.info(f"Coverage report generated at {coverage_output_file}.")

    # Run Semgrep
    logging.info(f"Running semgrep with config {semgrep_config}...")

    subprocess.run([
        'semgrep', '--config', semgrep_config, '--json', '--quiet', 
        '-o', semgrep_output_file, target_app
    ], check=True, stdout=subprocess.DEVNULL)
    
    logging.info(f"Semgrep results saved to {semgrep_output_file}.")


def print_banner():
    yellow = "\033[93m"
    reset = "\033[0m"

    print(yellow + r"""
            __                 
 _  ____ __/ /__  _______ _  __
| |/ / // / / _ \/ __/ _ \ |/ /
|___/\_,_/_/_//_/\__/\___/___/ 

                       """ + reset + """ v0.0.1

Made by https://linkedin.com/in/mllamazares

---
""")

def get_input_params():
    parser = argparse.ArgumentParser(description='Correlates Semgrep findings with Python test code coverage. You can either provide semgrep and coverage JSON files directly or specify a pytest folder and target app to generate them (see Options below).')

    common_group = parser.add_argument_group('Common arguments')
    common_group.add_argument('-er', '--exclude_rule_regex', default='', help='Exclude semgrep rules which name matches the provided regex')
    common_group.add_argument('-o', '--vulncov_output_file', default='vulncov_results.json', help='Path to save the output JSON file of Vulncov (optional)')
    common_group.add_argument('-q', '--quiet', default=False, help="Suppress all output")

    generate_group = parser.add_argument_group('Option 1 - To run coverage and semgrep before')
    generate_group.add_argument('-p', '--pytest_folder', required=False, help='Path to the folder containing pytest tests')
    generate_group.add_argument('-t', '--target_app', required=False, help='Path to the target application source code')
    generate_group.add_argument('-sc', '--semgrep_config', default='p/python', help='Specify the rules configuration to execute semgrep (optional).')
    generate_group.add_argument('-os', '--semgrep_output_file', default='semgrep_vulns.json', help='Path to save the output JSON file of Semgrep (optional)')
    generate_group.add_argument('-oc', '--coverage_output_file', default='coverage.json', help='Path to save the output JSON file of Coverage (optional)')

    input_group = parser.add_argument_group('Option 2 - To feed already existing Semgrep and Coverage ouputs')
    input_group.add_argument('-s', '--semgrep_json_file', required=False, help='Path to the Semgrep JSON file')
    input_group.add_argument('-c', '--coverage_json_file', required=False, help='Path to the Coverage JSON file')

    args = parser.parse_args()

    if not (args.semgrep_json_file and args.coverage_json_file):
        if not (args.pytest_folder and args.target_app):
            parser.error("You must provide either --semgrep_json_file and --coverage_json_file, or --pytest_folder and --target_app.")

    return args

def main():

    args = get_input_params()

    logging.basicConfig(
        level=logging.INFO if not args.quiet else logging.CRITICAL,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if not args.quiet:
        print_banner()

    if (args.pytest_folder and args.target_app):
        run_coverage_and_semgrep(
            pytest_folder=args.pytest_folder,
            semgrep_output_file=args.semgrep_output_file,
            coverage_output_file=args.coverage_output_file,
            target_app=args.target_app,
            semgrep_config=args.semgrep_config,
        )

    matcher = VulnCov(semgrep_filepath=args.semgrep_output_file, coverage_filepath=args.coverage_output_file)
    matched_results = matcher.match_semgrep_with_coverage(exclude_rule=args.exclude_rule_regex)

    with open(args.vulncov_output_file, 'w') as output_file:
        json.dump(matched_results, output_file, indent=4, separators=(',', ':'))
    logging.info(f"Vulnerability coverage results saved to {args.vulncov_output_file}.")

if __name__ == "__main__":
    main()
