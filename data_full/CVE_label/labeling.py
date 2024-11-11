import json
import re

def read_json_file(file_path):
    data = {}
    with open(file_path, 'r') as file:
        try:
            # Load the entire JSON content at once
            data = json.load(file)
            
            # Iterate through the key-value pairs
            for cve_id, description in data.items():
                data[cve_id] = description
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    return data



def label_cve_ids(data):
    # Initialize lists for each label
    integer_overflow = []
    wrong_logic = []
    bad_randomness = []
    access_control = []
    typo_constructor = []
    token_devalue = []
    manual_labeling = []

    # Define the labels to search for
    labels = {
        "Integer Overflow": integer_overflow,
        "Wrong Logic": wrong_logic,
        "Bad Randomness": bad_randomness,
        "Access Control": access_control,
        "Typo Constructor": typo_constructor,
        "Token Devalue": token_devalue
    }

    # Iterate over each CVE and description
    for cve_id, description in data.items():
        found_label = False
        
        # Check for each label in the description
        for label, label_list in labels.items():
            if label.lower() in description.lower():
                label_list.append(cve_id)
                found_label = True
                break
        
        # If no label was found, add to manual labeling list
        if not found_label:
            manual_labeling.append(cve_id)

    # Return the lists
    return {
        "Integer Overflow": integer_overflow,
        "Wrong Logic": wrong_logic,
        "Bad Randomness": bad_randomness,
        "Access Control": access_control,
        "Typo Constructor": typo_constructor,
        "Token Devalue": token_devalue,
        "Manual Labeling": manual_labeling
    }

def cross_check_duplicates(labeled_cve_ids):
    # Create a dictionary to track the count of each CVE ID
    cve_count = {}

    # Iterate through each category and the list of CVE IDs
    for label, cve_list in labeled_cve_ids.items():
        for cve_id in cve_list:
            # If the CVE ID already exists, increment the count
            if cve_id in cve_count:
                cve_count[cve_id].append(label)
            else:
                # Otherwise, initialize the count with the current label
                cve_count[cve_id] = [label]

    # Find CVE IDs that appear in more than one category
    duplicates = {cve_id: labels for cve_id, labels in cve_count.items() if len(labels) > 1}

    return duplicates

def generate_labeled_json(labeled_cve_ids, output_file):
    # Create a dictionary to store the final labeled data
    labeled_data = {}

    # Iterate through each category and their corresponding CVE IDs
    for label, cve_list in labeled_cve_ids.items():
        for cve_id in cve_list:
            # If the CVE ID is already present, append the new label
            if cve_id in labeled_data:
                labeled_data[cve_id] += f", {label}"
            else:
                # Otherwise, add the CVE ID with the current label
                labeled_data[cve_id] = label

    # Write the labeled data to a JSON file
    with open(output_file, 'w') as json_file:
        json.dump(labeled_data, json_file, indent=4)

def extract_function_name(description):
    # Regular expressions to match different function name patterns
    # 1. Matches patterns like 'functionName(' or 'functionName ()'
    call_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*)\(\)'
    
    # 2. Matches patterns like 'the functionName function'
    function_phrase_pattern = r'\b[Tt]he\s+([a-zA-Z_][a-zA-Z0-9_]*)\s+function\b'

    # Try to match function call patterns like 'functionName('
    matches_call = re.findall(call_pattern, description)
    
    # Try to match phrases like 'the functionName function'
    matches_phrase = re.findall(function_phrase_pattern, description)

    # Clean up the function names by removing parentheses or unnecessary spaces
    functions_call = [match.strip().replace('(', '') for match in matches_call]
    functions_phrase = [match.strip() for match in matches_phrase]

    # Return the first found function name, prioritizing function call patterns
    if functions_call:
        return functions_call[0]
    elif functions_phrase:
        return functions_phrase[0]
    else:
        return "Not Provided"
    
def add_vulnerable_function_column(label_file, description_file, output_file):
    # Load the existing label.json file
    with open(label_file, 'r') as file:
        label_data = json.load(file)
    
    # Load the description.json file
    with open(description_file, 'r') as file:
        description_data = json.load(file)
    
    # Create a new structured format
    updated_data = {}

    # Iterate through each CVE ID and label
    for cve_id, vulnerability_type in label_data.items():
        # Look up the corresponding description for the CVE ID
        description = description_data.get(cve_id, "")
        
        # Extract the function name from the description
        vulnerable_function_name = extract_function_name(description)
        
        # Store the structured data
        updated_data[cve_id] = {
            "vulnerability_type": vulnerability_type,
            "vulnerable_function_name": vulnerable_function_name
        }

    # Save the updated data to a new JSON file
    with open(output_file, 'w') as outfile:
        json.dump(updated_data, outfile, indent=4)

# file_path = 'CVE2description.json'
# data = read_json_file(file_path)
# labeled_cve_ids = label_cve_ids(data)

# # Display the results
# for label, cve_list in labeled_cve_ids.items():
#     print(f"{label}: {cve_list}")

# duplicates = cross_check_duplicates(labeled_cve_ids)

# # Display the results
# if duplicates:
#     print("CVE IDs found in multiple categories:")
#     for cve_id, categories in duplicates.items():
#         print(f"{cve_id} appears in {categories}")
# else:
#     print("No CVE IDs found in multiple categories.")

# output_file = 'CVE2label2.json'
# generate_labeled_json(labeled_cve_ids, output_file)


description_file = 'CVE2description.json'
label_file = 'CVE2label2.json'
output_file = 'CVElabel3.json'
add_vulnerable_function_column(label_file, description_file, output_file)

