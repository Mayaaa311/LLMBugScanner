#!/bin/bash
#SBATCH -J run_batch-data_full/CVE_clean_organized_b5/subfolder_7           # Job name
#SBATCH -N1                                         # Number of nodes
#SBATCH --ntasks-per-node=1            # Run only one task
#SBATCH --gres=gpu:A100:2            # Request 2 GPUs
#SBATCH --mem-per-gpu=128G         # Increase memory   
#SBATCH -t 200                         # Duration of the job
#SBATCH -o Report-codellama_ft%j-1.out                # Combined output and error messages file
#SBATCH --mail-type=FAIL       # Mail preferences
#SBATCH --mail-user=yyuan394@gatech.edu  # E-mail address for notifications
cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory
export TRITON_CACHE_DIR=/home/hice1/yyuan394/scratch/triton_cache
mkdir -p $TRITON_CACHE_DIR  # Ensure the directory exists

module load anaconda3/2023.03            # Load module dependencies
conda activate /home/hice1/yyuan394/scratch/env

# python src/bugscanner_cli.py -a finetune/model/Deepseek_finetuning_MessiQ_20ep_GPTLens40_byfunc_new/checkpoint-80 finetune/model/Nxcode_finetuning_MessiQ_20ep_GPTLens_40ep_byfunc_new finetune/model/final_models/gemma_messi_5ep_CVE_10ep -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r NTQAI/Nxcode-CQ-7B-orpo -d data_full/CVE_clean_organized_b5/subfolder_7 -o result/finetuned_rerun/finetuned_single/codellama_ft -k 5 -log logger
# python src/bugscanner_cli.py -a deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r NTQAI/Nxcode-CQ-7B-orpo -d data_full/CVE_clean_organized_b5/subfolder_7 -o result/finetuned_rerun/finetuned_single/codellama_ft -k 5 -log logger
python src/bugscanner_cli.py -a finetune/model/final_models/codellama_CVE_10ep -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r NTQAI/Nxcode-CQ-7B-orpo -d data_full/CVE_clean_organized_b5/subfolder_7 -o result/finetuned_rerun/finetuned_single/codellama_ft -k 5 -log logger

# python src/bugscanner_cli.py -a finetune/model/Deepseek_finetuning_MessiQ_20ep_GPTLens40_byfunc_new/checkpoint-80 -c finetune/model/Deepseek_finetuning_MessiQ_critic -r NTQAI/Nxcode-CQ-7B-orpo -d data_full/CVE_clean_organized_b5/subfolder_7 -o result/finetuned_rerun/finetuned_single/codellama_ft -k 5 -log logger

