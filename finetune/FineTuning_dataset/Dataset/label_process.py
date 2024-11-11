import pandas as pd

# Load the Excel file with multiple sheets
file_path = "finetune/FineTuning_dataset/Dataset/ground_truth_label.xlsx"  # Replace with your actual file path
excel_file = pd.ExcelFile(file_path)

# Initialize an empty list to store each sheet's DataFrame
sheets = []

# Loop through each sheet in the Excel file
for sheet_name in excel_file.sheet_names:
    # Load the sheet into a DataFrame
    df = excel_file.parse(sheet_name)
    
    # Add a column with the sheet name as 'vul_type'
    df['vul_type'] = sheet_name
    
    # Append the modified DataFrame to the list
    sheets.append(df)

# Concatenate all sheets into a single DataFrame
single_sheet_df = pd.concat(sheets, ignore_index=True)

# Remove columns starting with 'Unnamed'
single_sheet_df = single_sheet_df.loc[:, ~single_sheet_df.columns.str.startswith('Unnamed')]

# Save to a new CSV file
output_file = "finetune/FineTuning_dataset/Dataset/combined_single_sheet.csv"
single_sheet_df.to_csv(output_file, index=False)

print(f"Combined single-sheet CSV saved as {output_file}")
