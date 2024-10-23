import json
import os
import numpy as np
import matplotlib.pyplot as plt

# Function to read and count vulnerability types in CVElabel3_full.json
def count_vulnerability_types(json_file_path):
    with open(json_file_path, 'r') as file:
        data = json.load(file)
    
    vuln_type_count = {}
    
    for cve_id, details in data.items():
        vuln_type = details["vulnerability_type"]
        if vuln_type in vuln_type_count:
            vuln_type_count[vuln_type] += 1
        else:
            vuln_type_count[vuln_type] = 1
            
    return vuln_type_count

# Function to calculate code line stats from files in CVE_clean directory
def calculate_code_stats(directory_path):
    line_counts = []
    
    for filename in os.listdir(directory_path):
        if filename.endswith(".sol") or filename.endswith(".py") or filename.endswith(".c"):  # Add any relevant extensions
            file_path = os.path.join(directory_path, filename)
            with open(file_path, 'r') as file:
                line_count = len(file.readlines())
                line_counts.append(line_count)
    
    # Calculate statistics
    mean_lines = np.mean(line_counts)
    median_lines = np.median(line_counts)
    quartiles = np.percentile(line_counts, [25, 50, 75])
    
    return line_counts, mean_lines, median_lines, quartiles

# Function to plot the distribution of vulnerability types
def plot_vulnerability_type_distribution(vuln_type_count):
    vuln_types = list(vuln_type_count.keys())
    counts = list(vuln_type_count.values())

    plt.figure(figsize=(10, 6))
    plt.bar(vuln_types, counts, color='skyblue')
    plt.xlabel('Vulnerability Types')
    plt.ylabel('Count')
    plt.title('Distribution of Vulnerability Types')
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
    plt.savefig("dist_of_data")

# Function to plot a histogram of code line counts
def plot_code_line_distribution(line_counts):
    plt.figure(figsize=(10, 6))
    plt.hist(line_counts, bins=20, color='lightcoral', edgecolor='black')
    plt.xlabel('Number of Lines')
    plt.ylabel('Frequency')
    plt.title('Distribution of Code Line Counts')
    plt.tight_layout()
    plt.show()
    plt.savefig("num_of_code_line")

# Example paths
json_file_path = 'data_full/CVE_label/CVElabel3_full.json'  # Path to CVElabel3_full.json
directory_path = 'data_full/CVE_clean/'  # Path to directory containing code files

# Count vulnerability types
vuln_type_count = count_vulnerability_types(json_file_path)

# Calculate code statistics
line_counts, mean_lines, median_lines, quartiles = calculate_code_stats(directory_path)

# Output vulnerability type distribution
plot_vulnerability_type_distribution(vuln_type_count)

# Output code line statistics and plot
print(f"Mean lines of code: {mean_lines}")
print(f"Median lines of code: {median_lines}")
print(f"Quartiles: {quartiles}")
plot_code_line_distribution(line_counts)


