import logging
import json
import uuid
import re

from datetime import datetime
from .coverage_validator import CoverageValidator
from .test_case_matcher import TestCaseMatcher

class VulnerabilityCoverageMatcher:
    def __init__(self, semgrep_filepath, coverage_filepath):
        """
        Initializes VulnerabilityCoverageMatcher with paths to Semgrep and coverage JSON files.

        Args:
            semgrep_filepath (str): Path to the Semgrep JSON file.
            coverage_filepath (str): Path to the coverage JSON file.
        """
        self.semgrep_data = self._load_json_file(semgrep_filepath)
        self.coverage_data = self._load_json_file(coverage_filepath)

        self.headers = {
            'semgrep_input_file': semgrep_filepath,
            'coverage_input_file': coverage_filepath
        }

        # Validate coverage structure
        CoverageValidator(self.coverage_data).validate_structure()

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
            logging.info(f"✍️ Excluding vulnerabilities which Semgrep rule matches the regex: {exclude_rule}")

        logging.info(f"Input vulnerabilities: {self.headers['number_vulnerabilities_input']}")
        logging.info("🤹 Correlating Semgrep findings with test code coverage...")

        matched_results = []
        matcher = TestCaseMatcher()

        for result in self.semgrep_data['results']:
            # Exclude results if the exclude_rule regex matches any part of the rule name
            if exclude_rule and re.search(exclude_rule, result['check_id']):
                continue

            file_path = result['path']
            start_line = result['start']['line']
            end_line = result['end']['line']
            vulnerability_lines = list(range(start_line, end_line + 1))

            if file_path in self.coverage_data['files']:
                test_cases = matcher.extract_test_cases(self.coverage_data['files'][file_path]['contexts'])
                matched_test_cases = matcher.match_test_cases(test_cases, vulnerability_lines)

                if matched_test_cases:
                    coverage_match = {
                        'semgrep': {
                            'fingerprint': result['extra']['fingerprint'],
                            'check_id': result['check_id'],
                            'rule_category': result['extra']['metadata']['category'],
                            'vulnerability_class': result['extra']['metadata']['vulnerability_class'],
                            'impact': result['extra']['metadata']['impact'],
                            'message': result['extra']['message'],
                            'path': result['path'],
                            'cwe': result['extra']['metadata']['cwe'],
                            'lines': result['extra']['lines'],
                            'vuln_lines': vulnerability_lines,
                        },
                        'test_cases': matched_test_cases,
                    }
                    matched_results.append(coverage_match)

        self.headers['number_vulnerabilities_matched'] = len(matched_results)
        logging.info(f"🪄 Filtered vulnerabilities: {self.headers['number_vulnerabilities_matched']}")

        final_output = {
            'summary': self.headers,
            'matched_results': matched_results,
        }

        return final_output
