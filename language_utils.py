import os
import re

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
        elif any(file.endswith('.html') or file.endswith('.css') for file in files):
            return 'HTML/CSS', '', 'N/A'
        elif any(file.endswith('.js') for file in files):
            return 'JavaScript', '', 'node main.js'
    return 'Unknown', '', ''

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
