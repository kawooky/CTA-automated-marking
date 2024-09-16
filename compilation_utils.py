import os
import subprocess
import re

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
            if os.path.commonpath([root, os.path.join(repo_dir, 'src', 'test')]) == os.path.join(repo_dir, 'src', 'test'):
                continue
            for file in files:
                if file.endswith('.java'):
                    java_files.append(os.path.join(root, file))

        # Compile all .java files
        target_dir = os.path.join(repo_dir, 'target')
        os.makedirs(target_dir, exist_ok=True)
        compile_command = f"javac -d {target_dir} " + " ".join(java_files)

        try:
            subprocess.check_call(compile_command, shell=True, cwd=repo_dir)
        except subprocess.CalledProcessError as compile_error:
            return False, f"Compilation failed for {main_class_path}: {compile_error}", False, f"Compilation failed so run was skipped"

        run_command = f"java -cp {target_dir} {full_class_name}"
        subprocess.check_call(run_command, shell=True, cwd=repo_dir)

        return True, "Compiled successfully", True, "Main method ran successfully" 
    except subprocess.CalledProcessError as run_error:
        return True, "Compiled successfully", False, f"Failed to run the main method: {run_error}"
    


