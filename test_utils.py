import subprocess
import os
import re

# Function to run tests based on the detected language
def run_tests(repo_dir, language):
    try:
        if language == 'Java' and os.path.isfile(os.path.join(repo_dir, 'pom.xml')):
            test_command = 'mvn test'
            result = subprocess.run(test_command, shell=True, cwd=repo_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
