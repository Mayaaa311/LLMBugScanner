#!/usr/bin/env python3

import argparse
import os
import logging
import time
from lens import BugScanner

# Import all the model classes
from lens import Huggingface_LLM, pipeline_LLM, gemma_LLM
from datetime import datetime
# Model-to-class map
MODEL_CLASS_MAP = {
    "AlfredPros/CodeLlama-7b-Instruct-Solidity": Huggingface_LLM,
    "m-a-p/OpenCodeInterpreter-DS-6.7B": Huggingface_LLM,
    "NTQAI/Nxcode-CQ-7B-orpo": Huggingface_LLM,
    "Artigenz/Artigenz-Coder-DS-6.7B": Huggingface_LLM,
    "bigcode/starcoder2-15b": Huggingface_LLM,
    "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct": Huggingface_LLM,
    "Qwen/CodeQwen1.5-7B": Huggingface_LLM,
    "meta-llama/Llama-3.1-8B-Instruct": Huggingface_LLM,
    "meta-llama/CodeLlama-7b-hf": pipeline_LLM,
    "WisdomShell/CodeShell-7B-Chat": Huggingface_LLM,
    "google/codegemma-7b": gemma_LLM,
}
required_folders = ["auditor", "auditor_summary", "critic", "critic_summary", "ranker", "final_output"]
def setup_logging(log_folder):
    """Set up logging with the specified log folder."""

    os.makedirs(log_folder, exist_ok=True)
    
    log_file = os.path.join(log_folder, "bugscanner.log")

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),  # Logs to the specified log file
            logging.StreamHandler()  # Logs to the console
        ]
    )

def get_model_instance(model_name, prompt_path=None, model_params_path=None):
    """Instantiate the correct model class based on the model name."""
    model_class = MODEL_CLASS_MAP.get(model_name)
    
    if not model_class:
        return Huggingface_LLM(model_id=model_name, prompt_path=prompt_path)
    
    return model_class(model_id=model_name, prompt_path=prompt_path)
    
def find_earliest_missing_folder(resume_folder):
    """
    Checks each subfolder in the resume_folder and returns the earliest missing stage
    in the expected order ('auditor', 'auditor_summary', 'critic', 'critic_summary', 'ranker', 'final_output')
    across all subfolders. If all stages are complete, returns -1.
    """
    earliest_missing_stage = 'final_output'
    # earliest_missing_subfolder = 'final_output'
    
    # Iterate through each subfolder
    for subfolder in os.listdir(resume_folder):
        subfolder_path = os.path.join(resume_folder, subfolder)
        
        # Only check directories
        if not os.path.isdir(subfolder_path):
            continue
        
        # Check each required folder in order
        for folder in required_folders:
            folder_path = os.path.join(subfolder_path, folder)
            if not os.path.exists(folder_path):
                # Update if this is the first missing stage found
                if required_folders.index(folder) < required_folders.index(earliest_missing_stage):
                    earliest_missing_stage = folder
    
    # Return -1 if all folders are present
    if earliest_missing_stage is None:
        return -1, -1
    
    return earliest_missing_stage


