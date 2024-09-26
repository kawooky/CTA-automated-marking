import subprocess
import os
import re

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


def compile_java_non_main_repo(repo_dir):
    try:
        subprocess.check_call('mvn compile', shell=True, cwd=repo_dir)
        return True, "Compiled successfully"
    except subprocess.CalledProcessError as e:
        return False, f"Compilation failed: {e}"


# Function to compile and run the Java main method
def run_java_main(repo_dir, main_class_path):
    try:
        # Convert the main class path into a format for running with Java
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
            if os.path.commonpath([root, os.path.join(repo_dir, 'src', 'test')]) == os.path.join(repo_dir, 'src', 'test'):
                continue
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))

        # Compile all .java files
        target_dir = os.path.join(repo_dir, 'target')
        os.makedirs(target_dir, exist_ok=True)
        
        # Use absolute paths for the compile command
        compile_command = f"javac -d \"{os.path.abspath(target_dir)}\" " + " ".join(f"\"{os.path.abspath(file)}\"" for file in java_files)

        try:
            subprocess.check_call(compile_command, shell=True)
        except subprocess.CalledProcessError as compile_error:
            return False, f"Compilation failed for {main_class_path}: {compile_error}", False, f"Compilation failed so run was skipped"

        # Run the compiled Java class
        run_command = f"java -cp \"{os.path.abspath(target_dir)}\" {full_class_name}"
        subprocess.check_call(run_command, shell=True)

        return True, "Compiled successfully", True, "Main method ran successfully"
    except subprocess.CalledProcessError as run_error:
        return True, "Compiled successfully", False, f"Failed to run the main method: {run_error}"


# Function to run tests based on the detected language
def run_java_tests(clone_dir, language):
    try:
        if language == 'Java-Maven':
            test_command = 'mvn test'
            result = subprocess.run(test_command, shell=True, cwd=clone_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            output = result.stdout + result.stderr
            if 'BUILD SUCCESS' in output:
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
        else:
            return True, "No tests available", "N/A"
    except subprocess.CalledProcessError as e:
        return False, f"Test execution failed: {e}", "N/A"


def java_process(clone_dir, language):
    main_class_path = find_main_class(clone_dir)
    if main_class_path:
        compile_success, compile_msg, run_success, run_msg = run_java_main(clone_dir, main_class_path)
    else:
        compile_success, compile_msg = compile_java_non_main_repo(clone_dir)
        run_success, run_msg = True, "Main method not found, so no run attempted"

    test_success, test_msg, test_summary = run_java_tests(clone_dir, language)

    return compile_success, compile_msg, run_success, run_msg, test_success, test_msg, test_summary
