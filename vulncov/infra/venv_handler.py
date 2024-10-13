import os
import subprocess
import venv
import logging
import shutil

def create_virtualenv(venv_path, req_file):
    """
    Creates a virtual environment and installs dependencies.

    Args:
        venv_path (str): Path where the virtual environment will be created.
        req_file (str): Path to the requirements file for the target app (optional).
    """
    logging.info(f"🐍 Creating virtual environment at {venv_path}...")
    
    # Create the virtual environment
    venv.create(venv_path, with_pip=True)

    # Get the path to the pip executable inside the virtual environment
    pip_executable = os.path.join(venv_path, 'bin', 'pip')

    # Install target app dependencies from the provided requirements file
    if req_file:
        logging.info(f"Installing target app dependencies from {req_file}...")
        subprocess.run([pip_executable, 'install', '-r', req_file], check=True, stdout=subprocess.DEVNULL)

    # Install default dependencies from the 'venv_reqs.txt' file
    logging.info("Installing default dependencies (coverage, pytest, semgrep)...")
    venv_reqs_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'venv_reqs.txt')
    
    subprocess.run([pip_executable, 'install', '-r', venv_reqs_path], check=True, stdout=subprocess.DEVNULL)

    logging.info("🎉 Virtual environment setup complete.")

def run_coverage(venv_path, pytest_folder, output_file):
    """
    Generates the coverage JSON file by running the specified commands.

    Args:
        venv_path (str): Path to the virtual environment.
        pytest_folder (str): The folder containing the pytest tests.
        output_file (str): The file path where the output JSON file of coverage will be saved.
    """
    coverage_path = os.path.join(venv_path, 'bin', 'coverage')

    # Check if coverage executable exists
    if not shutil.which(coverage_path):
        raise EnvironmentError(f"Error: {coverage_path} is not installed. Please ensure the virtual environment is set up properly.")

    logging.info("🗺️ Executing coverage...")
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'coverage.cfg')

    # Run coverage to collect test coverage data
    subprocess.run([coverage_path, 'run', '--rcfile', config_path, '-m', 'pytest', pytest_folder], check=True, stdout=subprocess.DEVNULL)
    
    # Generate coverage JSON report
    subprocess.run([
        coverage_path, 'json', '-o', output_file, 
        f'--omit={pytest_folder}*', '--show-contexts'
    ], check=True, stdout=subprocess.DEVNULL)

    logging.info(f"Coverage report generated at {output_file}.")

def run_semgrep(venv_path, output_file, target_app, semgrep_config='p/python'):
    """
    Generates the Semgrep JSON file by running the specified commands.

    Args:
        venv_path (str): Path to the virtual environment.
        output_file (str): The file path where the output JSON file of Semgrep will be saved.
        target_app (str): The target application to run Semgrep on.
        semgrep_config (str, optional): The Semgrep configuration to use. Defaults to 'p/python'.
    """
    semgrep_path = os.path.join(venv_path, 'bin', 'semgrep')

    # Check if semgrep executable exists
    if not shutil.which(semgrep_path):
        raise EnvironmentError(f"Error: {semgrep_path} is not installed. Please ensure the virtual environment is set up properly.")

    logging.info(f"🔎 Running Semgrep with config {semgrep_config}...")

    # Run Semgrep with the specified configuration
    subprocess.run([
        semgrep_path, '--config', semgrep_config, '--json', '--quiet', 
        '-o', output_file, target_app
    ], check=True, stdout=subprocess.DEVNULL)

    logging.info(f"Semgrep results saved to {output_file}.")
