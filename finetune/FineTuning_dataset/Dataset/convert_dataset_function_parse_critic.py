import json
import os
from datasets import Dataset, load_dataset
import pandas as pd
from collections import defaultdict
import random
# Paths
code_dir = "finetune/FineTuning_dataset/Dataset/code_folder"
vulnerability_file = "finetune/FineTuning_dataset/Dataset/combined_single_sheet.csv"
output_file = "finetune/FineTuning_dataset/Dataset/fine_tuning_correctness_data.jsonl"





# Load vulnerabilities and their correctness
vulnerabilities = pd.read_csv(vulnerability_file)


# Function to load the content of each Solidity file
def load_code_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Fallback to ISO-8859-1 encoding
        with open(filepath, 'r', encoding='ISO-8859-1') as file:
            return file.read()

# Aggregate vulnerabilities by file and contract
vulnerability_data = defaultdict(list)
vulnerability_data_answer = defaultdict(list)
unique_vul = set()
for _, row in vulnerabilities.iterrows():
    if (row['ground truth'] == '0' )| (row['ground truth'] == '1'):
        cve_id = row['file']
        function_name = row["contract"]
        vulnerability_type = row['vul_type']
        correctness = int(row['ground truth'])  # Assuming 0 or 1 in the "ground truth" column
        vulnerability_data[cve_id].append({
            "function_name": function_name,
            "vulnerability": vulnerability_type,
        })
        vulnerability_data_answer[cve_id].append({
            "function_name": function_name,
            "vulnerability": vulnerability_type,
            "correctness":correctness
        })
        unique_vul.add(vulnerability_type)




# Generate and save JSONL data
with open(output_file, 'w') as out_file:
    for cve_id, vul_list in vulnerability_data.items():
        file_path = os.path.join(code_dir, f"{cve_id}.sol")
        vul_list_answer = vulnerability_data_answer[cve_id]

        for i in range(len(vul_list)):
            if vul_list_answer[i]['correctness'] == '0':
                vul_list_answer[i]['vulnerability'] = random.choice(list(unique_vul))
                vul_list[i]['vulnerability'] = vul_list_answer[i]['vulnerability']


        # Check if the file exists before reading it
        if os.path.isfile(file_path):
            code_content = load_code_content(file_path)

            # Build the JSON entry
            entry = {
                "messages": [
                    {"role": "system", "content": """Requirement: Below vulnerabilities for the code are likely to contain mistakes. As a harsh vulnerability critic, your duty is to scrutinize the function and evaluate the correctness, 0 for false and 1 for true. 
Output Formatting requirement:
{
    "output_list": [
        {
            "function_name": "<function_name_1>",
            "vulnerability": "<short_vulnera_desc_1>",
            "correctness": <0~1>,
        },
        ...
    ]
}"""},
                    {"role": "user", "content": f"Code: {code_content}\n\nVulnerabilities:\n{json.dumps(vul_list, indent=4)}"},
                    {"role": "assistant", "content": json.dumps({"output_list": vul_list_answer}, indent=4)}
                ]
            }

            # Write the entry to the JSONL file
            out_file.write(json.dumps(entry) + "\n")

# Load the generated JSONL dataset
dataset = load_dataset("json", data_files=output_file, split="train")

# Define the transformation function
def create_conversation(sample):
    return {
        "messages": sample["messages"]
    }

# Apply the transformation
dataset = dataset.map(create_conversation)

# Split dataset into training and test sets
dataset = dataset.train_test_split(test_size=0.2)

# Save the splits to disk
dataset["train"].to_json("finetune/FineTuning_dataset/Dataset/train_critic_dataset.json", orient="records")
dataset["test"].to_json("finetune/FineTuning_dataset/Dataset/test_critic_dataset.json", orient="records")

print(f"Training and testing datasets saved successfully.")
