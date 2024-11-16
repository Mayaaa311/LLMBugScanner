#!/bin/bash
#SBATCH -J runbatch-data_full/CVE_clean_organized_b5/subfolder_21           # Job name
#SBATCH -N 1                            # Number of nodes
#SBATCH --ntasks=1                      # Run only one task
#SBATCH --gpus=3           
#SBATCH --mem=100G   
#SBATCH -t 300                          # Duration of the job
#SBATCH -o Report-%j-3.out                # Combined output and error messages file
#SBATCH --mail-type=BEGIN,END,FAIL       # Mail preferences
#SBATCH --mail-user=yyuan394@gatech.edu  # E-mail address for notifications
cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory
export TRITON_CACHE_DIR=/home/hice1/yyuan394/scratch/triton_cache
mkdir -p $TRITON_CACHE_DIR  # Ensure the directory exists

module load anaconda3/2023.03            # Load module dependencies
conda activate /home/hice1/yyuan394/scratch/env


python src/bugscanner_cli.py -a finetune/model/Nxcode_instructional_finetuning_alllinear -c finetune/model/Nxcode_instructional_finetuning_alllinear -r NTQAI/Nxcode-CQ-7B-orpo -d  data_full/CVE_clean_organized_b5/subfolder_21 -o result/result_nxcodes_k5_instructional_ftlinear_newversion -k 5 -log logger
# python src/bugscanner_cli.py -a finetune/model/Nxcode_instructional_finetuning_alllinear -c finetune/model/Nxcode_instructional_finetuning_alllinear -r  finetune/model/Nxcode_instructional_finetuning_alllinear -d  data_full/CVE_clean_organized_b5/subfolder_21 -o result/result_nxcodes_k5_instructional_ftlinear_newversion -k 5 -log logger

