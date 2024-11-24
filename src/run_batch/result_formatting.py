import os
import sys
def reformat_file_content(file_path):
    with open(file_path, 'r') as file:
        content = file.read()
    
    # Replace escaped newlines with actual newlines
    content = content.replace('\\n', '\n')
    
    # Remove all backslashes
    content = content.replace('\\', '')

    while content.startswith('\n'):
        content = content[1:] 
    while content.endswith('\n'):
        content = content[:-1]
        
    # Remove leading and trailing quotes if present
    
    while content.startswith('"') and content.endswith('"'):
        content = content[1:-1]
    if file_path.split('/')[-1] == 'NTQAI_Nxcode-CQ-7B-orpo_summarized0.csv':
        max_attempts = len(content)  # Limit the attempts to the length of the content
        attempts = 0
        
        while not content.startswith('dataname') and attempts < max_attempts:
            content = content[1:]  # Shift content to the right by one character
            attempts += 1
        
        # Check if 'dataname' was not found after all attempts
        if not content.startswith('dataname'):
            print("Warning: 'dataname' not found in content.")
    # Write the reformatted content back to the file
    with open(file_path, 'w') as file:
        file.write(content)

def process_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            print(f"Processing file: {file_path}")
            reformat_file_content(file_path)



def main():
    # Check if the correct number of arguments is provided
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <argument>")
        sys.exit(1)

    # Retrieve the argument
    argument = sys.argv[1]
    process_directory(argument)


if __name__ == "__main__":
    main()
