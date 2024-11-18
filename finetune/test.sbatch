#!/bin/bash
#SBATCH -J finetuningNxcode             # Job name
#SBATCH -N1                             # Number of nodes
#SBATCH --ntasks-per-node=1             # Run only one task
#SBATCH --gres=gpu:A100                    # Request 1 GPU of any type
#SBATCH --mem-per-gpu=80G              # Increase memory
#SBATCH -t 8:00:00                          # Duration of the job
#SBATCH -o output/test_gemma_0ep.out                # Combined output and error messages file

cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory

module load anaconda3/2023.03            # Load module dependencies
conda deactivate
conda activate BugScanner

echo $CONDA_PREFIX

#PEFT_MODEL_ID="model/nxcode/nxcode_10ep/"
#PEFT_MODEL_ID="model/codellama_finetuned/codellama_10ep/"
#PEFT_MODEL_ID="NTQAI/Nxcode-CQ-7B-orpo"
PEFT_MODEL_ID="TechxGenus/CodeGemma-7b"
#PEFT_MODEL_ID="WisdomShell/CodeShell-7B-Chat"
#PEFT_MODEL_ID="AlfredPros/CodeLlama-7b-Instruct-Solidity"

FINETUNED=0.0
DATASET="CVE_dataset/fine_tuning_data.jsonl"

# srun python src/bugscanner_cli.py -a AlfredPros/CodeLlama-7b-Instruct-Solidity m-a-p/OpenCodeInterpreter-DS-6.7B NTQAI/Nxcode-CQ-7B-orpo -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_test_small -k 5 -log logs_oct1
# srun python src/bugscanner_cli.py -a m-a-p/OpenCodeInterpreter-DS-6.7B -c m-a-p/OpenCodeInterpreter-DS-6.7B -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_parsed -k 5 -log logs_oct1
srun python3 test_model.py $PEFT_MODEL_ID $FINETUNED $DATASET
# python3 finetune/generate_label.py
