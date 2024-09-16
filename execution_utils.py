import os
import webbrowser
import subprocess

import webbrowser

def run_code(repo_dir, run_command, language):
    if language == 'HTML/CSS':
        # Open the index.html file (or the main HTML file) in the default web browser
        html_file = os.path.join(repo_dir, 'index.html')  # or another common entry file
        if os.path.isfile(html_file):
            try:
                webbrowser.open(f'file:///{html_file}')
                return True, "Opened HTML file in the browser"
            except Exception as e:
                return False, f"Failed to open HTML file: {e}"
        else:
            return False, "No HTML file found to open"
    
    if run_command and run_command != 'N/A':
        try:
            subprocess.check_call(run_command, shell=True, cwd=repo_dir)
            return True, "Ran successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Run failed: {e}"
    
    return True, "No run command needed"

