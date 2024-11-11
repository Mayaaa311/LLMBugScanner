# import os
# import csv
# import json

# # Path to the base folder and JSON file
# base_folder = 'result_batches_run3/'
# json_file_path = 'data_full/CVE_label/CVElabel3_full.json'

# # Load JSON data
# with open(json_file_path, 'r') as jsonfile:
#     json_data = json.load(jsonfile)

# # Function to compare vulnerabilities and functions
# def compare_vulnerabilities(csv_data, json_data, dataname):
#     results = []
#     print("json data is : ",json_data)
#     dataname = "CVE-"+dataname
#     print(dataname,"-"*20)
    
#     for csv_row in csv_data:
#         vulnerability = csv_row['vulnerability']
#         function_name = csv_row['function_name']
        
#         # Check if dataname exists in JSON
#         if dataname in json_data:
#             json_vulnerability = json_data[dataname]["vulnerability_type"]
#             json_function_name = json_data[dataname]["vulnerable_function_name"]
            
#             # Compare vulnerability and function names
#             print("-"*20)
#             print("vulnerability: ",vulnerability)
#             print("json_vulnerability: ",json_vulnerability)
#             print("function_name: ",function_name)
#             print("json_function_name: ",json_function_name)
#             if vulnerability == json_vulnerability and function_name == json_function_name:
#                 result = (dataname, vulnerability, function_name, 'True')
#             else:
#                 result = (dataname, vulnerability, function_name, 'False')
#         else:
#             result = (dataname, vulnerability, function_name, 'False')
        
#         results.append(result)
    
#     return results

# # Function to extract data from the CSV-formatted text
# def extract_data_from_text_file(file_path):
#     csv_data = []
    
#     with open(file_path, 'r') as file:
#         lines = file.readlines()
        
#         # Skip introductory lines and locate the CSV part
#         csv_start_index = 0
#         for i, line in enumerate(lines):
#             if "dataname,vulnerability,function_name" in line:
#                 csv_start_index = i + 1
#                 break
        
#         # Read the CSV lines after the header line
#         csv_lines = lines[csv_start_index:]
        
#         # Parse CSV lines
#         csvreader = csv.reader(csv_lines)
#         for row in csvreader:
#             if len(row) == 3:  # Ensure the row has the expected columns
#                 csv_data.append({
#                     'dataname': row[0],
#                     'vulnerability': row[1],
#                     'function_name': row[2]
#                 })
    
#     return csv_data

# # Function to process a folder
# def process_folder(folder_path, json_data):
#     # Extract the dataname from the folder name
#     dataname = os.path.basename(folder_path)
    
#     # Path to the file inside the folder
#     file_path = os.path.join(folder_path, 'final_output/AlfredPros_CodeLlama-7b-Instruct-Solidity_summarized0.csv')
    
#     # Check if the file exists
#     if os.path.exists(file_path):
#         print(f"Processing file: {file_path}")
        
#         # Extract data from the text-based file
#         csv_data = extract_data_from_text_file(file_path)
        
#         # Run the comparison
#         comparison_results = compare_vulnerabilities(csv_data, json_data, dataname)
#         return comparison_results
#     else:
#         print(f"File not found in {folder_path}")
#         return []

# # Function to process all folders in the base directory
# def process_all_folders(base_folder, json_data):
#     all_results = []
    
#     # Iterate through all subdirectories in the base folder
#     for folder_name in os.listdir(base_folder):
#         folder_path = os.path.join(base_folder, folder_name)
        
#         if os.path.isdir(folder_path):
#             # Process the folder
#             folder_results = process_folder(folder_path, json_data)
#             folder_results = list(set(folder_results))
#             all_results.extend(folder_results)
    
#     return all_results

# # Run the comparison for all folders
# all_comparison_results = process_all_folders(base_folder, json_data)

# # Output the results
# print("Comparison Results:")
# for result in all_comparison_results:
#     print(result)

# # Optional: Save the results to a CSV
# output_csv_path = 'evaluation.csv'
# with open(output_csv_path, mode='w', newline='') as file:
#     writer = csv.writer(file)
#     writer.writerow(['dataname', 'vulnerability', 'function_name', 'match'])
#     writer.writerows(all_comparison_results)




import os
import csv
import json

# Path to the base folder and JSON file
base_folder = 'result_batches_run3/'
json_file_path = 'data_full/CVE_label/CVElabel3_full.json'

# Load JSON data
with open(json_file_path, 'r') as jsonfile:
    json_data = json.load(jsonfile)

