import os
import json

# Define paths
result_path = "result/Deepseek_k5_MessiQ_GPTLens_Method2"
clean_data_path = "data_full/0.8splitCVE_clean"
code_path = "data_full/0.8splitCVE_clean"  # Path where code files are stored
label_file_path = "finetune/FineTuning_dataset/gptlens_dataset/auditor_summary_with_code.json"

# Get clean dataset identifiers
clean_data = {os.path.splitext(file)[0] for file in os.listdir(clean_data_path) if file.endswith(".sol")}

# Load label data
with open(label_file_path, "r") as label_file:
    label_data = json.load(label_file)

# Prepare results
data_to_export = []
counter = 0

# Traverse result folder
for folder in os.listdir(result_path):
    folder_path = os.path.join(result_path, folder)
    if os.path.isdir(folder_path) and folder not in clean_data:
        auditor_summary_path = os.path.join(folder_path, "auditor_summary")
        if os.path.exists(auditor_summary_path):
            merged_output_list = []
            # Traverse auditor_summary folder
            for file in os.listdir(auditor_summary_path):
                if file.endswith(".json"):
                    json_file_path = os.path.join(auditor_summary_path, file)
                    with open(json_file_path, "r") as f:
                        data = json.load(f)
                        merged_output_list.extend(data.get("output_list", []))
            if merged_output_list:
                # Load the corresponding code file
                code_file_path = os.path.join('data_full/CVE_clean', f"{folder}.sol")
                if os.path.exists(code_file_path):
                    with open(code_file_path, "r") as code_file:
                        code_content = code_file.read()

                    # Find the matching label data
                    label_entry = next((item for item in label_data if item["Dataname"] == folder), None)
                    if label_entry:
                        label_content = label_entry["label"]

                        # Construct the transformed format
                        transformed_entry = {
                            "messages": [
                                {"role": "system", "content": (
                                    "Requirement: Below vulnerabilities and reasoning for the code are likely to contain mistakes. "
                                    "As a harsh vulnerability critic, your duty is to scrutinize the function and evaluate the correctness, "
                                    "severity, and profitability of the given vulnerabilities and associated reasoning with corresponding scores "
                                    "ranging from 0 (lowest) to 9 (highest). You also need to provide criticism, which must include explanations "
                                    "for your scoring. Make your criticism detailed and concise (within 1-3 sentences), don't assign the same score "
                                    "for different vulnerabilities. In your output, make sure the auditor index is 1."
                                )},
                                {"role": "user", "content": (
                                    f"Vulnerability: {json.dumps(merged_output_list, indent=4)}\n"
                                    f"Code: {code_content}"
                                )},
                                {"role": "assistant", "content": label_content}
                            ]
                        }

                        # Append the transformed data
                        data_to_export.append(transformed_entry)

# Save to JSON file
output_json_path = "finetune/FineTuning_dataset/critic_training_dataset.json"
with open(output_json_path, "w") as json_file:
    json.dump(data_to_export, json_file, indent=4)

print(f"Data saved to {output_json_path}")
