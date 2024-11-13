#!/bin/bash
#SBATCH -J testsmalldataset             # Job name
#SBATCH -N 1                            # Number of nodes
#SBATCH --ntasks=1                      # Run only one task
#SBATCH --gpus=3                        # Request 4 GPUs
#SBATCH --mem=100G                      # Increase memory
#SBATCH -t 200                          # Duration of the job
#SBATCH -o Report-%j.out                # Combined output and error messages file
#SBATCH --mail-type=BEGIN,END,FAIL      # Mail preferences
#SBATCH --mail-user=ywang4343@gatech.edu # E-mail address for notifications

cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory

module load anaconda3/2023.03           # Load module dependencies
conda activate /home/hice1/ywang4343/scratch/env

python src/bugscanner_cli.py -a finetune/model -c finetune/model -r finetune/model -d data_full/CVE_clean_organized_b5/subfolder_3 -o result_nxcodes_finetuned -k 3 -log logs_nov3
