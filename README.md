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

### 4. install models 

Follow instruction here to install Ollama models: https://github.com/ollama/ollama 

### 5. Run the Example

```sh
python src/main.py
```


## Currently Supported Models: 

| Model Id                                | Model Class Name | Model source                                                     | model size |
|-------------------------------------------|------------------|------------------------------------------------------------------|------------|
| Llama 3                                   | ChatOllamaLLM    | https://ollama.com/library/llama3                                | 8B         |
| codellama base                            | ChatOllamaLLM    | https://ollama.com/library/codellama                             | 7B         |
| AlfredPros/CodeLlama-7b-Instruct-Solidity | Huggingface_LLM  | https://huggingface.co/AlfredPros/CodeLlama-7b-Instruct-Solidity | 7B         |
| codeqwen                                  | ChatOllamaLLM    | https://ollama.com/library/codeqwen                              | 7B         |
| deepseek-coder-v2                         | ChatOllamaLLM    | https://ollama.com/library/deepseek-coder-v2                     | 16B        |
| starcoder2                                | ChatOllamaLLM    | https://ollama.com/library/starcoder2:7b                         | 15B        |
| bartowski/Nxcode-CQ-7B-orpo-GGUF          | LlamaCpp_LLM     | https://huggingface.co/bartowski/Nxcode-CQ-7B-orpo-GGUF          | 7b         |


## Example Creating Model objects

ChatOllamaLLM(model_id="deepseek-coder-v2",model_params_path="config/temp0.json"),
ChatOllamaLLM(model_id="codeqwen",model_params_path="config/temp0.json"),
ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.json"),
ChatOllamaLLM(model_id="codellama",model_params_path="config/temp0.json"),
ChatOllamaLLM(model_id="starcoder2",model_params_path="config/temp0.json"),
Huggingface_LLM(model_id="AlfredPros/CodeLlama-7b-Instruct-Solidity", model_params_path = "config/temp0.json")
LlamaCpp_LLM(model_id="bartowski/Nxcode-CQ-7B-orpo-GGUF", model_path="Nxcode-CQ-7B-orpo-IQ1_M.gguf",model_params_path="config/temp0.json")

salloc --ntasks-per-node=60 --gpus=7
module load anaconda3/2023.03
conda activate /home/hice1/yyuan394/scratch/env
python3 src/main.py