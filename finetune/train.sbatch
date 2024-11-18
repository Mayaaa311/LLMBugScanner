#!/bin/bash
#SBATCH -J finetuningNxcode             # Job name
#SBATCH -N1                             # Number of nodes
#SBATCH --ntasks-per-node=1             # Run only one task
#SBATCH --gres=gpu:A100                    # Request 1 GPU of any type
#SBATCH --mem-per-gpu=80G              # Increase memory 
#SBATCH -t 4:00:00                          # Duration of the job
#SBATCH -o output/finetune_codeshell_messi_10ep.out                # Combined output and error messages file

cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory

module load anaconda3/2023.03            # Load module dependencies
conda deactivate
conda activate BugScanner

echo $CONDA_PREFIX

#MODEL_ID="NTQAI/Nxcode-CQ-7B-orpo"
#MODEL_ID="AlfredPros/CodeLlama-7b-Instruct-Solidity"
MODEL_ID="WisdomShell/CodeShell-7B-Chat"
#MODEL_ID="TechxGenus/CodeGemma-7b"
#OUTPUT_DIR="model/codellama_finetuned/codellama_10ep/"
OUTPUT_DIR="model/codeshell/codeshell_messi_10ep/"

FINETUNE=0.0
DATASET="MessiQ_dataset/train_dataset1.json"

# srun python src/bugscanner_cli.py -a AlfredPros/CodeLlama-7b-Instruct-Solidity m-a-p/OpenCodeInterpreter-DS-6.7B NTQAI/Nxcode-CQ-7B-orpo -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_test_small -k 5 -log logs_oct1
# srun python src/bugscanner_cli.py -a m-a-p/OpenCodeInterpreter-DS-6.7B -c m-a-p/OpenCodeInterpreter-DS-6.7B -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_parsed -k 5 -log logs_oct1
srun python finetune_model.py $MODEL_ID $OUTPUT_DIR $FINETUNE $DATASET
# python3 convert_dataset.py
