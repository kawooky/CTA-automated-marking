# Repository Processing Tool

This project provides a Python script to automate the process of cloning Git repositories, detecting their programming languages, running compilation or validation processes based on the detected language, and logging results to an Excel file. It supports various types of repositories, including Java, HTML/CSS, and SQL.

## Features

- Clone or pull repositories from a list of URLs.
- Detect the programming language of each repository.
- Perform language-specific processes:
  - **Java/Java-Maven**: Compilation, execution, and testing.
  - **HTML/CSS**: Validation of HTML and CSS files.
  - **SQL**: Validation of SQL files.
- Log results to an Excel file.

## Requirements

- Python 3.x
- The dependencies listed in `requirements.txt`.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/kawooky/CTA-automated-marking
   cd CTA-automated-marking
   ```

2. **Install dependencies**: Ensure you have pip installed. Then run the following command to install the required dependencies from requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Prepare the repository list**:

- Edit the repos.txt file in the root directory of the project.
- This file should contain the repository URLs and folder names, one per line, in the following format:

  ```txt
  https://github.com/user/repo_name folder_name
  ```

- Here’s an example of a `repos.txt` file:

  ```txt
  https://github.com/example-user/java-project my-java-project
  https://github.com/example-user/html-css-project my-html-css-project
  https://github.com/example-user/sql-project my-sql-project
  ```

2. **Run the script**:

- Run the following command to start the script:

  ```bash
  python repo_processing.py
  ```

- The script will:
  - Clone or pull the repositories listed in repos.txt.
  - Detect the programming language of each repository.
  - Perform the appropriate processing (compilation, validation, etc.).
  - Log the results in an Excel file named repo_processing_results.xlsx.

3. **Check the results**

- Once the script has finished running, the results will be saved in an Excel file (repo_processing_results.xlsx).
- This file will contain detailed information about:
  - Repository URL and folder name
  - Clone status (success or failure)
  - Detected programming language
  - Compilation status (if applicable)
  - Run status (if applicable)
  - Test status and test summary (if applicable)
  - HTML and CSS validation results (if applicable)
  - SQL file validation results (if applicable)
