#!/usr/bin/env python3

import argparse
import os
import logging
import time
from lens import BugScanner

# Import all the model classes
from lens import Huggingface_LLM, pipeline_LLM, gemma_LLM

# Model-to-class map
MODEL_CLASS_MAP = {
    "AlfredPros/CodeLlama-7b-Instruct-Solidity": Huggingface_LLM,
    "m-a-p/OpenCodeInterpreter-DS-6.7B": Huggingface_LLM,
    "NTQAI/Nxcode-CQ-7B-orpo": Huggingface_LLM,
    "Artigenz/Artigenz-Coder-DS-6.7B": Huggingface_LLM,
    "bigcode/starcoder2-15b": Huggingface_LLM,
    "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct": Huggingface_LLM,
    "Qwen/CodeQwen1.5-7B": pipeline_LLM,
    "meta-llama/Llama-3.1-8B-Instruct": pipeline_LLM,
    "meta-llama/CodeLlama-7b-hf": pipeline_LLM,
    "WisdomShell/CodeShell-7B-Chat": Huggingface_LLM,
    "google/codegemma-7b": gemma_LLM,
}

def setup_logging(log_folder):
    """Set up logging with the specified log folder."""
    if not os.path.exists(log_folder):
        os.makedirs(log_folder)
    
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
        raise ValueError(f"Model {model_name} is not recognized or not supported.")
    
    # Return the instantiated model class with the necessary parameters
    if model_params_path:
        return model_class(model_id=model_name, prompt_path=prompt_path, model_params_path=model_params_path)
    else:
        return model_class(model_id=model_name, prompt_path=prompt_path)

def main():
    # Start overall timer
    overall_start_time = time.time()

    parser = argparse.ArgumentParser(description="Run bug scanner with auditors, critic, ranker, and data folder")

    parser.add_argument('-a', '--auditors', nargs='+', required=True, help='One or more auditor model IDs')
    parser.add_argument('-c', '--critic', help='Optional critic model ID (only one allowed)')
    parser.add_argument('-r', '--ranker', help='Optional ranker model ID (only one allowed)')
    parser.add_argument('-d', '--data_folder', required=True, help='Path to the data folder')
    parser.add_argument('-o', '--output_folder', required=True, help='Output results folder')
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

    logging.info("Initializing BugScanner with the given models...")
    detector = BugScanner(
        auditor_models=auditor_models,
        critic_model=critic_model,
        ranker_model=ranker_model
    )
    logging.info("BugScanner initialization completed.")

    # List all files in the data folder
    data_files = [f for f in os.listdir(args.data_folder) if f.endswith('.sol')]
    logging.info(f"Found {len(data_files)} .sol files in the folder: {args.data_folder}")

    # Before the data processing loop
    logging.info(f"Starting the bug scanning pipeline with Top-K = {args.topk}...")
    logging.info("Processing files one by one...\n")

    # Process each file
    for data in data_files:
        file_start_time = time.time()  # Start timing for each file

        data_path = os.path.join(args.data_folder, data)
        name = data.split('/')[-1].rsplit('.', 1)[0]
        output_name = f"{name}_k{args.topk}_n{len(auditor_models)}"
        output_dir = os.path.join(args.output_folder, output_name)

        # Detailed log before processing each file
        logging.info(f"Now running bug scanner for: {data}")
        logging.info(f"Full file path: {data_path}")
        logging.info(f"Output will be saved in: {output_dir}")

        # Ensure the output directory exists
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            logging.info(f"Created output directory: {output_dir}")

        # Run the bug scanner pipeline
        detector.run_pipeline(
            code_path=data_path,
            topk=args.topk,
            output=output_name,
            result_dir=args.output_folder
        )

        # Log completion of each file and timing
        file_time_taken = time.time() - file_start_time
        logging.info(f"Finished processing: {data} in {file_time_taken:.2f} seconds.")
        logging.info(f"Results saved in: {output_dir}")

    # Log final completion and overall time
    overall_time_taken = time.time() - overall_start_time
    logging.info(f"Bug scanning pipeline completed for all files in {overall_time_taken:.2f} seconds.")

if __name__ == '__main__':
    main()
