import json

# Load CVE labels
with open("data_full/CVE_label/CVElabel3_full.json", "r") as f:
    cve_labels = json.load(f)

# Load CVE descriptions
with open("data_full/CVE_label/CVE2description_processed.json", "r") as f:
    cve_descriptions = json.load(f)

# Create a new dictionary to store only entries with descriptions
filtered_cve_labels = {}

# Add description to each entry in CVE labels if it exists in descriptions
for cve_id, details in cve_labels.items():
    # Check if the cve_id exists in cve_descriptions and details is a dictionary
    if cve_id in cve_descriptions and isinstance(details, dict):
        details["description"] = cve_descriptions[cve_id]
        filtered_cve_labels[cve_id] = details
    else:
        print(f"Skipping {cve_id} because it doesn't exist in descriptions or isn't a dictionary.")

# Save the filtered data with descriptions
with open("data_full/CVE_label/CVE2label_with_description.json", "w") as f:
    json.dump(filtered_cve_labels, f, indent=4)

print("Descriptions added to matching CVE IDs and saved to CVE2label_with_description.json")
