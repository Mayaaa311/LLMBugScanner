import json

def process_generated_labels(file_path):
    dataset = []
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            try:
                # Parse each line as JSON
                label_data = json.loads(line.strip())
                if 'generated_text' in label_data:
                    generated_text = label_data['generated_text']
                    
                    # Process the generated text as required
                    # Example of constructing a dataset entry:
                    dataset.append({
                        "messages": [
                            {"role": "system", "content": "You are a smart contract auditor, identify the top 1 severe vulnerabilities in the provided smart contract and the function it is in, provide detailed reasoning and explanation"},
                            {"role": "user", "content": "Insert the specific Solidity code here."},
                            {"role": "assistant", "content": generated_text}
                        ]
                    })
            except json.JSONDecodeError as e:
                print(f"Failed to parse line: {line.strip()} - Error: {e}")

    return dataset

# File path to the generated labels
file_path = '/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/FineTuning_dataset/new_label_dataset.txt'
dataset = process_generated_labels(file_path)

# Save the dataset to a new JSON file
output_file = '/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/FineTuning_dataset/processed_generated_label_dataset.json'
with open(output_file, 'w') as outfile:
    json.dump(dataset, outfile, indent=4)
