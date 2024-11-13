import os
import shutil
import argparse


def distribute_files(source_folder, target_folder, files_per_subfolder):
    # Ensure the target folder exists
    os.makedirs(target_folder, exist_ok=True)
    
    # List all files in the source folder
    files = [f for f in os.listdir(source_folder) if os.path.isfile(os.path.join(source_folder, f))]
    
    subfolder_index = 1
    file_counter = 0
    current_subfolder = None

    for file in files:
        # Create a new subfolder if needed
        if file_counter % files_per_subfolder == 0:
            current_subfolder = os.path.join(target_folder, f'subfolder_{subfolder_index}')
            print(current_subfolder, "created")
            os.makedirs(current_subfolder, exist_ok=True)
            subfolder_index += 1
        
        # Copy file to the current subfolder
        shutil.copy2(os.path.join(source_folder, file), os.path.join(current_subfolder, file))
        
        file_counter += 1

def main():
    # Argument parser for files_per_subfolder
    parser = argparse.ArgumentParser(description="Distribute files into subfolders.")
    parser.add_argument("files_per_subfolder", type=int, help="Number of files per subfolder")
    args = parser.parse_args()
    
    # Source and target folders
    source_folder = '/home/hice1/yyuan394/scratch/LLMBugScanner/data_full/CVE_clean'
    target_folder = '/home/hice1/yyuan394/scratch/LLMBugScanner/data_full/CVE_clean_organized'
    
    # Clear target folder if it exists
    if os.path.exists(target_folder) and os.path.isdir(target_folder):
        shutil.rmtree(target_folder)
        print(f"The folder '{target_folder}' has been cleared.")
    
    file_per_subfolder = 5
    if args.files_per_subfolder:
        file_per_subfolder = args.files_per_subfolder
        
    # Run distribution
    distribute_files(source_folder, target_folder, file_per_subfolder)

if __name__ == "__main__":
    main()