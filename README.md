# Automated Repository Processor

This Python script is designed to clone Git repositories, detect their programming languages, validate the code, and log the results to an Excel file. It provides a user-friendly interface for processing multiple repositories efficiently.

## Features

- Clone or pull repositories from Git.
- Automatically detect the programming language used in each repository.
- Validate the code based on the detected language (supports Java, HTML/CSS, and SQL).
- Log results to an Excel file, with options to append to existing files.
- User-friendly file dialog for selecting Excel files.

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

3. **Follow the prompts**:

- The script will check the validity of the repository URLs.
- You will be prompted to select an Excel file to log results using a visual dialog or create a new one.
- The results will be saved in the specified Excel file following a predetermined format.
