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
