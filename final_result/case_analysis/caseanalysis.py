# import pandas as pd

# # Load the two CSV files
# file1 = "result/case_analysis/general_determination_codeinterpreter.csv"  # Replace with your first CSV file name
# file2 = "result/case_analysis/general_determination_nxcode.csv"  # Replace with your second CSV file name

# # Read the CSV files into DataFrames
# df1 = pd.read_csv(file1)
# df2 = pd.read_csv(file2)

# # Merge the two DataFrames on the common column(s)
# # Assuming the column 'dataname' is the common column
# merged_df = pd.merge(df1, df2, on="dataname", suffixes=('_llm1', '_llm2'))

# # Categorize the data
# def categorize(row):
#     if row['match_llm1'] == True and row['match_llm2'] == True:
#         return 'easy'
#     elif row['match_llm1'] != row['match_llm2']:
#         return 'medium'
#     else:
#         return 'hard'

# merged_df['category'] = merged_df.apply(categorize, axis=1)

# # Create a summary table
# category_counts = merged_df['category'].value_counts()

# # Save the categorized data into a new CSV file
# merged_df.to_csv("result/case_analysis/categorized_data.csv", index=False)

# # Print the summary table
# print("Summary Table:")
# print(category_counts)

# import pandas as pd
# import matplotlib.pyplot as plt

# # Load the CSV file into a DataFrame
# file = "result/case_analysis/categorized_data.csv"  # Replace with your file name
# df = pd.read_csv(file)

# # Ensure all vulnerability types are treated as strings and remove NaN values
# df['vulnerability_llm1'] = df['vulnerability_llm1'].astype(str)
# df = df[df['vulnerability_llm1'] != 'nan']

# # Get all unique vulnerability types from the entire dataset
# all_vulnerabilities = df['vulnerability_llm1'].unique()

# # Create a list of unique categories
# categories = df['category'].unique()

# # Loop through each category and generate a graph
# for category in categories:
#     # Filter the data for the current category
#     category_data = df[df['category'] == category]

#     # Count the occurrences of each vulnerability type, reindex with all vulnerabilities
#     vulnerability_counts = category_data['vulnerability_llm1'].value_counts()
#     vulnerability_counts = vulnerability_counts.reindex(all_vulnerabilities, fill_value=0)

#     # Plot the data
#     plt.figure(figsize=(10, 6))
#     plt.bar(vulnerability_counts.index, vulnerability_counts.values)
#     plt.xlabel('Vulnerability Type')
#     plt.ylabel('Count')
#     plt.title(f'Data Count per Vulnerability - {category.capitalize()} Cases')
#     plt.xticks(rotation=45, ha='right')
#     plt.tight_layout()

#     # Save the plot to a file
#     plt.savefig(f'result/case_analysis/{category}_vulnerability_analysis.png')

#     # Show the plot (optional)
#     plt.show()

# print("Graphs generated and saved for each category!")






# 
# import pandas as pd
# import matplotlib.pyplot as plt

# # Load the CSV file into a DataFrame
# file = "result/case_analysis/categorized_data.csv"  # Replace with your file name
# df = pd.read_csv(file)

# # Ensure all vulnerability types are treated as strings and remove NaN values
# df['vulnerability_llm1'] = df['vulnerability_llm1'].astype(str)
# df = df[df['vulnerability_llm1'] != 'nan']

# # Get all unique vulnerability types
# all_vulnerabilities = df['vulnerability_llm1'].unique()

# # Count the occurrences of each category (easy, medium, hard) for each vulnerability
# category_counts = df.groupby(['vulnerability_llm1', 'category']).size().unstack(fill_value=0)

# # Reindex to ensure all vulnerabilities are included
# category_counts = category_counts.reindex(all_vulnerabilities, fill_value=0)

# # Plot the stacked bar chart
# plt.figure(figsize=(12, 8))

# # Create a stacked bar for each category
# bottom = None
# for category in ['easy', 'medium', 'hard']:
#     plt.bar(
#         category_counts.index, 
#         category_counts[category], 
#         bottom=bottom, 
#         label=category.capitalize()
#     )
#     # Update the bottom for stacking
#     if bottom is None:
#         bottom = category_counts[category]
#     else:
#         bottom += category_counts[category]

# # Set labels and title
# plt.xlabel('Vulnerability Type')
# plt.ylabel('Total Count')
# plt.title('Proportion of Easy, Medium, and Hard Cases for Each Vulnerability')
# plt.xticks(rotation=45, ha='right')
# plt.legend(title='Category')
# plt.tight_layout()

# # Save the plot
# plt.savefig("result/case_analysis/vulnerability_stacked_bar.png")

# # Show the plot
# plt.show()

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Load the categorized data
file = "result/case_analysis/categorized_data.csv"  # Replace with your file path
df = pd.read_csv(file)

# Ensure 'vulnerability_llm1' and 'dataname' are strings
df['vulnerability_llm1'] = df['vulnerability_llm1'].astype(str)
df['dataname'] = df['dataname'].astype(str)

# Remove NaN vulnerabilities
df = df[df['vulnerability_llm1'] != 'nan']

# Define the directory containing the code files
code_dir = "data_full/CVE_clean"  # Replace with your directory path

# Initialize a dictionary to store line counts for each category
line_counts = {'easy': [], 'medium': [], 'hard': []}

# Loop through each row in the DataFrame
for _, row in df.iterrows():
    category = row['category']
    dataname = row['dataname']
    
    # Construct the filename from the dataname (e.g., CVE-2018-13722 -> 2018-13722.sol)
    file_name = f"{dataname.split('-')[1]}-{dataname.split('-')[2]}.sol"
    file_path = os.path.join(code_dir, file_name)
    
    # Check if the file exists
    if os.path.exists(file_path):
        # Count the number of lines in the file
        with open(file_path, 'r') as file:
            num_lines = len(file.readlines())
        # Append the line count to the corresponding category
        line_counts[category].append(num_lines)

# Generate statistics for each category
stats = {}
for category, counts in line_counts.items():
    stats[category] = {
        'average': np.mean(counts) if counts else 0,
        'median': np.median(counts) if counts else 0,
        'max': max(counts) if counts else 0,
        'min': min(counts) if counts else 0
    }

# Create a DataFrame for the statistics
stats_df = pd.DataFrame(stats).T
stats_df = stats_df[['average', 'median', 'max', 'min']]

# Save the statistics to a CSV file
stats_df.to_csv("result/case_analysis/code_line_statistics.csv")
print("Code line statistics saved to 'result/case_analysis/code_line_statistics.csv'")

# Plot the distributions for each category in separate subplots
fig, axes = plt.subplots(3, 1, figsize=(10, 18), sharex=True)

categories = ['easy', 'medium', 'hard']
for i, category in enumerate(categories):
    counts = line_counts[category]
    axes[i].hist(counts, bins=20, alpha=0.7, color='blue')
    axes[i].set_title(f"Distribution of Code Lines - {category.capitalize()} Cases")
    axes[i].set_ylabel("Frequency")
    axes[i].grid(axis='y', linestyle='--', alpha=0.7)

# Set shared X-axis label
axes[-1].set_xlabel("Number of Lines")

# Adjust layout
plt.tight_layout()

# Save the plot
plt.savefig("result/case_analysis/code_line_distribution_subplots.png")
print("Code line distribution subplot saved to 'result/case_analysis/code_line_distribution_subplots.png'")

# Show the plot (optional)
plt.show()
