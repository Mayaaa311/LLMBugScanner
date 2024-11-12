#!/bin/bash
#SBATCH -J finetuningNxcode1             # Job name
#SBATCH -N 1                            # Number of nodes
#SBATCH --ntasks=1                      # Run only one task
#SBATCH --gpus=3           # Request 2 GPUs
#SBATCH -t 300                          # Duration of the job
#SBATCH -o Report-%j.out                # Combined output and error messages file
#SBATCH --mail-type=BEGIN,END,FAIL       # Mail preferences
#SBATCH --mail-user=yyuan394@gatech.edu  # E-mail address for notifications

cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory

export TRITON_CACHE_DIR=/home/hice1/yyuan394/scratch/triton_cache
mkdir -p $TRITON_CACHE_DIR  # Ensure the directory exists

module load anaconda3/2023.03            # Load module dependencies
# conda activate /home/hice1/yyuan394/scratch/env
conda activate /home/hice1/yyuan394/scratch/env

# srun python src/bugscanner_cli.py -a AlfredPros/CodeLlama-7b-Instruct-Solidity m-a-p/OpenCodeInterpreter-DS-6.7B NTQAI/Nxcode-CQ-7B-orpo -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_test_small -k 5 -log logs_oct1
# srun python src/bugscanner_cli.py -a m-a-p/OpenCodeInterpreter-DS-6.7B -c m-a-p/OpenCodeInterpreter-DS-6.7B -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_parsed -k 5 -log logs_oct1
python3 finetune/finetune_nxcode.py
# python3 finetune/FineTuning_dataset/Dataset/label_process.py