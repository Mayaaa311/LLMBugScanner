
import os
import csv
import json
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
model = SentenceTransformer('all-MiniLM-L6-v2')

# -----------------!!! Change this to the result folder you want to evaluate!!!-----------------
# result_folder = 'result/result_nxcodes_k3_a5_beforeft'
# result_folder = 'result/result_nxcodes_k5_a5_beforeft'
# result_folder='result/result_nxcodes_k5_a5_beforeft_t0.5'
# result_folder = 'result/result_nxcodes_k5_a5_beforeft'
result_folder = 'result/finetuned_single/opencodeinterpreter_ft'
test_only = True
# ------------------Folder definition-------------------------------------------------------
base_folder = result_folder
os.makedirs(result_folder, exist_ok=True)

# Paths for result files
output_detailed_csv_path = os.path.join(result_folder, 'detailed_evaluation_auditor_w_similarity.csv')
output_general_csv_path = os.path.join(result_folder, 'general_determination_auditor_w_similarity.csv')

json_file_path = 'data_full/CVE_label/CVE2label_with_description_final.json'
# -------------------------------------------Result Reformatting-------------------------------------------------

def reformat_file_content(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Replace escaped newlines with actual newlines
    content = content.replace('\\n', '\n')
    
    # Remove all backslashesq  1                             
    content = content.replace('\\', '')

    while content.startswith('\n'):
        content = content[1:] 
    while content.endswith('\n'):
        content = content[:-1]
        
    # Remove leading and trailing quotes if present
    while content.startswith('"'):
        content = content[1:]
    while content.endswith('"'):
        content = content[:-1]

    if(file_path.endswith('summarized0.csv')):
        while not content.startswith('dataname'):
            if (content == ''):
                break
            content = content[1:] 

    # Write the reformatted content back to the file
    with open(file_path, 'w') as file:
        file.write(content)


def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"reformatting file: {file_path}")
            reformat_file_content(file_path)

process_directory(result_folder)
#----------------------------------------OPTIONAL: eval on only test set---------------------------------
# Define the directory containing .sol files
directory = "data_full/0.8splitCVE_clean"

# Initialize an empty list to store the formatted names
formatted_names = []

# Iterate through all files in the directory
for filename in os.listdir(directory):
    # Check if the file has a .sol extension
    if filename.endswith(".sol"):
        # Remove the .sol extension and add "CVE-" prefix
        formatted_name = "CVE-" + filename.replace(".sol", "")
        # Add the formatted name to the list
        formatted_names.append(formatted_name)
print(formatted_names)
# -------------------------------------------GENERATE EVALUATION-------------------------------------------------
# Load JSON data
with open(json_file_path, 'r') as jsonfile:
    json_data = json.load(jsonfile)
# Function to compare vulnerabilities and functions
def compare_vulnerabilities(csv_data, json_data, dataname):
    results = []
    dataname = "CVE-" + dataname
    true_answer_line = "N/A"  # Initialize as N/A, to be updated if a true match is found
    
    # Deduplicate the CSV data based on 'vulnerability', 'function_name', and 'auditor_idx'
    unique_csv_data = { (row['vulnerability'], row['function_name'], row['description'], row['auditor_idx']): row for row in csv_data }.values()
    
    # Check if dataname exists in JSON
    if dataname not in json_data:
        print(f"Warning: {dataname} not found in JSON data")
        general_determination = (dataname, "N/A", "N/A", 'False', true_answer_line, "N/A", -1)
        return results, general_determination

    for i, csv_row in enumerate(unique_csv_data, start=1):
        vulnerability = csv_row['vulnerability']
        function_name = csv_row['function_name']
        description = csv_row['description']
        
        # Get vulnerability and function name from JSON
        json_vulnerability = json_data[dataname]["vulnerability_type"]
        json_function_name = json_data[dataname]["vulnerable_function_name"]
        json_description = json_data[dataname]["description"]

        similarity_score = -1
        # Compare function name only
        match = (function_name == json_function_name) & (vulnerability == json_vulnerability)
        if match == True:
            desc_embedding = model.encode(description)
            json_desc_embedding = model.encode(json_description)
            # Compute cosine similarity
            similarity_score = cosine_similarity([desc_embedding], [json_desc_embedding])[0][0]


        result = (dataname, vulnerability, function_name, auditor_idx, 'True' if match else 'False', similarity_score)
        
        if match and true_answer_line == "N/A":
            true_answer_line = i  # Update to the first true match line number

        results.append(result)
    
    # Remove duplicates from the current results list after processing
    results = list(set(results))
    
    # Check if there's any `True` match in the results for this file
    any_true_match = any(result[4] == 'True' for result in results)
    max_similarity = max(result[5] for result in results)

    
    # Create a general determination result based on whether there's a true match, and add the line number of the first true answer
    general_determination = (dataname, json_vulnerability, json_function_name, 'True' if any_true_match else 'False', max_similarity, true_answer_line, auditor_idx)
    
    return results, general_determination
