import os
import logging
import tqdm

from ..domain.appsec_wizard import AppSecWizard

def suggest_vulnerability_fixes(matched_results, repo_path, llm_service,  model, api_key=None, base_url=None):
    """
    Suggests vulnerability fixes using the LLM (Large Language Model).

    Args:
        matched_results (dict): The results from matching Semgrep with coverage data.
        repo_path (str): Path to the repository where the code exists.
        llm_service (str): LLM service provider (e.g., 'ollama', 'openai', 'anthropic').
        model (str): The model name for the LLM.
        api_key (str): API key for external LLM services (if required).
        base_url (str): Base URL for self-hosted models (e.g., Ollama).

    Returns:
        dict: Updated results with LLM-suggested vulnerability fixes.
    """

    template_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'llm_instructions.txt')
    with open(template_path, 'r') as file:
        template_fix = file.read()

    llm = AppSecWizard(service=llm_service, model=model, api_key=api_key, base_url=base_url)
    chain = llm.create_chain(template_fix, retriever)

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
