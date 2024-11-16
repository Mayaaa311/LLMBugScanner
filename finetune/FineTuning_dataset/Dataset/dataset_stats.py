import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the CSV file
file_path = 'finetune/FineTuning_dataset/Dataset/combined_single_sheet.csv'
df = pd.read_csv(file_path)
save_dir = 'finetune/FineTuning_dataset/Dataset'
os.makedirs(save_dir, exist_ok=True)

# Ensure 'ground truth' is numeric
df['ground truth'] = pd.to_numeric(df['ground truth'], errors='coerce').fillna(0).astype(int)

# Aggregate 'ground truth' to count the total number of vulnerabilities per file
# Sum 'ground truth' values for each file to count the vulnerabilities
df['vulnerabilities'] = df.groupby('file')['ground truth'].transform('sum')

# Filter the dataframe to unique files with their vulnerability count
aggregated_df = df.groupby('file')['vulnerabilities'].max().reset_index()

# Calculate the total number of unique files
total_files = aggregated_df['file'].nunique()

# Distribution of vulnerability types
vul_type_distribution = df['vul_type'].value_counts()

# Distribution of the number of vulnerabilities per file
vul_per_file_distribution = aggregated_df['vulnerabilities'].value_counts().sort_index()

# Print the results
print("Total number of unique files:", total_files)
print("\nDistribution of vulnerability types:")
print(vul_type_distribution)
print("\nDistribution of the number of vulnerabilities per file:")
print(vul_per_file_distribution)

# Plotting the distribution of vulnerability types
if not vul_type_distribution.empty:
    plt.figure(figsize=(10, 6))
    vul_type_distribution.plot(kind='bar', color='skyblue')
    plt.title("Distribution of Vulnerability Types")
    plt.xlabel("Vulnerability Type")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'vulnerability_types_distribution.png'))
    plt.close()
    print("Vulnerability types distribution plot saved.")
else:
    print("No data available for vulnerability types distribution.")

# Plotting the distribution of the number of vulnerabilities per file
if not vul_per_file_distribution.empty:
    plt.figure(figsize=(10, 6))
    vul_per_file_distribution.plot(kind='bar', color='salmon')
    plt.title("Distribution of Number of Vulnerabilities per File")
    plt.xlabel("Number of Vulnerabilities")
    plt.ylabel("Number of Files")
    plt.tight_layout()
    plt.savefig(os.path.join(save_dir, 'vulnerabilities_per_file_distribution.png'))
    plt.close()
    print("Number of vulnerabilities per file distribution plot saved.")
else:
    print("No data available for the number of vulnerabilities per file distribution.")