# Function to compare vulnerabilities and functions
def compare_vulnerabilities(csv_data, json_data, dataname):
    results = []
    dataname = "CVE-" + dataname
    true_answer_line = "N/A"  # Initialize as N/A, to be updated if a true match is found
    
    # Deduplicate the CSV data based on 'vulnerability' and 'function_name' before processing
    unique_csv_data = { (row['vulnerability'], row['function_name']): row for row in csv_data }.values()
    
    # Check if dataname exists in JSON
    if dataname not in json_data:
        print(f"Warning: {dataname} not found in JSON data")
        general_determination = (dataname, "N/A", "N/A", 'False', true_answer_line)
        return results, general_determination

    for i, csv_row in enumerate(unique_csv_data, start=1):
        vulnerability = csv_row['vulnerability']
        function_name = csv_row['function_name']
        
        # Get vulnerability and function name from JSON
        json_vulnerability = json_data[dataname]["vulnerability_type"]
        json_function_name = json_data[dataname]["vulnerable_function_name"]
        
        # Compare function name only
        match = function_name == json_function_name
        result = (dataname, vulnerability, function_name, 'True' if match else 'False')
        
        if match and true_answer_line == "N/A":
            true_answer_line = i  # Update to the first true match line number

        results.append(result)
    
    # Remove duplicates from the current results list after processing
    results = list(set(results))
    
    # Check if there's any `True` match in the results for this file
    any_true_match = any(result[3] == 'True' for result in results)
    
    # Create a general determination result based on whether there's a true match, and add the line number of the first true answer
    general_determination = (dataname, json_vulnerability, json_function_name, 'True' if any_true_match else 'False', true_answer_line)
    
    return results, general_determination

# Function to extract data from the CSV-formatted text
def extract_data_from_text_file(file_path):
    csv_data = []
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        # Skip introductory lines and locate the CSV part
        csv_start_index = 0
        for i, line in enumerate(lines):
            if "dataname,vulnerability,function_name" in line:
                csv_start_index = i + 1
                break
        
        # Read the CSV lines after the header line
        csv_lines = lines[csv_start_index:]
        
        # Parse CSV lines
        csvreader = csv.reader(csv_lines)
        for row in csvreader:
            if len(row) == 3:  # Ensure the row has the expected columns
                csv_data.append({
                    'dataname': row[0],
                    'vulnerability': row[1],
                    'function_name': row[2]
                })
    
    return csv_data

# Function to process a folder
def process_folder(folder_path, json_data):
    # Extract the dataname from the folder name
    dataname = os.path.basename(folder_path)
    
    # Path to the file inside the folder
    file_path = os.path.join(folder_path, 'final_output/AlfredPros_CodeLlama-7b-Instruct-Solidity_summarized0.csv')
    
    # Check if the file exists
    if os.path.exists(file_path):
        print(f"Processing file: {file_path}")
        
        # Extract data from the text-based file
        csv_data = extract_data_from_text_file(file_path)
        
        # Run the comparison and deduplicate the results within this file
        comparison_results, general_determination = compare_vulnerabilities(csv_data, json_data, dataname)
        return comparison_results, general_determination
    else:
        print(f"File not found in {folder_path}")
        return [], None

# Function to process all folders in the base directory
def process_all_folders(base_folder, json_data):
    all_results = []
    general_determinations = []
    
    # Iterate through all subdirectories in the base folder
    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        
        if os.path.isdir(folder_path):
            # Process the folder and deduplicate each file's results
            folder_results, general_determination = process_folder(folder_path, json_data)
            all_results.extend(folder_results)  # Aggregate deduplicated results for detailed output
            
            if general_determination:
                general_determinations.append(general_determination)  # Collect aggregated results for general output
    
    return all_results, general_determinations

# Run the comparison for all folders
all_comparison_results, all_general_determinations = process_all_folders(base_folder, json_data)

# Calculate accuracy based on general determinations
true_matches = sum(1 for determination in all_general_determinations if determination[3] == 'True')
total_determinations = len(all_general_determinations)
accuracy = true_matches / total_determinations if total_determinations > 0 else 0
print(f"\nAccuracy: {accuracy:.2f} ({true_matches}/{total_determinations})")

# Save detailed results to `detailed_evaluation.csv`
output_detailed_csv_path = 'detailed_evaluation.csv'
with open(output_detailed_csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['dataname', 'vulnerability', 'function_name', 'match'])
    writer.writerows(all_comparison_results)

# Save general determinations to `general_determination.csv`
output_general_csv_path = 'general_determination.csv'
with open(output_general_csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['dataname', 'vulnerability', 'function_name', 'match', 'true_answer_line'])
    writer.writerows(all_general_determinations)

# Output accuracy summary
with open(output_general_csv_path, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([])
    writer.writerow(['Accuracy', f"{accuracy:.2f}", f"({true_matches}/{total_determinations})"])