import os
import shutil

# Paths
sbatch_template = """#!/bin/bash
#SBATCH -J run_batch-{data_folder}           # Job name
#SBATCH -N1                                         # Number of nodes
#SBATCH --ntasks-per-node=1            # Run only one task
#SBATCH --gpus=3            # Request 2 GPUs
#SBATCH --mem-per-gpu=128G         # Increase memory   
#SBATCH -t 200                         # Duration of the job
#SBATCH -o Report-{taskname}%j-{i}.out                # Combined output and error messages file
#SBATCH --mail-type=BEGIN,END,FAIL       # Mail preferences
#SBATCH --mail-user=yyuan394@gatech.edu  # E-mail address for notifications
cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory
export TRITON_CACHE_DIR=/home/hice1/yyuan394/scratch/triton_cache
mkdir -p $TRITON_CACHE_DIR  # Ensure the directory exists

module load anaconda3/2023.03            # Load module dependencies
conda activate /home/hice1/yyuan394/scratch/env

python src/bugscanner_cli.py -a finetune/model/Deepseek_finetuning_MessiQ_20ep_GPTLens40_byfunc_new/checkpoint-80 finetune/model/Nxcode_finetuning_MessiQ_20ep_GPTLens_40ep_byfunc_new finetune/model/final_models/gemma_messi_5ep_CVE_10ep -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r NTQAI/Nxcode-CQ-7B-orpo -d {data_folder} -o {result_folder} -k {k} -log logger
# python src/bugscanner_cli.py -a finetune/model/Deepseek_finetuning_MessiQ_20ep_GPTLens40_byfunc_new/checkpoint-80 -c finetune/model/Deepseek_finetuning_MessiQ_critic -r NTQAI/Nxcode-CQ-7B-orpo -d {data_folder} -o {result_folder} -k {k} -log logger

"""


# ------------------------------------------Change below definition to run and custom result folder name-------------------------------
# change this to the model you want to test
# data_path = 'data_full/0.8CVE_clean_organized_b5'
data_path = 'data_full/CVE_clean_organized_b5'

# model_name = 'finetune/model/deepseek_finetuning_MessiQ_20ep_new'
# model_name = 'finetune/model/Deepseek_finetuning_MessiQ_20ep_byfunc_new'
# model_name = 'finetune/model/deepseek_finetuning_GPTLens_70ep_new'
# model_name = 'finetune/model/deepseek_finetuning_MessiQ20_GPTLens'
model_name = 'finetune/model/deepseek_finetuning_alllinear_b32_20ep'
result_folder_name = 'result/multimodel/deepseek_nxcode_gemma_k5_origionalcritic_wcontext'

# model_name = 'finetune/model/deepseek_finetuning_MessiQ_20ep_new'
# result_folder_name ='result/Deepseek_k5_MessiQOnly'

# model_name = 'finetune/model/deepseek_finetuning_GPTLens_70ep_new'
# result_folder_name = 'result/Deepseek_k5_GPTLensOnly' 

# model_name ='finetune/model/Nxcode_finetuning_MessiQ_20ep_new'
# result_folder_name ='result/Nxcode_k5_MessiOnly'

# model_name = 'finetune/model/deepseek_finetuning_MessiQ20_GPTLens'
# result_folder_name ='result/Deepseek_k5_MessiQ_GPTLens'

# model_name = 'finetune/model/Nxcode_finetuning_MessiQ20_GPTLens50'
# result_folder_name ='result/Nxcode_k5_MessiQ_GPTLens'
# model_name = 'finetune/model/final_models/OpenCodeInterpreter_gptLensFT_ds'

# change this to the data folder you want to run
# data_path = 'data_full/CVE_clean_organized_b5'
# changet this to the k you want to run
k = 5
taskname = result_folder_name.split('/')[-1]
#change this to where you want to save your result

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
        sbatch_content = sbatch_template.format(data_folder=full_subfolder_path, result_folder = result_folder_name, model_name = model_name, k = k, i = i, taskname = taskname)
        sbatch_file_path = os.path.join(sbatch_output_path, f'batch_{i}.sbatch')
        
        # Write the sbatch file
        with open(sbatch_file_path, 'w') as sbatch_file:
            sbatch_file.write(sbatch_content)
        
        # Submit the  job
        # if(subfolder== 'subfolder_1'):
        os.system(f'sbatch {sbatch_file_path}')