import os
from clone_utils import clone_or_pull_repo
from language_utils import detect_language, find_main_class
from compilation_utils import compile_repo, run_java_main
from test_utils import run_tests
from logging_utils import log_results_to_excel
from execution_utils import run_code


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
            run_msg, html_validation_msg, css_validation_msg = run_code(clone_dir, run_command, language)  # Assuming run_code does not need the language parameter
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
            'HTML Validation Summary': html_validation_msg if language == 'HTML/CSS' else 'N/A',
            'CSS Validation Summary': css_validation_msg if language == 'HTML/CSS' else 'N/A',
        })

    # Log all results to an Excel file
    log_results_to_excel(results, output_file)

# Example usage
output_file = 'repo_processing_results.xlsx'
process_repos(output_file)
