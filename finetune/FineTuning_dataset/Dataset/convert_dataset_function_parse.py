import json
import os
from datasets import Dataset, load_dataset
import pandas as pd
from collections import defaultdict

# Paths
code_dir = "finetune/FineTuning_dataset/Dataset/code_folder"
label_file = "finetune/FineTuning_dataset/Dataset/combined_single_sheet.csv"
output_file = "finetune/FineTuning_dataset/Dataset/fine_tuning_data2.jsonl"

# Load labels
labels = pd.read_csv(label_file)

# Function to load the content of each Solidity file
def load_code_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Fallback to ISO-8859-1 encoding
        with open(filepath, 'r', encoding='ISO-8859-1') as file:
            return file.read()

# Aggregate vulnerabilities by file and contract
vulnerability_data = defaultdict(lambda: defaultdict(list))

for _, row in labels.iterrows():
    cve_id = row['file']
    function_name = row["contract"]
    vulnerability_type = row['vul_type']
    vulnerability_data[cve_id][function_name] = []
    if row['ground truth'] == '0':
        continue
    vulnerability_data[cve_id][function_name].append(vulnerability_type)
print(vulnerability_data)
# Generate and save JSONL data
with open(output_file, 'w') as out_file:
    for cve_id, contracts in vulnerability_data.items():
        file_path = os.path.join(code_dir, f"{cve_id}.sol")
        
        # Check if the file exists before reading it
        if os.path.isfile(file_path):
            code_content = load_code_content(file_path)
            
            for contract, vul_types in contracts.items():
                output_list = vul_types

                # Structure JSON entry with aggregated vulnerabilities
                entry = {
                    "messages": [
                        {"role": "system", "content": """Requirement: You are a smart contract auditor, identify most severe vulnerabilities of function {contract} in the provided code. Make sure that they are exploitable in real world and beneficial to attackers. 
                        Provide each identified vulnerability with its associated contract. Your output should strictly be limited to the following vulnerability types: 

                        1. Reentrancy: Reentrancy vulnerability occurs when an invocation to call.value can call back to itself through a chain of calls, allowing unexpected repeated money transfers.

                        2. Timestamp Dependency: The timestamp dependency vulnerability exists when a function uses the block timestamp as a condition to conduct critical operations, such as transferring Ether.

                        3. Block Number Dependency: The block number dependency vulnerability occurs when a function uses the block number (block.number) as a condition in a branch statement, which can be exploited for malicious behaviors.

                        4. Dangerous Delegatecall: The delegatecall vulnerability arises when an attacker can manipulate the argument of delegatecall, potentially gaining control over the contract and executing arbitrary code.

                        5. Ether Frozen: The Ether frozen vulnerability occurs when a contract relies on external code to transfer Ether without having its own functions to send Ether. This can result in all Ether in the contract being permanently frozen.

                        6. Unchecked External Call: This vulnerability arises when the return value of a call to an external contract is not checked, leading to potential unhandled exceptions within the call-chain.

                        7. Integer Overflow/Underflow: Integer overflow vulnerability occurs when an arithmetic operation results in a numeric value outside the range of the integer type, causing truncated values due to limitations in the EVM stack.

                        8. Dangerous Ether Strict Equality: This vulnerability exists when Ether balance (this.balance) is used as a condition in branch statements, which can be unreliable since the balance may be affected by other factors, such as pre-stored Ether or selfdestruct.
                        
                        You should ONLY output a json in below json format:""".format(contract=contract)+"""
                        {
                            "output_list": ["<short_vulnera_desc_1>", "<short_vulnera_desc_2>", ...]
                        }"""},

                        {"role": "user", "content": f"Code Input: \n\n{code_content}"},
                        {"role": "assistant", "content": json.dumps({"output_list": output_list}, indent=4)}
                    ]
                }
                
                # Write to JSONL file
                out_file.write(json.dumps(entry) + "\n")
                # print(entry)
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
dataset["train"].to_json("finetune/FineTuning_dataset/Dataset/train_dataset2.json", orient="records")
dataset["test"].to_json("finetune/FineTuning_dataset/Dataset/test_dataset2.json", orient="records")

print(f"Training and testing datasets saved successfully.")
