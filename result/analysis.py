import os
import pandas as pd

# Path to the baseline folder
base_path = "result/finetuned_both"

# Initialize a list to store the extracted data
data = []

# Loop through all subfolders in the base_path
for subfolder in os.listdir(base_path):
    subfolder_path = os.path.join(base_path, subfolder)
    if os.path.isdir(subfolder_path):  # Only process directories
        file_path = os.path.join(subfolder_path, "general_determination.csv")
        print("reading: ",file_path)
        if os.path.exists(file_path):
            try:
                # Read the CSV file
                with open(file_path, "r") as f:
                    lines = f.readlines()
                
                # Extract the last two lines
                top_k_hit_rate = lines[-2].strip() if len(lines) >= 2 else "N/A"
                top_1_hit_rate = lines[-1].strip() if len(lines) >= 1 else "N/A"
                
                # Add to the data list
                data.append({
                    "Subfolder": subfolder,
                    "Metric": "Top k hit rate",
                    "Value": top_k_hit_rate
                })
                data.append({
                    "Subfolder": subfolder,
                    "Metric": "Top 1 hit rate",
                    "Value": top_1_hit_rate
                })
            except Exception as e:
                print(f"Error reading file {file_path}: {e}")

# Convert the data to a DataFrame
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file in the same directory
output_file = os.path.join(base_path, "summary_metrics.csv")
df.to_csv(output_file, index=False)

print(f"Summary metrics saved to {output_file}")
