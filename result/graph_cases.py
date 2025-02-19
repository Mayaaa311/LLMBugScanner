import pandas as pd
import matplotlib.pyplot as plt

# Load the two CSV files
path_csv1 = 'result/Deepseek_k5_MessiQ_GPTLens_Method2/general_determination.csv'
path_csv2 = 'result/deepseek_newft_nxcode_critic_k5_try2/general_determination.csv'

data1 = pd.read_csv(path_csv1)
data2 = pd.read_csv(path_csv2)

# Compare the "match" column in both CSVs
comparison = data1.merge(data2, on='dataname', suffixes=('_csv1', '_csv2'))

# Save the table of mismatched cases
mismatch_cases = comparison[(comparison['match_csv1'] == False) & (comparison['match_csv2'] == True)]
mismatch_table_path = 'result/Deepseek/mismatch_cases.csv'
mismatch_cases.to_csv(mismatch_table_path, index=False)
print(f"Mismatch cases saved to {mismatch_table_path}")

# Perform statistics on vulnerabilities and functions
vulnerability_stats = mismatch_cases['vulnerability_csv2'].value_counts()
function_stats = mismatch_cases['function_name_csv2'].value_counts()

# Print summary statistics
print("\nVulnerability Statistics:")
print(vulnerability_stats)

print("\nFunction Statistics:")
print(function_stats)

# Create visualizations
# Plot vulnerabilities
plt.figure(figsize=(10, 6))
ax = vulnerability_stats.plot(kind='bar')
plt.title('Correct Identifications by Vulnerability Type')
plt.xlabel('Vulnerability Type')
plt.ylabel('Frequency')
plt.xticks(rotation=45)

# Add labels to bars
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 5), textcoords='offset points')

plt.tight_layout()
plt.savefig('result/Deepseek/vulnerability_stats.png')
print("Vulnerability stats graph saved as 'vulnerability_stats.png'")

# Plot functions
plt.figure(figsize=(10, 6))
ax = function_stats.plot(kind='bar', color='orange')
plt.title('Correct Identifications by Function Name')
plt.xlabel('Function Name')
plt.ylabel('Frequency')
plt.xticks(rotation=45)

# Add labels to bars
for p in ax.patches:
    ax.annotate(str(p.get_height()), (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 5), textcoords='offset points')

plt.tight_layout()
plt.savefig('result/Deepseek/function_stats.png')
print("Function stats graph saved as 'function_stats.png'")

# Generate percentage-based graphs
# Calculate percentages for vulnerabilities
vulnerability_percentage = (vulnerability_stats / data2['vulnerability'].value_counts()) * 100
plt.figure(figsize=(10, 6))
ax = vulnerability_percentage.plot(kind='bar', color='blue')
plt.title('Percentage of Correct Identifications by Vulnerability Type')
plt.xlabel('Vulnerability Type')
plt.ylabel('Percentage (%)')
plt.xticks(rotation=45)

# Add labels to bars
for p in ax.patches:
    ax.annotate(f"{p.get_height():.2f}%", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 5), textcoords='offset points')

plt.tight_layout()
plt.savefig('result/Deepseek/vulnerability_percentage.png')
print("Vulnerability percentage graph saved as 'vulnerability_percentage.png'")

# Calculate percentages for functions
function_percentage = (function_stats / data2['function_name'].value_counts()) * 100
plt.figure(figsize=(10, 6))
ax = function_percentage.plot(kind='bar', color='green')
plt.title('Percentage of Correct Identifications by Function Name')
plt.xlabel('Function Name')
plt.ylabel('Percentage (%)')
plt.xticks(rotation=45)

# Add labels to bars
for p in ax.patches:
    ax.annotate(f"{p.get_height():.2f}%", (p.get_x() + p.get_width() / 2., p.get_height()), ha='center', va='center', xytext=(0, 5), textcoords='offset points')

plt.tight_layout()
plt.savefig('result/Deepseek/function_percentage.png')
print("Function percentage graph saved as 'function_percentage.png'")
