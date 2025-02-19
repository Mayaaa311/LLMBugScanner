import os

# Define the base folder and the file prefix to match
# base_folder = "result/Deepseek_k5_GPTLensOnly"
# base_folder = 'result/Deepseek_k5_MessiQOnly'
base_folder = 'result/finetuned_rerun/finetuned_single/codellama_ft'
# base_folder = 'result/Nxcode_k5_MessiOnly'
file_prefix = ""

# Iterate through all subfolders in the base folder
for subfolder in os.listdir(base_folder):
    # critic_folder = os.path.join(base_folder, subfolder, "critic")
    # # critic_folder = os.path.join(base_folder, subfolder, "final_output")
    
    # # Check if the 'critic' folder exists
    # if os.path.exists(critic_folder) and os.path.isdir(critic_folder):
    #     # List all files in the 'critic' folder
    #     for file_name in os.listdir(critic_folder):
    #         # Check if the file starts with the specified prefix
    #         if file_name.startswith(file_prefix):
    #             file_path = os.path.join(critic_folder, file_name)
    #             try:
    #                 # Delete the file
    #                 os.remove(file_path)
    #                 print(f"Deleted: {file_path}")
    #             except Exception as e:
    #                 print(f"Failed to delete {file_path}: {e}")

    # critic_folder = os.path.join(base_folder, subfolder, "critic_summary")
    # # critic_folder = os.path.join(base_folder, subfolder, "final_output")
    
    # # Check if the 'critic' folder exists
    # if os.path.exists(critic_folder) and os.path.isdir(critic_folder):
    #     # List all files in the 'critic' folder
    #     for file_name in os.listdir(critic_folder):
    #         # Check if the file starts with the specified prefix
    #         if file_name.startswith(file_prefix):
    #             file_path = os.path.join(critic_folder, file_name)
    #             try:
    #                 # Delete the file
    #                 os.remove(file_path)
    #                 print(f"Deleted: {file_path}")
    #             except Exception as e:
    #                 print(f"Failed to delete {file_path}: {e}")

    critic_folder = os.path.join(base_folder, subfolder, "critic")
    # critic_folder = os.path.join(base_folder, subfolder, "final_output")
    
    # Check if the 'critic' folder exists
    if os.path.exists(critic_folder) and os.path.isdir(critic_folder):
        # List all files in the 'critic' folder
        for file_name in os.listdir(critic_folder):
            # Check if the file starts with the specified prefix
            if file_name.startswith(file_prefix):
                file_path = os.path.join(critic_folder, file_name)
                try:
                    # Delete the file
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

    os.rmdir(critic_folder)
    # critic_folder = os.path.join(base_folder, subfolder, "ranker")
    critic_folder = os.path.join(base_folder, subfolder, "critic_summary")
    
    # Check if the 'critic' folder exists
    if os.path.exists(critic_folder) and os.path.isdir(critic_folder):
        # List all files in the 'critic' folder
        for file_name in os.listdir(critic_folder):
            # Check if the file starts with the specified prefix
            if file_name.startswith(file_prefix):
                file_path = os.path.join(critic_folder, file_name)
                try:
                    # Delete the file
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
    os.rmdir(critic_folder)
    critic_folder = os.path.join(base_folder, subfolder, "ranker")
    
    # Check if the 'critic' folder exists
    if os.path.exists(critic_folder) and os.path.isdir(critic_folder):
        # List all files in the 'critic' folder
        for file_name in os.listdir(critic_folder):
            # Check if the file starts with the specified prefix
            if file_name.startswith(file_prefix):
                file_path = os.path.join(critic_folder, file_name)
                try:
                    # Delete the file
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")

    os.rmdir(critic_folder)

    critic_folder = os.path.join(base_folder, subfolder, "final_output")
    
    # Check if the 'critic' folder exists
    if os.path.exists(critic_folder) and os.path.isdir(critic_folder):
        # List all files in the 'critic' folder
        for file_name in os.listdir(critic_folder):
            # Check if the file starts with the specified prefix
            if file_name.startswith(file_prefix):
                file_path = os.path.join(critic_folder, file_name)
                try:
                    # Delete the file
                    os.remove(file_path)
                    print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Failed to delete {file_path}: {e}")
    os.rmdir(critic_folder)