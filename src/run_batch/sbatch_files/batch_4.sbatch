#!/bin/bash
#SBATCH -J runbatch-data_full/CVE_clean_organized_b5/subfolder_9           # Job name
#SBATCH -N 1                            # Number of nodes
#SBATCH --ntasks=1                      # Run only one task
#SBATCH --gpus=2                        # Request 4 GPUs
#SBATCH --mem=200G                      # Increase memory
#SBATCH -t 100                          # Duration of the job
#SBATCH -o Report-%j-4.out   # Combined output and error messages file
#SBATCH --mail-type=FAIL      # Mail preferences
#SBATCH --mail-user=yyuan394@gatech.edu # E-mail address for notifications

cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory
export TRITON_CACHE_DIR=/home/hice1/yyuan394/scratch/triton_cache
mkdir -p $TRITON_CACHE_DIR  # Ensure the directory exists

module load anaconda3/2023.03            # Load module dependencies
conda activate /home/hice1/yyuan394/scratch/env


python src/bugscanner_cli.py -a finetune/model/Nxcode_outdataset1/checkpoint-10000 -c finetune/model/Nxcode_outdataset1/checkpoint-10000 -r finetune/model/Nxcode_outdataset1/checkpoint-10000 -d data_full/CVE_clean_organized_b5/subfolder_9 -o result/result_nxcodes_k5_ft26000 -k 5 -log logger
