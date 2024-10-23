import os
import csv
import json

# Path to the base folder and JSON file
base_folder = '/home/hice1/yyuan394/scratch/LLMBugScanner/result_test_parser/trail3/k5_n1_2024-10-18_04-49-35.log/'
json_file_path = '/home/hice1/yyuan394/scratch/LLMBugScanner/data_full/CVE_label/CVElabel3_full.json'

# Load JSON data
with open(json_file_path, 'r') as jsonfile:
    json_data = json.load(jsonfile)

# Function to compare vulnerabilities and functions
def compare_vulnerabilities(csv_data, json_data, dataname):
    results = []
    print("json data is : ",json_data)
    dataname = "CVE-"+dataname
    print(dataname,"-"*20)
    
    for csv_row in csv_data:
        vulnerability = csv_row['vulnerability']
        function_name = csv_row['function_name']
        
        # Check if dataname exists in JSON
        if dataname in json_data:
            json_vulnerability = json_data[dataname]["vulnerability_type"]
            json_function_name = json_data[dataname]["vulnerable_function_name"]
            
            # Compare vulnerability and function names
            print("-"*20)
            print("vulnerability: ",vulnerability)
            print("json_vulnerability: ",json_vulnerability)
            print("function_name: ",function_name)
            print("json_function_name: ",json_function_name)
            if vulnerability == json_vulnerability and function_name == json_function_name:
                result = (dataname, vulnerability, function_name, 'True')
            else:
                result = (dataname, vulnerability, function_name, 'False')
        else:
            result = (dataname, vulnerability, function_name, 'False')
        
        results.append(result)
    
    return results

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
    file_path = os.path.join(folder_path, 'final_output/m-a-p_OpenCodeInterpreter-DS-6.7B_summarized0.json')
    
    # Check if the file exists
    if os.path.exists(file_path):
        print(f"Processing file: {file_path}")
        
        # Extract data from the text-based file
        csv_data = extract_data_from_text_file(file_path)
        
        # Run the comparison
        comparison_results = compare_vulnerabilities(csv_data, json_data, dataname)
        return comparison_results
    else:
        print(f"File not found in {folder_path}")
        return []

# Function to process all folders in the base directory
def process_all_folders(base_folder, json_data):
    all_results = []
    
    # Iterate through all subdirectories in the base folder
    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        
        if os.path.isdir(folder_path):
            # Process the folder
            folder_results = process_folder(folder_path, json_data)
            all_results.extend(folder_results)
    
    return all_results

# Run the comparison for all folders
all_comparison_results = process_all_folders(base_folder, json_data)

# Output the results
print("Comparison Results:")
for result in all_comparison_results:
    print(result)

# Optional: Save the results to a CSV
output_csv_path = 'all_comparison_results.csv'
with open(output_csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['dataname', 'vulnerability', 'function_name', 'match'])
    writer.writerows(all_comparison_results)
