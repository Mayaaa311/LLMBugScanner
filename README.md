# GPTLens-2.0

## Overview

GPTLens-2.0 is an advanced tool designed to enhance the functionalities of GPTLens by automating the process of identifying and evaluating potential vulnerabilities in code. It provides more flexibility by allowing the use of different Large Language Model (LLM) agents. The tool is equipped with an auditor and a critic, which work together to find and rank vulnerabilities based on correctness and severity.

## Features

- **Automated Vulnerability Detection**: Automatically identifies potential vulnerabilities in code.
- **Flexible LLM Agents**: Supports various LLM agents for auditing and critique.
- **Enhanced Accuracy**: Ranks vulnerabilities based on correctness and severity scores.
- **User-Friendly**: Easy to configure and extend.

## Setup

Follow these steps to set up the virtual environment, install dependencies, and run the example.

### 1. Clone the Repository

```sh
git clone https://github.com/Mayaaa311/GPTLens-2.0.git
cd GPTLens-2.0
```
### 2. Set Up Virtual Environment
Create and activate a virtual environment to manage dependencies.

```sh
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```


### 5. Run the Example

```sh
python src/bugscanner_cli.py -a NTQAI/Nxcode-CQ-7B-orpo  -c m-a-p/OpenCodeInterpreter-DS-6.7B -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_test_pipe -k 5 -log logs_nov3
```

### 6. to resume a run
```
python src/bugscanner_cli.py -a NTQAI/Nxcode-CQ-7B-orpo  -c NTQAI/Nxcode-CQ-7B-orpo -r NTQAI/Nxcode-CQ-7B-orpo -d data_full/CVE_clean_organized -o result -k 5 -log logger/log_nxcode -res result_nxcodes_k3_beforeft/k3_n1_2024-11-11_19-21-40
```
### if running +10 data, recomend using run_batch folder's method

## Currently Tested Model: 
| AlfredPros/CodeLlama-7b-Instruct-Solidity   | Huggingface_LLM | https://huggingface.co/AlfredPros/CodeLlama-7b-Instruct-Solidity   | 7B   |
|---------------------------------------------|-----------------|--------------------------------------------------------------------|------|
| m-a-p/OpenCodeInterpreter-DS-6.7B           | Huggingface_LLM | https://huggingface.co/m-a-p/OpenCodeInterpreter-DS-6.7B           | 6.7B |
| NTQAI/Nxcode-CQ-7B-orpo                     | Huggingface_LLM | https://huggingface.co/NTQAI/Nxcode-CQ-7B-orpo                     | 7B   |
| Artigenz/Artigenz-Coder-DS-6.7B             | Huggingface_LLM | https://huggingface.co/Artigenz/Artigenz-Coder-DS-6.7B             | 6.7B |
| bigcode/starcoders2-15b                     | Huggingface_LLM | https://huggingface.co/bigcode/starcoders2-15b                     | 15B  |
| deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct | Huggingface_LLM | https://huggingface.co/deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct | 16B  |
| Qwen/CodeQwen1.5-7B                         | pipeline_LLM    | https://huggingface.co/Qwen/CodeQwen1.5-7B                         | 7B   |
| meta-llama/Llama-3.1-8B-Instruct            | pipeline_LLM    | https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct            | 8B   |
| meta-llama/CodeLlama-7b-hf                  | pipeline_LLM    | https://huggingface.co/meta-llama/CodeLlama-7b-hf                  | 7B   |
| WisdomShell/CodeShell-7B-Chat               | Huggingface_LLM | https://huggingface.co/WisdomShell/CodeShell-7B-Chat               | 7B   |
| THUDM/codegeex2-6b                          | Huggingface_LLM | https://huggingface.co/THUDM/codegeex2-6b                          | 6B   |
| google/codegemma-7b                         | gemma_LLM       | https://huggingface.co/google/codegemma-7b                         | 7B   |

## Example Creating Model objects


## Commands for testing
salloc --ntasks-per-node=60 --gpus=7
module load anaconda3/2023.03
conda activate /home/hice1/yyuan394/scratch/env

python src/bugscanner_cli.py -a  AlfredPros/CodeLlama-7b-Instruct-Solidity -c m-a-p/OpenCodeInterpreter-DS-6.7B -r m-a-p/OpenCodeInterpreter-DS-6.7B -p m-a-p/OpenCodeInterpreter-DS-6.7B -d data_2 -o result_test_parser/trail3 -k 5 -log logs_oct1

### multiple auditors
python src/bugscanner_cli.py -a AlfredPros/CodeLlama-7b-Instruct-Solidity m-a-p/OpenCodeInterpreter-DS-6.7B NTQAI/Nxcode-CQ-7B-orpo -c m-a-p/OpenCodeInterpreter-DS-6.7B -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_test_parser -k 5 -log logs_oct1

### single auditor(currently testing on)
python src/bugscanner_cli.py -a NTQAI/Nxcode-CQ-7B-orpo  -c m-a-p/OpenCodeInterpreter-DS-6.7B -r NTQAI/Nxcode-CQ-7B-orpo -d data -o result_test_pipe -k 5 -log logs_nov3


 <!-- m-a-p/OpenCodeInterpreter-DS-6.7B NTQAI/Nxcode-CQ-7B-orpo  -->