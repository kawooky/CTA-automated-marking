import os
import time
import pandas as pd  # Make sure to import pandas
from language_utils import detect_language
from java_utils import java_process
from clone_utils import clone_or_pull_repo
from logging_utils import log_results_to_excel
from html_css_utils import html_css_proccess
from sql_utils import find_and_check_sql_files
from git import Repo
import tempfile  # Import tempfile for creating temporary directories

# Function to check if the output file is open
def is_file_open(file_path):
    try:
        # Try to open the file in exclusive mode
        with open(file_path, 'a'):
            return False
    except IOError:
        return True

# Function to validate if a Git repository URL is reachable
def is_valid_git_repo_url(repo_url):
    try:
        # Create a unique temporary directory for validation
        with tempfile.TemporaryDirectory() as temp_dir:
            # Attempt to clone a shallow copy (only the latest commit)
            Repo.clone_from(repo_url, temp_dir, depth=1)
        return True
    except Exception as e:
        print(f"Invalid repository URL: {repo_url}. Error: {str(e)}")
        return False

# Create a new directory for each run
def create_run_directory(base_dir='cloned_repos'):
    timestamp = time.strftime('%Y%m%d-%H%M%S')  # Create a timestamp
    run_dir = os.path.join(base_dir, timestamp)  # Combine base dir and timestamp
    os.makedirs(run_dir, exist_ok=True)  # Create the directory if it doesn't exist
    return run_dir

def get_repos_with_names(file_path='repos.txt'):
    repos_with_names = {}
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()
            if line:
                repo_url, folder_name = line.split()
                repos_with_names[repo_url] = folder_name
    return repos_with_names

# Main function to process repositories
def process_repos():
    repos_with_names = get_repos_with_names('repos.txt')  # Read repo URLs and folder names from file
    results = []
    
    # Validate all repository URLs before processing
    print('Checking repo validity')
    invalid_urls = [url for url in repos_with_names.keys() if not is_valid_git_repo_url(url)]
    if invalid_urls:
        print("The following repository URLs are invalid:")
        for url in invalid_urls:
            print(url)
        return  # Exit if there are invalid URLs
    else:
        print('Respository check successful')



    # Asking whether to append or create new file
    append = input("Do you want to append results to an existing file? (y/n): ").strip().lower() == 'y'

    if append:
        output_file = input("Enter the full path of the existing Excel file (e.g., 'C:/path/to/repo_processing_results.xlsx'): ").strip()
    else:
        # Save results to 'repo_processing_results.xlsx' in the current directory
        output_file = os.path.join(os.getcwd(), 'repo_processing_results.xlsx')
        print(f"New file will be created at: {output_file}")

        # Check if the output file is open
    if is_file_open(output_file):
        print(f"The file '{output_file}' is currently open. Please close it and try again.")
        return  # Exit the function if the file is open

    # Create a new directory for this run
    run_directory = create_run_directory()

    for repo_url, folder_name in repos_with_names.items():
        # Create a unique folder for each repository inside the new run directory
        clone_dir = os.path.join(run_directory, folder_name)

        # Clone the repository
        print(f"Cloning or pulling {repo_url} into {clone_dir}...")
        clone_success, clone_msg = clone_or_pull_repo(repo_url, clone_dir)

        if not clone_success:
            results.append({
                'Repository': repo_url,
                'Folder Name': folder_name,
                'Clone Status': f'Failed: {clone_msg}',
                'Language': 'Unknown',
                'Compilation Status': 'N/A',
                'Run Status': 'N/A',
                'Test Status': 'N/A',
                'Test Summary': 'N/A',
                'Validation Summary': 'N/A',
            })
            continue

        # Detect the programming language
        language = detect_language(clone_dir)
        print(f"Language: {language}")

        # Initialize validation messages as empty
        sql_check_msg, html_results, css_results = "", "", ""

        # Compile the code
        if language == 'Java' or language == 'Java-Maven':
            compile_success, compile_msg, run_success, run_msg, test_success, test_msg, test_summary = java_process(clone_dir, language)
        elif language == 'HTML/CSS':
            compile_success, compile_msg = True, "No compilation needed"
            test_success, test_msg, test_summary = True, "No tests available", "N/A"
            run_msg, html_results, css_results = html_css_proccess(clone_dir) 
        elif language == 'SQL':
            compile_success, compile_msg = True, "No compilation needed"
            run_msg = 'No run needed'
            test_success, test_msg, test_summary = True, "No tests available", "N/A"
            sql_check_success, sql_check_msg = find_and_check_sql_files(clone_dir)

        # Create validation summary based on language
        validation_summary = ""
        if language == 'SQL':
            validation_summary = sql_check_msg
        elif language == 'HTML/CSS':
            validation_summary = " ".join(html_results) + " " + " ".join(css_results)
        else:
            validation_summary = 'N/A'

        # Log results
        results.append({
            'Repository': repo_url,
            'Folder Name': folder_name,
            'Clone Status': 'Success',
            'Language': language,
            'Compilation Status': compile_msg,
            'Run Status': run_msg,
            'Test Status': test_msg,
            'Test Summary': test_summary,
            'Validation Summary': validation_summary,
        })

    # Log all results to an Excel file
    log_results_to_excel(results, output_file, append=append)


# Example usage
process_repos()
