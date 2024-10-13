import os
import logging
import tqdm

from ..domain.appsec_wizard import AppSecWizard

def suggest_vulnerability_fixes(matched_results, repo_path, ollama_url, ollama_model):
    """
    Suggests vulnerability fixes using the LLM (Large Language Model).

    Args:
        matched_results (dict): The results from matching Semgrep with coverage data.
        repo_path (str): Path to the repository where the code exists.
        ollama_url (str): URL to the Ollama LLM server.

    Returns:
        dict: Updated results with LLM-suggested vulnerability fixes.
    """

    template_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'llm_instructions.txt')
    with open(template_path, 'r') as file:
        template_fix = file.read()

    # Initialize AppSecWizard with repo path and LLM server URL
    vuln_processor = AppSecWizard(repo_path, ollama_url, ollama_model)
    chain = vuln_processor.create_chain(template_fix)

    # Iterate over matched vulnerabilities
    for vuln in tqdm.tqdm(matched_results['matched_results']):
        if 'test_cases' in vuln:
            # Construct the question for the LLM
            question = (f"Vulnerability details:\n"
                        f" - Vulnerability class: {', '.join(vuln['semgrep']['vulnerability_class'])}\n"
                        f" - Description: {vuln['semgrep']['message']}\n"
                        f" - Related CWE: {', '.join(vuln['semgrep']['cwe'])}\n"
                        f" - Specific vulnerable code:\n {vuln['semgrep']['lines']}\n")

            logging.info(f"🧙‍♂️ Asking the LLM wizard how to fix vulnerability {vuln['semgrep']['check_id']} in file {vuln['semgrep']['path']}...")

            # Call the LLM chain to suggest a fix
            response = chain.invoke(question)
            
            light_green = "\033[92m"
            reset_color = "\033[0m"
            logging.info(f"Response: {light_green}{response}{reset_color}")

            # Save the LLM's suggested fix in the matched results
            vuln['llm_suggested_fix'] = response

    return matched_results
