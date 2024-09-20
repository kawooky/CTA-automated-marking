import os
from clone_utils import clone_or_pull_repo
from language_utils import detect_language, find_main_class
from compilation_utils import compile_repo, run_java_main
from test_utils import run_tests
from logging_utils import log_results_to_excel
from execution_utils import run_code
import sqlparse
import sqlite3
import glob


def check_sql_syntax(file_path):
    with open(file_path, 'r') as file:
        file_name=os.path.basename(file_path)
        sql = file.read()
        try:
            formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
            print(f"Checking syntax for {file_name}...")

            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.executescript(formatted_sql)
            conn.close()

            return True, f"Syntax OK for {file_name}"
        except sqlite3.Error as e:
            return False, f"Syntax error in {file_name}: {e}"


def find_and_check_sql_files(repo_dir):
    sql_files = glob.glob(f"{repo_dir}/**/*.sql", recursive=True)
    errors = []  # List to store error messages

    if not sql_files:
        return True, "No SQL files found"

    for sql_file in sql_files:
        valid, message = check_sql_syntax(sql_file)
        if not valid:
            errors.append(f"{message}")  # Include the file name in the error message

    if errors:
        return False, "\n".join(errors)  # Return all errors if any found
    return True, "All SQL files passed syntax check"























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
def process_repos(output_file):
    repos_with_names = get_repos_with_names('repos.txt')  # Read repo URLs and folder names from file
    results = []

    for repo_url, folder_name in repos_with_names.items():
        clone_dir = os.path.join(os.getcwd(), folder_name)

        # Clone the repository
        print(f"Cloning or pulling {repo_url} into {folder_name}...")
        # clone_success, clone_msg = clone_repo(repo_url, clone_dir)
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
                'HTML Validation Summary': 'N/A',
                'CSS Validation Summary': 'N/A',
            })
            continue

        # Detect the programming language
        language, compile_command, run_command = detect_language(clone_dir)
        print(f"language is {language}")

        # Compile the code
        if language == 'Java':
            main_class_path = find_main_class(clone_dir)
            if main_class_path:
                compile_success, compile_msg, run_success, run_msg = run_java_main(clone_dir, main_class_path)
            else:
                compile_success, compile_msg = compile_repo(clone_dir, compile_command)
                run_success, run_msg = True, "Main method not found, so no run attempted"
        elif language == 'HTML/CSS':
            compile_success, compile_msg = True, "No compilation needed"
            run_msg, html_results, css_results = run_code(clone_dir, run_command, language)  # Assuming run_code does not need the language parameter
        elif language =='SQL':
            compile_msg = "No compilation needed"
            run_msg = 'No run needed'
            sql_check_success, sql_check_msg = find_and_check_sql_files(clone_dir)
        else:
            compile_success, compile_msg = compile_repo(clone_dir, compile_command)
            run_success, run_msg = run_code(clone_dir, run_command, language)


        # Run tests
        test_success, test_msg, test_summary = run_tests(clone_dir, language)

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
            'SQL Validation Summary': sql_check_msg if language == 'SQL' else 'N/A',
            'HTML Validation Summary': html_results if language == 'HTML/CSS' else 'N/A',
            'CSS Validation Summary': css_results if language == 'HTML/CSS' else 'N/A',
        })

    # Log all results to an Excel file
    log_results_to_excel(results, output_file)

# Example usage
output_file = 'repo_processing_results.xlsx'
process_repos(output_file)
