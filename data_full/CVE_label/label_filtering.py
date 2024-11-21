import os
import json

# Define the input and output file paths
input_dir = 'data_full/CVE_clean'
output_file = 'data_full/CVE_label/filtered_labels.json'
label_file = 'data_full/CVE_label/CVE2description.json'

# Load the descriptions from CVE2description.json
with open(label_file, 'r') as label_data:
    cve_descriptions = json.load(label_data)

# Dictionary to store CVE labels and their matched descriptions
cve_labels = {}

# Loop through each file in the input directory
for filename in os.listdir(input_dir):
    # Only process .sol files
    if filename.endswith('.sol'):
        # Extract CVE label from the filename (assuming format "CVE-YYYY-NNNNN.sol")
        cve_label = 'CVE-'+filename.replace('.sol', '')

        # Find the corresponding description in the loaded data
        description = cve_descriptions.get(cve_label, "Description not found")  # Default if not found

        # Add the label and description to the dictionary
        cve_labels[cve_label] = description

# Save the dictionary to a JSON file
with open(output_file, 'w') as file:
    json.dump(cve_labels, file, indent=4)

print("All CVE labels and descriptions have been saved to", output_file)
