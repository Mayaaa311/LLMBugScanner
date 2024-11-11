import os
import pandas as pd
import json
# Define the base directory and the output file path
base_directory = 'result_batches_run3'
output_file = os.path.join(base_directory, 'concatenated_summary.csv')

# Initialize an empty DataFrame to concatenate all the CSV files
concatenated_df = pd.DataFrame()

# Walk through the base directory
for root, dirs, files in os.walk(base_directory):
    for file in files:
        # Check for the specific file name
        if file == 'AlfredPros_CodeLlama-7b-Instruct-Solidity_summarized0.csv':
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")
            try:
                # Try to read only the specified columns
                df = pd.read_csv(file_path, usecols=['dataname', 'vulnerability', 'function_name'], on_bad_lines='skip')
            except ValueError:
                # If columns are unmatched or there's another error, read the first three columns
                try:
                    df = pd.read_csv(file_path, usecols=[0, 1, 2], on_bad_lines='skip')
                    df.columns = ['dataname', 'vulnerability', 'function_name']
                except Exception as e:
                    print(f"Error processing file: {file_path}, error: {e}")
                    continue
            
            concatenated_df = pd.concat([concatenated_df, df], ignore_index=True)

# Drop null values and duplicates
concatenated_df.dropna(inplace=True)
concatenated_df.drop_duplicates(inplace=True)

# Save the concatenated DataFrame to the output file
concatenated_df.to_csv(output_file, index=False)
print(f"Concatenated CSV saved to {output_file}")


# Load the label dictionary from the JSON file
label_file_path = 'data_full/CVE_label/CVElabel3_full.json'

with open(label_file_path, 'r') as label_file:
    labels = json.load(label_file)
# Remove the 'CVE-' prefix from the keys in the label dictionary if present
labels = {k[4:] if k.startswith("CVE-") else k: v for k, v in labels.items()}


total_labels = concatenated_df['dataname'].nunique()
hits = 0
# Check each row in concatenate_df against the labels
for _, row in concatenated_df.iterrows():
    if row['dataname'] in labels:
        label = labels[row['dataname']]
        if ((row['function_name'] == label['vulnerable_function_name']) & (row['vulnerability'] == label['vulnerability_type'] )):
            hits += 1
            continue  # Count only one hit per label per file
# Calculate hit rate
hit_rate = hits / total_labels if total_labels > 0 else 0
print(f"Hit Rate: {hit_rate:.2f} ({hits}/{total_labels})")



