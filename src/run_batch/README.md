## Running a large dataset: 

1. Folder process.py: partition data folder's files into multiple subfolder of defined size
2. write_run_sbatch.py: for each subfolder, create a sbatch in sbatch_files directory, and run them. 
3. result_formatting.py: after running all batches, result is saved to the defined result directory, clean the result by running result_formatting multiple times til the results are formatted correctly
4. evaluate_batch.py: this read all result to memory(and save to file) while calculating accuracy with label

salloc --ntasks-per-node=60 --gpus=7
module load anaconda3/2023.03
conda activate /home/hice1/yyuan394/scratch/env
