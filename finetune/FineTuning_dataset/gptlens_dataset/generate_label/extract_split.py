import json
import shutil
import os
def copy_matching_files(source_dir, destination_dir, matching_files):
    """
    Copies files from the source directory to the destination directory based on matching filenames.
    Creates the destination directory if it does not exist.
    
    Args:
        source_dir (str): Path to the source directory containing all files.
        destination_dir (str): Path to the destination directory.
        matching_files (list): List of filenames to be copied.
    """
    # Ensure destination directory exists
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)
        print(f"Created directory: {destination_dir}")

    # Copy matching files
    for file_name in matching_files:
        source_file = os.path.join(source_dir, file_name)
        destination_file = os.path.join(destination_dir, file_name)

        if os.path.exists(source_file):
            shutil.copy2(source_file, destination_file)
            print(f"Copied: {source_file} to {destination_file}")
        else:
            print(f"File not found: {source_file}")

def load_jsonl(file_path):
    """Load a JSONL file and return a list of dictionaries."""
    with open(file_path, 'r') as file:
        return [json.loads(line.strip()) for line in file]

def extract_content(json_data):
    """Extract 'content' field from the JSON data."""
    content_set = set()
    for entry in json_data:
        for message in entry.get("messages", []):
            if message["role"] == "user":  # Compare the 'content' under 'user'
                content_set.add(message["content"])
    return content_set

def compare_datasets(train_path, fine_tuning_path):
    """Compare train_dataset.jsonl and fine_tuning_data.jsonl based on content."""
    # Load datasets
    train_data = load_jsonl(train_path)
    fine_tuning_data = load_jsonl(fine_tuning_path)

    # Extract content from both datasets
    train_content = extract_content(train_data)
    fine_tuning_matches = []

    # Compare with fine_tuning_data
    for entry in fine_tuning_data:
        data_name = None
        for message in entry.get("messages", []):
            if message["role"] == "user":  # Find content to match
                if message["content"] in train_content:
                    # Extract data_name if match found
                    data_name = next(
                        (msg.get("data_name") for msg in entry["messages"] if "data_name" in msg), None
                    )
                    if data_name:
                        fine_tuning_matches.append(data_name)
                    break

    return fine_tuning_matches

if __name__ == "__main__":
    # File paths
    train_dataset_path = "finetune/FineTuning_dataset/gptlens_dataset/0.8split_dataset.json"
    fine_tuning_dataset_path = "finetune/FineTuning_dataset/fine_tuning_data.jsonl"

    # Compare and output matches
    matching_data_names = compare_datasets(train_dataset_path, fine_tuning_dataset_path)


     # Define paths
    source_folder = "data_full/CVE_clean"
    destination_folder = "data_full/0.8splitCVE_clean"

    copy_matching_files(source_folder, destination_folder, matching_data_names)
    print("Matching data names:", matching_data_names)
