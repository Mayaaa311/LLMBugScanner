#!/bin/bash
#SBATCH -J finetuningNxcode             # Job name
#SBATCH -N1                             # Number of nodes
#SBATCH --ntasks-per-node=1             # Run only one task
#SBATCH --gres=gpu:H100:1                    # Request 1 GPU of any type
#SBATCH --mem-per-gpu=128G              # Increase memory 
#SBATCH -t 16:00:00                         # Duration of the job
#SBATCH -o output/gemma_messi_5ep.out                # Combined output and error messages file

cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory

module load anaconda3/2023.03            # Load module dependencies
conda deactivate
conda init
conda activate BugScanner

echo $CONDA_PREFIX

#MODEL_ID="NTQAI/Nxcode-CQ-7B-orpo"
#MODEL_ID="AlfredPros/CodeLlama-7b-Instruct-Solidity"
#MODEL_ID="WisdomShell/CodeShell-7B-Chat"
#MODEL_ID="TechxGenus/CodeGemma-7b"

AUDITOR="finetune/model/gemma/gemma_messi_5ep"
#AUDITOR="finetune/model/codellama/codellama_messi_5ep"
#AUDITOR="finetune/model/gemma/gemma_CVE_10ep"
#AUDITOR="finetune/model/codellama/codellama_CVE_10ep"
#AUDITOR="finetune/model/gemma/gemma_messi_5ep_CVE_10ep"
#AUDITOR="finetune/model/codellama/codellama_messi_5ep_CVE_10ep"

CRITIC="NTQAI/Nxcode-CQ-7B-orpo"
RANKER="NTQAI/Nxcode-CQ-7B-orpo"

OUTPUT_DIR="eval_result/gemma_messi_5ep"
DATASET="data_full/0.8splitCVE_clean"

K=5

# srun python src/bugscanner_cli.py -a AlfredPros/CodeLlama-7b-Instruct-Solidity m-a-p/OpenCodeInterpreter-DS-6.7B NTQAI/Nxcode-CQ-7B-orpo -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_test_small -k 5 -log logs_oct1
# srun python src/bugscanner_cli.py -a m-a-p/OpenCodeInterpreter-DS-6.7B -c m-a-p/OpenCodeInterpreter-DS-6.7B -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_parsed -k 5 -log logs_oct1

srun python src/bugscanner_cli.py -a $AUDITOR -c $CRITIC -r $RANKER -d $DATASET -o $OUTPUT_DIR -k $K -log "logs"

#srun python finetune_model.py $MODEL_ID $OUTPUT_DIR $FINETUNE $DATASET1 #$DATASET2
# python3 convert_dataset.py
