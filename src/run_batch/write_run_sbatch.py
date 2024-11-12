import os
import shutil

# Paths
sbatch_template = """#!/bin/bash
#SBATCH -J testsmalldataset             # Job name
#SBATCH -N 1                            # Number of nodes
#SBATCH --ntasks=1                      # Run only one task
#SBATCH --gpus=4                        # Request 4 GPUs
#SBATCH --mem=200G                      # Increase memory
#SBATCH -t 200                          # Duration of the job
#SBATCH -o Report-%j.out                # Combined output and error messages file
#SBATCH --mail-type=BEGIN,END,FAIL      # Mail preferences
#SBATCH --mail-user=yyuan394@gatech.edu # E-mail address for notifications

cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory

module load anaconda3/2023.03           # Load module dependencies
conda activate /home/hice1/yyuan394/scratch/env

python src/bugscanner_cli.py -a NTQAI/Nxcode-CQ-7B-orpo -c NTQAI/Nxcode-CQ-7B-orpo -r NTQAI/Nxcode-CQ-7B-orpo -d {data_folder} -o {result_folder} -k 3 -log logs_nov3
"""

# change this to the data directory
data_base_path = '/home/hice1/yyuan394/scratch/LLMBugScanner/data_full/CVE_clean_organized'
# this is sbatch folder, do not change this 
sbatch_output_path = '/home/hice1/yyuan394/scratch/LLMBugScanner/src/run_batch/sbatch_files'

result_folder_name = 'result_nxcodes_k3_beforeft'
# Check if the directory exists
if os.path.exists(sbatch_output_path):
    # Clear the directory by removing it and all its contents
    shutil.rmtree(sbatch_output_path)

# Ensure the sbatch output directory exists
os.makedirs(sbatch_output_path, exist_ok=True)

# Iterate through subfolders in the data path
for i, subfolder in enumerate(os.listdir(data_base_path)):
    full_subfolder_path = os.path.join(data_base_path, subfolder)
    if os.path.isdir(full_subfolder_path):
        sbatch_content = sbatch_template.format(data_folder=full_subfolder_path, result_folder = result_folder_name)
        sbatch_file_path = os.path.join(sbatch_output_path, f'batch_{i}.sbatch')
        
        # Write the sbatch file
        with open(sbatch_file_path, 'w') as sbatch_file:
            sbatch_file.write(sbatch_content)
        
        # Submit the sbatch job
        os.system(f'sbatch {sbatch_file_path}')