# Function to extract data from the CSV-formatted text
def extract_data_from_text_file(file_path):
    csv_data = []
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
            
            if "output_list" in data:
                for entry in data["output_list"]:
                    csv_data.append({
                        'dataname': os.path.splitext(os.path.basename(file_path))[0],  # Extract dataname from filename
                        'vulnerability': entry['vulnerability'],
                        'function_name': entry['function_name'],
                        'description: ': entry['reason']
                    })
    except Exception as e:
        print(f"Error reading {file_path}: {e}. Skipping this file.")
    
    return csv_data


# Function to process a folder
def process_folder(folder_path, json_data):
    # Extract the dataname from the folder name
    dataname = os.path.basename(folder_path)
    
    # Path to the file inside the folder
    file_path = os.path.join(folder_path, 'auditor_summary/NTQAI_Nxcode-CQ-7B-orpo_summarized_0.json')
    if os.path.exists(folder_path+'/auditor_summary/'):
        for file in os.listdir(folder_path+'/auditor_summary/'):
            if(file.endswith('summarized_0.json')):
                file_path = os.path.join(folder_path+'/auditor_summary',file)
        
        
    # Check if the file exists
    if os.path.exists(file_path):
        print(f"Processing output: {file_path}")
        
        # Extract data from the text-based file
        csv_data = extract_data_from_text_file(file_path)
        
        if not csv_data:  # Skip processing if csv_data is empty or incorrectly formatted
            print(f"Skipping {file_path} due to empty or invalid format.")
            return [], None

        # Run the comparison and deduplicate the results within this file
        comparison_results, general_determination = compare_vulnerabilities(csv_data, json_data, dataname)
        return comparison_results, general_determination
    else:
        print(f"File {file_path}not found in {folder_path}")
        return [], None

# Function to process all folders in the base directory
def process_all_folders(base_folder, json_data):
    all_results = []
    general_determinations = []
    
    # Iterate through all subdirectories in the base folder
    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        
        if os.path.isdir(folder_path):
            print("folder path: ",folder_path)
            # Process the folder and deduplicate each file's results
            folder_results, general_determination = process_folder(folder_path, json_data)
            all_results.extend(folder_results)  # Aggregate deduplicated results for detailed output
            
            if general_determination:
                general_determinations.append(general_determination)  # Collect aggregated results for general output
    
    return all_results, general_determinations

# Run the comparison for all folders
all_comparison_results, all_general_determinations = process_all_folders(base_folder, json_data)
if test_only:
    all_comparison_results = [result for result in all_comparison_results if result[0] in formatted_names]
    all_general_determinations = [determination for determination in all_general_determinations if determination[0] in formatted_names]

# Calculate accuracy based on general determinations
true_matches = sum(1 for determination in all_general_determinations if determination[3] == 'True')
total_determinations = len(all_general_determinations)
accuracy = true_matches / total_determinations if total_determinations > 0 else 0
print(f"Top k hit rate: {accuracy:.2f} ({true_matches}/{total_determinations})")

with open(output_detailed_csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['dataname', 'vulnerability', 'function_name', 'auditor_idx', 'match', 'description_similarity'])
    writer.writerows(all_comparison_results)

# Save general determinations to `general_determination.csv`
with open(output_general_csv_path, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['dataname', 'vulnerability', 'function_name', 'match', 'description_similarity', 'true_answer_line', 'auditor_idx'])
    writer.writerows(all_general_determinations)



# Initialize counters
total_hits = 0
rank_1_hits = 0
file_path = base_folder+'/general_determination.csv'

# Open and read the CSV file
with open(file_path, 'r') as file:
    reader = csv.DictReader(file)
    
    # Iterate through each row
    for row in reader:
        # Check if `true_answer_line` is a "hit" (not 'N/A')
        if row['true_answer_line'] != 'N/A':
            total_hits += 1
            # Check if the hit is in rank 1
            if row['true_answer_line'] == '1':
                rank_1_hits += 1

# Calculate and print the hit rate
print("Top 1 hit rate:",rank_1_hits / total_determinations if total_determinations else 0,  f'({rank_1_hits}/{total_determinations})')



# Output accuracy summary
with open(output_general_csv_path, mode='a', newline='') as file:
    writer = csv.writer(file)
    writer.writerow([])
    writer.writerow(['Top k hit rate:', f"{accuracy:.2f}", f"({true_matches}/{total_determinations})"])
    writer.writerow(['Top 1 hit rate:', f"{accuracy:.2f}", rank_1_hits / total_determinations if total_determinations else 0,  f'({rank_1_hits}/{total_determinations})'])


