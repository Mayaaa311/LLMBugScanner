import os
import shutil

# Paths
sbatch_template = """#!/bin/bash
#SBATCH -J runbatch-{data_folder}           # Job name
#SBATCH -N1                                         # Number of nodes
#SBATCH --ntasks-per-node=1            # Run only one task
#SBATCH --gres=gpu:H100:1               # Request 1 H100
#SBATCH --mem-per-gpu=128G         # Increase memory   
#SBATCH -t 200                         # Duration of the job
#SBATCH -o Report-%j-{i}.out                # Combined output and error messages file
#SBATCH --mail-type=BEGIN,END,FAIL       # Mail preferences
#SBATCH --mail-user=yyuan394@gatech.edu  # E-mail address for notifications
cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory
export TRITON_CACHE_DIR=/home/hice1/yyuan394/scratch/triton_cache
mkdir -p $TRITON_CACHE_DIR  # Ensure the directory exists

module load anaconda3/2023.03            # Load module dependencies
conda activate /home/hice1/yyuan394/scratch/env

# python src/bugscanner_cli.py -a deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct NTQAI/Nxcode-CQ-7B-orpo m-a-p/OpenCodeInterpreter-DS-6.7B AlfredPros/CodeLlama-7b-Instruct-Solidity google/codegemma-7b -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct  -d {data_folder} -o {result_folder} -k {k} -log logger
python src/bugscanner_cli.py -a finetune/model/final_models/deepseek_finetuning_CVE_10ep finetune/model/final_models/codellama_CVE_10ep finetune/model/final_models/gemma_messi_5ep_CVE_10ep  finetune/model/final_models/Nxcode_instructional_finetuning_alllinear finetune/model/final_models/OpenCodeInterpreter_gptLensFT_ds -c finetune/model/final_models/deepseek_finetuning_CVE_10ep -r finetune/model/final_models/deepseek_finetuning_CVE_10ep -d {data_folder} -o {result_folder} -k {k} -log logger

# python src/bugscanner_cli.py -a {model_name} -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -d {data_folder} -o {result_folder} -k {k} -log logger
# python src/bugscanner_cli.py -a {model_name} -c {model_name} -r  {model_name} -d  {data_folder} -o {result_folder} -k {k} -log logger

"""


# ------------------------------------------Change below definition to run and custom result folder name-------------------------------
# change this to the model you want to test
# model_name = 'deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct'
model_name = 'finetune/model/deepseek_finetuning_specfunc0.05_alllinear_b32_10epoch_instructional'
# model_name = 'google/codegemma-7b'
# model_name = 'finetune/model/Nxcode_outdataset1/checkpoint-25000'
# change this to the data folder you want to run
# data_path = 'data_full/0.8CVE_clean_organized_b5'
data_path = 'data_full/CVE_clean_organized_b5'
# changet this to the k you want to run
k = 5
#change this to where you want to save your result
# result_folder_name = 'result/result_deepseek_k5_beforeft'

result_folder_name ='result/final_5_model_evaluation_1'

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
        sbatch_content = sbatch_template.format(data_folder=full_subfolder_path, result_folder = result_folder_name, model_name = model_name, k = k, i = i)
        sbatch_file_path = os.path.join(sbatch_output_path, f'batch_{i}.sbatch')
        
        # Write the sbatch file
        with open(sbatch_file_path, 'w') as sbatch_file:
            sbatch_file.write(sbatch_content)
        
        # Submit the  job
        # if(subfolder== 'subfolder_12'):
        os.system(f'sbatch {sbatch_file_path}')

