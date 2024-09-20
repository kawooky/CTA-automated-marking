import os
import sqlparse
import sqlite3
import glob


def check_sql_syntax(file_path):
    with open(file_path, 'r') as file:
        file_name=os.path.basename(file_path)
        sql = file.read()
        try:
            formatted_sql = sqlparse.format(sql, reindent=True, keyword_case='upper')
            print(f"Checking syntax for {file_name}...")

            conn = sqlite3.connect(':memory:')
            cursor = conn.cursor()
            cursor.executescript(formatted_sql)
            conn.close()

            return True, f"Syntax OK for {file_name}"
        except sqlite3.Error as e:
            return False, f"Syntax error in {file_name}: {e}"


def find_and_check_sql_files(repo_dir):
    sql_files = glob.glob(f"{repo_dir}/**/*.sql", recursive=True)
    errors = []  # List to store error messages

    if not sql_files:
        return True, "No SQL files found"

    for sql_file in sql_files:
        valid, message = check_sql_syntax(sql_file)
        if not valid:
            errors.append(f"{message}")  # Include the file name in the error message

    if errors:
        return False, "\n".join(errors)  # Return all errors if any found
    return True, "All SQL files passed syntax check"