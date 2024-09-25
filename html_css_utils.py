import os
import webbrowser
import requests
from pathlib import Path  # Import pathlib for better path handling

def validate_html(html_file):
    print(f"Validating: {Path(html_file).name}")
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
        errors = [
            f"Line {message.get('lastLine', 'N/A')}, Column {message.get('lastColumn', 'N/A')}: {message['message']}"
            for message in result.get('messages', []) if message['type'] == 'error'
        ]
        if errors:
            return False, f"HTML validation issues found: {errors}"
        return True, "HTML validation passed successfully"
    else:
        return False, f"Failed to validate HTML: {response.status_code}"

def validate_css(css_file):
    print(f"Validating: {Path(css_file).name}")
    """Validates CSS using the W3C CSS Validator API."""
    
    with open(css_file, 'r', encoding='utf-8') as file:
        css_content = file.read()

    try:
        # Prepare parameters for the API call
        params = {
            'output': 'json',        # Output format
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

def html_css_proccess(clone_dir):
    html_results = []
    css_results = []

    # Traverse the repository directory to find all HTML and CSS files
    for root, dirs, files in os.walk(clone_dir):
        for file in files:
            if file.endswith(".html"):
                html_file = Path(root) / file  # Use Path for consistent path handling

                print(f'This is the file path to the html file {html_file}')

                # Validate HTML
                html_validation_status, html_validation_msg = validate_html(html_file)
                html_results.append(f"{file} {html_validation_msg}")

                # Try opening the HTML file in the browser
                try:
                    html_file_path = html_file.resolve()  # Get the absolute path
                    print(f'Does the html_file exist?: {html_file_path.exists()}')

                    # Convert path to URI and open in browser
                    webbrowser.open(html_file_path.as_uri())
                    run_msg = f"Opened {file} successfully in browser"
                except Exception as e:
                    run_msg = f"Failed to open {file}: {e}"
                print(run_msg)

            elif file.endswith(".css"):
                css_file = Path(root) / file  # Use Path for consistent path handling

                # Validate CSS
                css_validation_status, css_validation_msg = validate_css(css_file)
                css_results.append(f"{file} {css_validation_msg}")

    return run_msg, html_results, css_results
