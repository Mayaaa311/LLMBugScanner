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
