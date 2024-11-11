#!/bin/bash
#SBATCH -J testsmalldataset             # Job name
#SBATCH -N 1                            # Number of nodes
#SBATCH --ntasks=1                      # Run only one task
#SBATCH --gpus=4                        # Request 4 GPUs
#SBATCH --mem=200G                      # Increase memory
#SBATCH -t 200                          # Duration of the job
#SBATCH -o Report-%j.out                # Combined output and error messages file
#SBATCH --mail-type=BEGIN,END,FAIL      # Mail preferences
#SBATCH --mail-user=yyuan394@gatech.edu # E-mail address for notifications

cd $SLURM_SUBMIT_DIR                    # Correctly change to the submit directory

module load anaconda3/2023.03           # Load module dependencies
conda activate /home/hice1/yyuan394/scratch/env

python src/bugscanner_cli.py -a NTQAI/Nxcode-CQ-7B-orpo -c NTQAI/Nxcode-CQ-7B-orpo -r NTQAI/Nxcode-CQ-7B-orpo -d /home/hice1/yyuan394/scratch/LLMBugScanner/data_full/CVE_clean_organized/subfolder_9 -o result_nxcodes_k3 -k 3 -log logs_nov3
