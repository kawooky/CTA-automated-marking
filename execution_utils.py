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

    try:
        # Prepare parameters for the API call
        params = {
            'output': 'json',        # Output format, you can also use 'text', 'html', 'soap12'
            'text': css_content      # Pass the raw CSS content to be validated
        }

        # Send the request to the validator
        response = requests.get(
            'https://jigsaw.w3.org/css-validator/validator',
            params=params,
            headers={'Content-Type': 'text/css'},
        )
        
        
        # Check response status
        if response.status_code == 200:
            result = response.json()
            
            # Check for errors in the validation result
            if 'cssvalidation' in result and result['cssvalidation'].get('errors', []):
                errors = result['cssvalidation']['errors']
                
                # Extract only the 'message' from each error
                error_messages = [error['message'] for error in errors]
                return False, f"CSS validation issues found: {error_messages}"
            
            return True, "CSS validation passed successfully"
        else:
            # If the status code is not 200, print the error details
            print(f"Failed to validate CSS: {response.status_code}, {response.text}")
            return False, f"Failed to validate CSS: {response.status_code}, {response.text}"

    except Exception as e:
        print(f"An error occurred: {e}")
        return False, f"An error occurred: {e}"







def run_code(repo_dir, run_command, language):
    if language == 'HTML/CSS':
        # Open the index.html file (or the main HTML file) in the default web browser
        html_file = os.path.join(repo_dir, 'index.html')  # or another common entry file
        css_file = os.path.join(repo_dir, 'styles.css')  # Assuming 'styles.css' is the CSS file


        # Validate HTML
        if os.path.isfile(html_file):
            html_validation_status, html_validation_msg = validate_html(html_file)

            try:
                webbrowser.open(f'file:///{html_file}')
                run_msg = "Opened HTML successfully in browser"
            except Exception as e:
                run_msg = f"Failed to open HTML file: {e}"
        else: 
            html_validation_status, html_validation_msg = False, "No HTML file found"

        if os.path.isfile(css_file):
            css_validation_status, css_validation_msg = validate_css(css_file)
        else:
            css_validation_status, css_validation_msg = "N/A", "No CSS file found"


        return run_msg, html_validation_msg, css_validation_msg

    




    # For other languages, execute the run command if provided
    if run_command and run_command != 'N/A':
        try:
            subprocess.check_call(run_command, shell=True, cwd=repo_dir)
            return True, "Ran successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Run failed: {e}"
    
    return True, "No run command needed"
