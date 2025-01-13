import json
import os

# Load the JSON files
json_file = "finetune/FineTuning_dataset/gptlens_dataset/auditor_summary_with_code.json"
reference_file = "data_full/CVE_label/CVE2label_with_description_final.json"

# Load main data
with open(json_file, "r") as f:
    data = json.load(f)

# Load reference labels
with open(reference_file, "r") as f:
    reference_data = json.load(f)

# Ensure the "label" field exists in each entry
for entry in data:
    if "label" not in entry:
        entry["label"] = None  # Add the "label" field if it doesn't exist

# Iterate through each entry and label
for index, entry in enumerate(data):
    # Skip entries that are already labeled
    if entry["label"] is not None:
        continue

    # Extract dataname and build CVE reference key
    dataname = entry["Dataname"]
    cve_key = f"CVE-{dataname}"

    # Get the reference label if it exists
    reference_label = reference_data.get(cve_key, None)

    # Display the prompt
    print(f"\nEntry {index + 1}/{len(data)}")
    print("Prompt:")
    print(entry["Prompt"])

    # Display the reference label if available
    if reference_label:
        print("\nReference Label:")
        print(f"Vulnerability Type: {reference_label['vulnerability_type']}")
        print(f"Vulnerable Function Name: {reference_label['vulnerable_function_name']}")
        print(f"Description: {reference_label['description']}")
    else:
        print("\nReference Label: Not Available")

    # Get the label from the user
    label = input("Enter the label for this entry: ").strip()

    # Save the label
    entry["label"] = label

    # Save the updated JSON file after each labeling
    with open(json_file, "w") as f:
        json.dump(data, f, indent=4)
    print("Label saved!\n")

print("\nLabeling completed.")
