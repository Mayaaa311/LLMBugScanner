import os
import shutil

# Paths
sbatch_template = """#!/bin/bash
#SBATCH -J runbatch-{data_folder}           # Job name
#SBATCH -N 1                            # Number of nodes
#SBATCH --ntasks=1                      # Run only one task
#SBATCH --gpus=2                        # Request 4 GPUs
#SBATCH --mem=200G                      # Increase memory
#SBATCH -t 100                          # Duration of the job
#SBATCH -o Report-%j-allnx.out                # Combined output and error messages file
#SBATCH --mail-type=FAIL      # Mail preferences
#SBATCH --mail-user=yyuan394@gatech.edu # E-mail address for notifications

cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory

module load anaconda3/2023.03           # Load module dependencies
conda activate /home/hice1/yyuan394/scratch/env

python src/bugscanner_cli.py -a {model_name} -c {model_name} -r {model_name} -p {model_name} -d {data_folder} -o {result_folder} -k {k} -log logger
"""


# ------------------------------------------Change below definition to run and custom result folder name-------------------------------
# change this to the model you want to test
model_name = 'NTQAI/Nxcode-CQ-7B-orpo '
# change this to the data folder you want to run
data_path = 'data_full/CVE_clean_organized_b5'
# changet this to the k you want to run
k = 5
#change this to where you want to save your result
result_folder_name = 'result/result_nxcodes_k5_beforeft'

# ------------------------------------------DO NOT CHANGE BELOW CODE-------------------------------

sbatch_output_path = 'src/run_batch/sbatch_files'
# Check if the directory exists
if os.path.exists(sbatch_output_path):
    # Clear the directory by removing it and all its contents
    shutil.rmtree(sbatch_output_path)

# Ensure the sbatch output directory exists
os.makedirs(sbatch_output_path, exist_ok=True)

# Iterate through subfolders in the data path
for i, subfolder in enumerate(os.listdir(data_path)):
    full_subfolder_path = os.path.join(data_path, subfolder)
    if os.path.isdir(full_subfolder_path):
        sbatch_content = sbatch_template.format(data_folder=full_subfolder_path, result_folder = result_folder_name, model_name = model_name, k = k)
        sbatch_file_path = os.path.join(sbatch_output_path, f'batch_{i}.sbatch')
        
        # Write the sbatch file
        with open(sbatch_file_path, 'w') as sbatch_file:
            sbatch_file.write(sbatch_content)
        
        # Submit the sbatch job
        os.system(f'sbatch {sbatch_file_path}')
