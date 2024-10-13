import os
import logging
import json

from .app.cli_handler import get_input_params, print_banner
from .app.result_matcher import match_results
from .app.fix_suggester import suggest_vulnerability_fixes
from .infra.venv_handler import create_virtualenv, run_coverage, run_semgrep

def main():
    args = get_input_params()
    logging.basicConfig(
        level=logging.INFO if not args.quiet else logging.CRITICAL,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    if not args.quiet:
        print_banner()

    # Step 1: Set up the virtual environment
    if args.venv_path:
        if not os.path.isdir(args.venv_path):
            create_virtualenv(args.venv_path, args.req_file)
        else:
            logging.info(f'💅 Using already existing {args.venv_path} virtual environment...')

    # Step 2: Generate coverage and semgrep JSON files if needed
    if args.pytest_folder and args.target_app:
        run_coverage(
            venv_path=args.venv_path,
            pytest_folder=args.pytest_folder,
            output_file=args.coverage_output_file,
        )

        run_semgrep(
            venv_path=args.venv_path,
            output_file=args.semgrep_output_file,
            target_app=args.target_app,
            semgrep_config=args.semgrep_config,
        )

    # Step 3: Match Semgrep findings with coverage data
    matched_results = match_results(
        args.semgrep_output_file, args.coverage_output_file, args.exclude_rule_regex
    )

    # Step 4: Use the LLM to suggest fixes, if an Ollama server URL is provided
    if args.ollama_server:
        matched_results = suggest_vulnerability_fixes(
            matched_results, args.target_app, args.ollama_server, args.ollama_model
        )

    # Step 5: Save the matched results to a file
    with open(args.vulncov_output_file, 'w') as output_file:
        json.dump(matched_results, output_file, indent=4, separators=(',', ':'))
    
    logging.info(f"💾 Vulnerability coverage results saved to {args.vulncov_output_file}.")

if __name__ == "__main__":
    main()