import os
import shutil
import subprocess
import pandas as pd
import stat
import errno
from git import Repo

# Function to handle errors during directory removal
def handle_remove_readonly(func, path, exc):
    excvalue = exc[1]
    if func in (os.unlink, os.rmdir) and excvalue.errno == errno.EACCES:
        os.chmod(path, stat.S_IRWXU)  # Change permissions to allow deletion
        func(path)
    else:
        raise

# Function to clone a repository
def clone_repo(repo_url, clone_dir):
    try:
        Repo.clone_from(repo_url, clone_dir)
        return True, "Cloned successfully"
    except Exception as e:
        return False, str(e)

# Function to detect the language and build/run commands
def detect_language(repo_dir):
    if os.path.isfile(os.path.join(repo_dir, 'pom.xml')):
        # Maven project, compile using 'mvn compile' first, then run tests with 'mvn test'
        return 'Java', 'mvn compile', 'mvn test'
    for root, dirs, files in os.walk(repo_dir):
        if any(file.endswith('.java') for file in files):
            return 'Java', '', 'java -cp . Main'
        elif any(file.endswith('.py') for file in files):
            return 'Python', '', 'python main.py'
        elif any(file.endswith('.js') for file in files):
            return 'JavaScript', '', 'node main.js'
        elif any(file.endswith('.html') or file.endswith('.css') for file in files):
            return 'HTML/CSS', '', 'N/A'
    return 'Unknown', '', ''

# Function to compile a repository
def compile_repo(repo_dir, compile_command):
    if compile_command:
        try:
            subprocess.check_call(compile_command, shell=True, cwd=repo_dir)
            return True, "Compiled successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Compilation failed: {e}"
    return True, "No compilation needed"

# Function to run the code
def run_code(repo_dir, run_command):
    if run_command != 'N/A':
        try:
            subprocess.check_call(run_command, shell=True, cwd=repo_dir)
            return True, "Ran successfully"
        except subprocess.CalledProcessError as e:
            return False, f"Run failed: {e}"
    return True, "No run command needed"

# Function to log results to an Excel file
def log_results_to_excel(results, output_file):
    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)

# Function to read repository URLs from a text file
def read_repos_from_file(file_path):
    with open(file_path, 'r') as file:
        repos = [line.strip() for line in file.readlines() if line.strip()]
    return repos

# Main function to process repositories
def process_repos(repo_list, output_file):
    results = []

    for repo_url in repo_list:
        repo_name = repo_url.split('/')[-1].replace('.git', '')
        clone_dir = os.path.join(os.getcwd(), repo_name)

        # Clone the repository
        print(f"Cloning {repo_url}...")
        clone_success, clone_msg = clone_repo(repo_url, clone_dir)

        if not clone_success:
            results.append({
                'Repository': repo_url,
                'Clone Status': 'Failed',
                'Language': 'Unknown',
                'Compilation Status': 'N/A',
                'Run Status': 'N/A',
                'Comments': clone_msg
            })
            continue

        # Detect the programming language and build/run commands
        language, compile_command, run_command = detect_language(clone_dir)
        print(f"Detected language: {language}")

        if language == 'Unknown':
            results.append({
                'Repository': repo_url,
                'Clone Status': 'Success',
                'Language': 'Unknown',
                'Compilation Status': 'N/A',
                'Run Status': 'N/A',
                'Comments': 'Could not detect the language or no recognized build system'
            })
            # Clean up the cloned directory with error handling
            try:
                shutil.rmtree(clone_dir, onerror=handle_remove_readonly)
            except Exception as e:
                print(f"Error removing directory: {e}")
            continue

        # Compilation step (if needed)
        print(f"Compiling {repo_url}...")
        compile_success, compile_msg = compile_repo(clone_dir, compile_command)

        # Run the code if compilation (or no compilation) is successful
        if compile_success:
            print(f"Running {repo_url}...")
            run_success, run_msg = run_code(clone_dir, run_command)
        else:
            run_success = False
            run_msg = "Skipped running due to compilation failure"

        # Append the result
        results.append({
            'Repository': repo_url,
            'Clone Status': 'Success',
            'Language': language,
            'Compilation Status': 'Success' if compile_success else 'Failed',
            'Run Status': 'Success' if run_success else 'Failed',
            'Comments': f"{compile_msg}; {run_msg}"
        })

        # Clean up the cloned directory with error handling
        try:
            shutil.rmtree(clone_dir, onerror=handle_remove_readonly)
        except Exception as e:
            print(f"Error removing directory: {e}")

    # Write the results to an Excel file
    log_results_to_excel(results, output_file)
    print(f"Results logged to {output_file}")

# Path to the text file containing the list of repositories
repo_file_path = 'repos.txt'

# Output Excel file
output_excel = 'results.xlsx'

# Read repositories from file and process them
repos = read_repos_from_file(repo_file_path)
process_repos(repos, output_excel)
