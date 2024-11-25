#!/bin/bash
#SBATCH -J runbatch-data_full/CVE_clean_organized_b5/subfolder_2           # Job name
#SBATCH -N1                                         # Number of nodes
#SBATCH --ntasks-per-node=1            # Run only one task
#SBATCH --gres=gpu:H100:1               # Request 1 H100
#SBATCH --mem-per-gpu=128G         # Increase memory   
#SBATCH -t 200                         # Duration of the job
#SBATCH -o Report-%j-0.out                # Combined output and error messages file
#SBATCH --mail-type=BEGIN,END,FAIL       # Mail preferences
#SBATCH --mail-user=yyuan394@gatech.edu  # E-mail address for notifications
cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory
export TRITON_CACHE_DIR=/home/hice1/yyuan394/scratch/triton_cache
mkdir -p $TRITON_CACHE_DIR  # Ensure the directory exists

module load anaconda3/2023.03            # Load module dependencies
conda activate /home/hice1/yyuan394/scratch/env

# python src/bugscanner_cli.py -a deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct NTQAI/Nxcode-CQ-7B-orpo m-a-p/OpenCodeInterpreter-DS-6.7B AlfredPros/CodeLlama-7b-Instruct-Solidity google/codegemma-7b -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct  -d data_full/CVE_clean_organized_b5/subfolder_2 -o result/final_5_model_evaluation_1 -k 5 -log logger
python src/bugscanner_cli.py -a finetune/model/final_models/deepseek_finetuning_CVE_10ep finetune/model/final_models/codellama_CVE_10ep finetune/model/final_models/gemma_messi_5ep_CVE_10ep  finetune/model/final_models/Nxcode_instructional_finetuning_alllinear finetune/model/final_models/OpenCodeInterpreter_gptLensFT_ds -c finetune/model/final_models/deepseek_finetuning_CVE_10ep -r finetune/model/final_models/deepseek_finetuning_CVE_10ep -d data_full/CVE_clean_organized_b5/subfolder_2 -o result/final_5_model_evaluation_1 -k 5 -log logger

# python src/bugscanner_cli.py -a finetune/model/deepseek_finetuning_specfunc0.05_alllinear_b32_10epoch_instructional -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -d data_full/CVE_clean_organized_b5/subfolder_2 -o result/final_5_model_evaluation_1 -k 5 -log logger
# python src/bugscanner_cli.py -a finetune/model/deepseek_finetuning_specfunc0.05_alllinear_b32_10epoch_instructional -c finetune/model/deepseek_finetuning_specfunc0.05_alllinear_b32_10epoch_instructional -r  finetune/model/deepseek_finetuning_specfunc0.05_alllinear_b32_10epoch_instructional -d  data_full/CVE_clean_organized_b5/subfolder_2 -o result/final_5_model_evaluation_1 -k 5 -log logger