def main():
    # Start overall timer
    overall_start_time = time.time()

    parser = argparse.ArgumentParser(description="Run bug scanner with auditors, critic, ranker, and data folder")

    parser.add_argument('-a', '--auditors', nargs='+', required=True, help='One or more auditor model IDs')
    parser.add_argument('-c', '--critic', help='Optional critic model ID (only one allowed)')
    parser.add_argument('-r', '--ranker', help='Optional ranker model ID (only one allowed)')
    parser.add_argument('-p', '--parser', help='Optional parser model ID (only one allowed)')
    parser.add_argument('-d', '--data_folder', required=True, help='Path to the data folder')
    parser.add_argument('-o', '--output_folder', required=False, help='Output results folder')
    parser.add_argument('-k', '--topk', required=True, help='Top k results')
    parser.add_argument('-log', '--log_folder', required=True, help='Folder to save log files')

    args = parser.parse_args()

    # Set up logging with the specified log folder
    setup_logging(args.log_folder)

    # Log start of the process
    logging.info("Initializing auditor models...")
    auditor_models = [
        get_model_instance(auditor, prompt_path='templates/auditor_v1.txt') for auditor in args.auditors
    ]
    logging.info(f"Auditor models: {', '.join(args.auditors)}")

    critic_model = None
    if args.critic:
        logging.info(f"Initializing critic model: {args.critic}")
        critic_model = get_model_instance(args.critic, prompt_path='templates/critic_v1.txt')
    else:
        logging.info("No critic model specified.")

    ranker_model = None
    if args.ranker:
        logging.info(f"Initializing ranker model: {args.ranker}")
        ranker_model = get_model_instance(args.ranker, prompt_path='templates/topk.txt')
    else:
        logging.info("No ranker model specified.")
    summarizer_model = None
    if args.parser:
        logging.info(f"Initializing parser model: {args.parser}")
        summarizer_model = get_model_instance(args.parser, prompt_path='templates/summarizer.txt')
    else:
        summarizer_model = get_model_instance("NTQAI/Nxcode-CQ-7B-orpo", prompt_path='templates/summarizer.txt')
        logging.info("No ranker model specified.")
    logging.info("Initializing BugScanner with the given models...")

    detector = BugScanner(
        auditor_models=auditor_models,
        critic_model=critic_model,
        ranker_model=ranker_model,
        summarizer_model= summarizer_model
    )

    logging.info("BugScanner initialization completed.")

    # Before the data processing loop
    logging.info(f"Starting the bug scanning pipeline with Top-K = {args.topk}...")

    # List all files in the data folder
    data_files = [f for f in os.listdir(args.data_folder) if f.endswith('.sol')]
    logging.info(f"Found {len(data_files)} .sol files in the folder: {args.data_folder}")
    output_name = "output"
    if args.output_folder:
        output_name = args.output_folder

    logging.info(f"Output will be saved in: {output_name}")

    # if args.resume_folder:
    #     logging.info(f"Initializing resuming: {args.resume_folder}")
    #     folder_nm = find_earliest_missing_folder(args.resume_folder)
        
    #     if(folder_nm != 'auditor'):
    #         folder_nm1 = required_folders[required_folders.index(folder_nm)-1] 
    #         folders = detector.recreate_subfolder_name_list(args.resume_folder, folder_nm1)
    #         print("missing folder: ", folders)
    #         detector.topk = args.topk
    #         detector.result_dir = args.resume_folder

    #         # Define the processing steps in sequential order
    #         steps = [
    #             detector.run_batch_auditor,
    #             detector.run_batch_summarizer1,
    #             detector.run_batch_critic,
    #             detector.run_batch_summarizer2,
    #             detector.run_batch_ranker,
    #             detector.run_batch_output_formatter
    #         ]

    #         # Find the starting index based on the folder's position in required_folders
    #         start_index = required_folders.index(folder_nm) 
    #         print("stratr from step: ",start_index)
    #         # Execute steps starting from the determined index
    #         for idx, step in enumerate(steps[start_index:], start=start_index):
    #             print(step)
    #             if idx == 2:
    #                 folders = step(folders, args.data_folder)
    #             elif idx > 0:
    #                 folders = step(folders)
    #             else:
    #                 folders = step(args.data_folder)
    #         return

  



    # Run the bug scanner pipeline
    detector.run_pipeline(
        code_folder=args.data_folder,
        result_dir=output_name,
        topk=args.topk
    )

    # Log final completion and overall time
    overall_time_taken = time.time() - overall_start_time
    logging.info(f"Bug scanning pipeline completed for all files in {overall_time_taken:.2f} seconds.")

if __name__ == '__main__':
    main()