import os
import webbrowser
import subprocess
import requests

def validate_html(html_file):
    """Validates HTML using the W3C Validator API."""
    with open(html_file, 'r', encoding='utf-8') as file:
        html_content = file.read()

    response = requests.post(
        'https://validator.w3.org/nu/?out=json',
        headers={'Content-Type': 'text/html; charset=utf-8'},
        data=html_content
    )

    if response.status_code == 200:
        result = response.json()
        errors = [message['message'] for message in result.get('messages', []) if message['type'] == 'error']
        if errors:
            return False, f"HTML validation issues found: {errors}"
        return True, "HTML validation passed successfully"
    else:
        return False, f"Failed to validate HTML: {response.status_code}"

def validate_css(css_file):
    """Validates CSS using the W3C CSS Validator API."""
    with open(css_file, 'r', encoding='utf-8') as file:
        css_content = file.read()

    response = requests.post(
        'https://jigsaw.w3.org/css-validator/validator',
        params={'profile': 'css3', 'output': 'json'},
        headers={'Content-Type': 'text/css'},
        data=css_content
    )

    if response.status_code == 200:
        result = response.json()
        if 'cssvalidation' in result and result['cssvalidation']['errors']:
            return False, f"CSS validation issues found: {result['cssvalidation']['errors']}"
        return True, "CSS validation passed successfully"
    else:
        return False, f"Failed to validate CSS: {response.status_code}"

def run_code(repo_dir, run_command, language):
    if language == 'HTML/CSS':
        # Open the index.html file (or the main HTML file) in the default web browser
        html_file = os.path.join(repo_dir, 'index.html')  # or another common entry file
        css_file = os.path.join(repo_dir, 'styles.css')  # Assuming 'styles.css' is the CSS file

        # Validate HTML
        if os.path.isfile(html_file):
            validation_result, message = validate_html(html_file)
            if not validation_result:
                return False, message  # Return early if HTML validation fails

            try:
                webbrowser.open(f'file:///{html_file}')
            except Exception as e:
                return False, f"Failed to open HTML file: {e}"
        else:
            return False, "No HTML file found to open"

        # Validate CSS (optional if CSS file is present)
        if os.path.isfile(css_file):
            validation_result, message = validate_css(css_file)
            if not validation_result:
                return False, message  # Return early if CSS validation fails

        return True, "Opened HTML file in the browser and validation passed"
    
    # For other languages, execute the run command if provided
    if run_command and run_command != 'N/A':
        try:
            subprocess.check_call(run_command, shell=True, cwd=repo_dir)
            return True, "Ran successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Run failed: {e}"
    
    return True, "No run command needed"
