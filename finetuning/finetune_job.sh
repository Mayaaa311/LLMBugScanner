#!/bin/bash
#SBATCH -JFinetune
#SBATCH -N1 --gres=gpu:A100:2 --ntasks-per-node=1 --mem-per-gpu=32G
#SBATCH -t4:00:00
#SBATCH -ofinetune.out

module load anaconda3
#conda init
conda deactivate
conda activate autotrain

srun autotrain --config config.yaml
