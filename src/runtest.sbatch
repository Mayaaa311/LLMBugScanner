#!/bin/bash
#SBATCH -J testsmalldataset             # Job name
#SBATCH -N 1                            # Number of nodes
#SBATCH --ntasks=1                      # Run only one task
#SBATCH --gpus=4             # Request 2 GPUs
#SBATCH --mem=200G                      # Increase memory 
#SBATCH -t 200                          # Duration of the job
#SBATCH -o Report-%j.out                # Combined output and error messages file
#SBATCH --mail-type=BEGIN,END,FAIL       # Mail preferences
#SBATCH --mail-user=yyuan394@gatech.edu  # E-mail address for notifications

cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory

module load anaconda3/2023.03            # Load module dependencies
conda activate /home/hice1/yyuan394/scratch/env

# srun python src/bugscanner_cli.py -a AlfredPros/CodeLlama-7b-Instruct-Solidity m-a-p/OpenCodeInterpreter-DS-6.7B NTQAI/Nxcode-CQ-7B-orpo -c deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_test_small -k 5 -log logs_oct1
# srun python src/bugscanner_cli.py -a m-a-p/OpenCodeInterpreter-DS-6.7B -c m-a-p/OpenCodeInterpreter-DS-6.7B -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_parsed -k 5 -log logs_oct1
# python src/bugscanner_cli.py -a  AlfredPros/CodeLlama-7b-Instruct-Solidity -c m-a-p/OpenCodeInterpreter-DS-6.7B -r m-a-p/OpenCodeInterpreter-DS-6.7B -p m-a-p/OpenCodeInterpreter-DS-6.7B -d data_2 -o result_test_parser/trail3 -k 5 -log logs_oct1
# python src/bugscanner_cli.py -a NTQAI/Nxcode-CQ-7B-orpo  -c NTQAI/Nxcode-CQ-7B-orpo -r NTQAI/Nxcode-CQ-7B-orpo -d data_2 -o result -k 5 -log logger/log_nxcode

python src/bugscanner_cli.py -a NTQAI/Nxcode-CQ-7B-orpo  -c NTQAI/Nxcode-CQ-7B-orpo -r NTQAI/Nxcode-CQ-7B-orpo -d data_full/CVE_clean_organized -o result -k 5 -log logger/log_nxcode -res result_nxcodes_k3_beforeft/k3_n1_2024-11-11_19-21-40