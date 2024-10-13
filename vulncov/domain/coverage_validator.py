import logging

class CoverageValidator:
    def __init__(self, coverage_data):
        """
        Initializes the CoverageValidator with coverage data.

        Args:
            coverage_data (dict): The JSON data from the coverage report.
        """
        self.coverage_data = coverage_data

    def validate_structure(self):
        """
        Validates the structure of the coverage data to ensure contexts are present.
        
        Raises:
            ValueError: If the coverage data does not contain the required 'contexts'.
        """

        if 'contexts' not in next(iter(self.coverage_data['files'].values())):
            raise ValueError(
                "Error: contexts not found. Must enable dynamic context: "
                "https://coverage.readthedocs.io/en/latest/contexts.html#dynamic-contexts. "
                "Example:\n"
                "    coverage run -m pytest demo/tests/ -o dynamic_context=test_function\n"
                "    coverage json -o coverage.json --omit=\"*/tests/*\" --show-contexts"
            )
