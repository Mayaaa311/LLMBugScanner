import json
import os
from datasets import Dataset, load_dataset

# Paths
code_dir = "/home/hice1/yyuan394/scratch/LLMBugScanner/data_full/CVE_clean"
label_file = "/home/hice1/yyuan394/scratch/LLMBugScanner/data_full/CVE_label/CVElabel3_full.json"
output_file = "/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/FineTuning_dataset/fine_tuning_data.jsonl"

# Load labels
with open(label_file, 'r') as f:
    labels = json.load(f)

# Function to load the content of each Solidity file
def load_code_content(filepath):
    with open(filepath, 'r') as file:
        return file.read()

# Generate and save JSONL data
with open(output_file, 'w') as out_file:
    for cve_id, details in labels.items():
        vulnerability_type = details["vulnerability_type"]
        function_name = details["vulnerable_function_name"]
        cve_id = cve_id[4:]  # Adjust CVE format as needed
        file_path = os.path.join(code_dir, f"{cve_id}.sol")

        # Check if the file exists before reading it
        if os.path.isfile(file_path):
            code_content = load_code_content(file_path)

            # Structure JSON entry
            entry = {
                "messages": [
                    {"role": "system", "content": "You are a smart contract auditor, identify the top 1 severe vulnerabilities in the provided smart contract and the function it is in, provide detailed reasoning and explaination, you do not need to generate solution"},
                    {"role": "user", "content": f"Analyze the following Solidity code:\n\n{code_content}"},
                    {"role": "assistant", "content": f"The code contains a vulnerability of type '{vulnerability_type}' in the function '{function_name}'."}
                ]
            }

            # Write to JSONL file
            out_file.write(json.dumps(entry) + "\n")

print(f"Dataset generated in {output_file}")

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
dataset["train"].to_json("/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/FineTuning_dataset/train_dataset.json", orient="records")
dataset["test"].to_json("/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/FineTuning_dataset/test_dataset.json", orient="records")

print(f"Training and testing datasets saved successfully.")
