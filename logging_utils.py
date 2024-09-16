import pandas as pd

# Function to log results to an Excel file
def log_results_to_excel(results, output_file):
    df = pd.DataFrame(results)
    df.to_excel(output_file, index=False)
