import os

def reformat_file_content(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Replace escaped newlines with actual newlines
    content = content.replace('\\n', '\n')
    
    # Remove all backslashes
    content = content.replace('\\', '')
    if content.startswith('\n'):
        content = content[1:] 
    if content.endswith('\n'):
        content = content[:-1]
        
    # Remove leading and trailing quotes if present
    if content.startswith('"') and content.endswith('"'):
        content = content[1:-1]

    # Write the reformatted content back to the file
    with open(file_path, 'w') as file:
        file.write(content)

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")
            reformat_file_content(file_path)

# Path to the main folder
main_folder = '/home/hice1/yyuan394/scratch/LLMBugScanner/result_batches_run2'

process_directory(main_folder)
