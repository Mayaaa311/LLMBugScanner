#!/bin/bash
#SBATCH -JBugScanner
#SBATCH -N1 --gres=gpu:A100:1 --ntasks-per-node=1 --mem-per-gpu=32G
#SBATCH -t1:00:00
#SBATCH -ojob_result.out

module load anaconda3
#conda init
conda deactivate
conda activate BugScanner

pip install langchain_core

echo $CONDA_PREFIX

srun python src/main.py
