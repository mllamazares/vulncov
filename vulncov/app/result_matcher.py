import logging

from ..domain.vuln_coverage_matcher import VulnerabilityCoverageMatcher

def match_results(semgrep_output_file, coverage_output_file, exclude_rule_regex):
    """
    Matches Semgrep and coverage results using VulnerabilityCoverageMatcher.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        dict: A dictionary with a summary and matched results.
    """
    logging.info("🤹 Correlating Semgrep findings with test code coverage...")

    # Initialize the VulnerabilityCoverageMatcher instance with Semgrep and coverage JSON file paths
    matcher = VulnerabilityCoverageMatcher(
        semgrep_filepath=semgrep_output_file, 
        coverage_filepath=coverage_output_file
    )

    # Perform the matching process, applying the exclusion rule if provided
    matched_results = matcher.match_semgrep_with_coverage(exclude_rule=exclude_rule_regex)

    return matched_results
