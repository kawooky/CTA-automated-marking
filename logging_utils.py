import pandas as pd
import os

def log_results_to_excel(results, output_file, append=False):
    df = pd.DataFrame(results)  # Convert results to DataFrame

    if append and os.path.exists(output_file):
        # If append mode is selected, open the Excel file in append mode
        with pd.ExcelWriter(output_file, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            try:
                # Try to access the existing 'Results' sheet
                startrow = writer.sheets['Results'].max_row  # Get the last row of the 'Results' sheet
                df.to_excel(writer, index=False, sheet_name='Results', startrow=startrow, header=False)  # Append without header
            except KeyError:
                # If 'Results' sheet does not exist, create it and write the DataFrame
                df.to_excel(writer, index=False, sheet_name='Results')  # Write to new 'Results' sheet
    else:
        # Otherwise, create a new Excel file
        df.to_excel(output_file, index=False, sheet_name='Results')
