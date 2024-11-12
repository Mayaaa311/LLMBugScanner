import os
import shutil

# Paths
sbatch_template = """#!/bin/bash
#SBATCH -J resume_job_{job_id}          # Job name with job_id
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

python src/bugscanner_cli.py -a NTQAI/Nxcode-CQ-7B-orpo -c NTQAI/Nxcode-CQ-7B-orpo -r NTQAI/Nxcode-CQ-7B-orpo -d {data_folder} -k 5 -log logger/log_nxcode -res {resume_folder}
"""

# Paths and directories
data_base_path = '/home/hice1/yyuan394/scratch/LLMBugScanner/data_full/CVE_clean_organized'
resume_from_folder = 'result_nxcodes_k3_beforeft'
resume_batch_path = '/home/hice1/yyuan394/scratch/LLMBugScanner/src/run_batch/resume_batch_files'

# Clear the resume batch directory if it exists, then recreate it
if os.path.exists(resume_batch_path):
    shutil.rmtree(resume_batch_path)
os.makedirs(resume_batch_path, exist_ok=True)

# Iterate over each subfolder in resume_from_folder to create resume jobs
for i, subfolder in enumerate(os.listdir(resume_from_folder)):
    full_resume_folder_path = os.path.join(resume_from_folder, subfolder)
    
    # Check if it's a directory and corresponds to a previous job
    if os.path.isdir(full_resume_folder_path):
        # Fill in the sbatch template with specific paths
        sbatch_content = sbatch_template.format(
            job_id=i,
            data_folder=data_base_path,
            resume_folder=full_resume_folder_path
        )
        
        # Define the path for the sbatch file
        sbatch_file_path = os.path.join(resume_batch_path, f'resume_batch_{i}.sbatch')
        
        # Write the sbatch file
        with open(sbatch_file_path, 'w') as sbatch_file:
            sbatch_file.write(sbatch_content)
        
        # Submit the sbatch job
        # os.system(f'sbatch {sbatch_file_path}')
