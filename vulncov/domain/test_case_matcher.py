import logging

class TestCaseMatcher:
    def extract_test_cases(self, context_data):
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

    def match_test_cases(self, test_cases, vulnerability_lines):
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
