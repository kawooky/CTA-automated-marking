import os
import shutil
import subprocess
import pandas as pd
import stat
import errno
from git import Repo
import re

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

# Function to find the main class in Java files
def find_main_class(repo_dir):
    main_class = None
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            if file.endswith('.java'):
                java_file = os.path.join(root, file)
                with open(java_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if re.search(r'public\s+static\s+void\s+main\s*\(\s*String\s*\[\]\s*args\s*\)', content):
                        # If a main method is found, assume the file contains the main class
                        main_class = java_file
                        break
        if main_class:
            break
    return main_class

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

# Function to compile and run the Java main method
def run_java_main(repo_dir, main_class_path):
    try:
        # Convert the main class path into a format for running with Java
        rel_path = os.path.relpath(main_class_path, repo_dir)  # Get relative path
        class_name = os.path.basename(main_class_path).replace('.java', '')  # Convert path to class name

        # Get package name if declared in the Java file
        with open(main_class_path, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'package\s+([\w\.]+);', content)
        if match:
            package_name = match.group(1)
            full_class_name = f"{package_name}.{class_name}"
        else:
            full_class_name = class_name

        # Collect all .java files in the source directory and not in test
        java_files = []
        for root, _, files in os.walk(repo_dir):
            # Skip directories that are under src/test
            if os.path.commonpath([root, os.path.join(repo_dir, 'src', 'test')]) == os.path.join(repo_dir, 'src', 'test'):
                continue
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))


        # Compile all .java files
        target_dir = os.path.join(repo_dir, 'target')  # Output directory for .class files
        os.makedirs(target_dir, exist_ok=True)  # Create target directory if it doesn't exist
        compile_command = f"javac -d {target_dir} " + " ".join(java_files)
        print(compile_command)
        print("compile command^^^^^")
        
        # Check for compilation success before running
        try:
            subprocess.check_call(compile_command, shell=True, cwd=repo_dir)
            print(f"Compilation successful for {main_class_path}.")
        except subprocess.CalledProcessError as compile_error:
            return False, f"Compilation failed for {main_class_path}: {compile_error}", False, f"Compilation failed so run was skipped"

        # If compilation was successful, run the compiled Java class
        run_command = f"java -cp {target_dir} {full_class_name}"
        subprocess.check_call(run_command, shell=True, cwd=repo_dir)

        return True, "Compiled successfully", True, "Main method ran successfully" 
    except subprocess.CalledProcessError as run_error:
        return True, "Compiled successfully", False, f"Failed to run the main method: {run_error}"

# Function to run tests based on the detected language
def run_tests(repo_dir, language):
    try:
        if language == 'Java' and os.path.isfile(os.path.join(repo_dir, 'pom.xml')):
            # Run Maven tests
            test_command = 'mvn test'
            result = subprocess.run(test_command, shell=True, cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout + result.stderr
            if 'BUILD SUCCESS' in output:
                # Extract test summary
                match = re.search(r'Tests run: (\d+), Failures: (\d+)', output)
                if match:
                    total_tests = int(match.group(1))
                    failed_tests = int(match.group(2))
                    passed_tests = total_tests - failed_tests
                    test_summary = f"{passed_tests} out of {total_tests} tests passed"
                    return True, "Tests ran successfully", test_summary
                else:
                    return True, "Tests ran successfully", "No test summary found"
            else:
                return False, "Tests failed", "N/A"
        elif language == 'Python':
            # Run Python unittests
            test_command = 'python -m unittest discover'
            result = subprocess.run(test_command, shell=True, cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout + result.stderr
            match = re.search(r'Ran (\d+) test[s] in', output)
            if match:
                total_tests = int(match.group(1))
                failures = output.count('FAILED')
                passed_tests = total_tests - failures
                test_summary = f"{passed_tests} out of {total_tests} tests passed"
                if 'OK' in output:
                    return True, "Tests ran successfully", test_summary
                else:
                    return False, "Some tests failed", test_summary
            else:
                return False, "Test output not recognized", "N/A"
        # Add logic for other languages (e.g., JavaScript) as needed
        else:
            return True, "No tests available", "N/A"
    except subprocess.CalledProcessError as e:
        return False, f"Test execution failed: {e}", "N/A"

# Function to run the code
def run_code(repo_dir, run_command):
    if run_command and run_command != 'N/A':
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
                'Test Status': 'N/A',
                'Test Summary': 'N/A',
                'Comments': clone_msg
            })
            continue

        # Detect the programming language and build/run commands
        language, compile_command, run_command = detect_language(clone_dir)
        print(f"Detected language: {language}")

        # Initialize variables for logging
        compile_success = True
        compile_msg = 'Skipped compilation'
        run_success = False
        run_msg = "N/A"
        test_success = False
        test_msg = "N/A"
        test_summary = "N/A"

        if language == 'Java':
            print(f"Searching for Java main method in {repo_url}...")
            main_class = find_main_class(clone_dir)

            if main_class:
                print(f"Found main method in {main_class}, trying to compile and run it...")
                compile_success, compile_msg, run_success, run_msg = run_java_main(clone_dir, main_class)
            else:
                run_success = False
                run_msg = "No main method found"

            # If the main method wasn't found or failed, compile and run normally
            if not main_class or not run_success:
                print(f"Compiling {repo_url}...")
                compile_success, compile_msg = compile_repo(clone_dir, compile_command)
                if compile_success:
                    print(f"Running {repo_url}...")
                    run_success, run_msg = run_code(clone_dir, run_command)

            # Run tests for Java project
            test_success, test_msg, test_summary = run_tests(clone_dir, language)

        elif language == 'Python':
            # Run Python code
            compile_success = True  # No compilation needed for Python
            run_success, run_msg = run_code(clone_dir, run_command)

            # Run Python tests
            test_success, test_msg, test_summary = run_tests(clone_dir, language)

        elif language == 'Unknown':
            results.append({
                'Repository': repo_url,
                'Clone Status': 'Success',
                'Language': 'Unknown',
                'Compilation Status': 'N/A',
                'Run Status': 'N/A',
                'Test Status': 'N/A',
                'Test Summary': 'N/A',
                'Comments': 'Could not detect the language or no recognized build system'
            })
            try:
                shutil.rmtree(clone_dir, onerror=handle_remove_readonly)
            except Exception as e:
                print(f"Error removing directory: {e}")
            continue

        # Append the result
        results.append({
            'Repository': repo_url,
            'Clone Status': 'Success',
            'Language': language,
            'Compilation Status': 'Success' if compile_success else 'Failed',
            'Run Status': 'Success' if run_success else 'Failed',
            'Test Status': 'Success' if test_success else 'Failed',
            'Test Summary': test_summary,
            'Comments': f"{compile_msg}; {run_msg}; {test_msg}"
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
