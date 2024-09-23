import os



from language_utils import detect_language
from java_utils import java_process
from clone_utils import clone_or_pull_repo
from logging_utils import log_results_to_excel
from html_css_utils import html_css_proccess
from sql_utils import find_and_check_sql_files





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
        language = detect_language(clone_dir)
        print(f"Language: {language}")



        # Compile the code
        if language == 'Java' or language == 'Java-Maven':
            compile_success, compile_msg, run_success, run_msg, test_success, test_msg, test_summary = java_process(clone_dir, language)
        elif language == 'HTML/CSS':
            compile_success, compile_msg = True, "No compilation needed"
            test_success, test_msg, test_summary = True, "No tests available", "N/A"
            run_msg, html_results, css_results = html_css_proccess(clone_dir) 
        elif language =='SQL':
            compile_success, compile_msg = True, "No compilation needed"
            run_msg = 'No run needed'
            test_success, test_msg, test_summary = True, "No tests available", "N/A"
            sql_check_success, sql_check_msg = find_and_check_sql_files(clone_dir)



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