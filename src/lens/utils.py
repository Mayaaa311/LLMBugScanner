import json
import os

param1 = {
    "max_new_tokens": 5000,
    "do_sample": True,
    "temperature": 0.001,
    "top_k": 50,
    "top_p": 0.95,
    "num_return_sequences": 1
}
param2 = {
    "max_new_tokens": 8000,
    "do_sample": False
}

auditor_prompt = {
    "messages": [
        {
            "role": "system",
            "content": "You are a smart contract auditor. Identify and explain {topk} most severe vulnerabilities in the provided smart contract. Ensure that the vulnerabilities are exploitable in the real world and beneficial to attackers. For each identified vulnerability, provide intermediate reasoning and specify the associated function. Include the entire function code without using '...'. Your reasoning should be comprehensive and detailed.\n\nFormat Requirement:\n\nYou should ONLY output in the following JSON format:\n{\n    \"output_list\": [\n        {\n            \"function_name\": \"<function_name_1>\",\n            \"code\": \"<code of the function1>\",\n            \"vulnerability\": \"<short_vulnera_desc_1>\",\n            \"reason\": \"<reason_1>\"\n        },\n        {\n            \"function_name\": \"<function_name_2>\",\n            \"code\": \"<code of the function2>\",\n            \"vulnerability\": \"<short_vulnera_desc_2>\",\n            \"reason\": \"<reason_2>\"\n        }\n    ]\n}\n\nNote: If no vulnerability is detected, you should output an empty JSON: {\"output_list\": []}."
        },
        {
            "role": "user",
            "content": "Smart contract code:\n\n{code}"
        },
        {
            "role": "assistant",
            "content": ""
        }
    ]
}


critic_prompt = {
    "messages": [
        {
            "role": "system",
            "content": "You are provided with a JSON object that contains a list of functions and associated vulnerabilities in a smart contract. I need you to extract this information and format it as a CSV. The CSV should have three columns and no repeating rows. Please only give the CSV file data without any other content:\n\ndataname - {dataname}\nvulnerability - Extract the vulnerability name\nfunction_name - Extract the function name."
        },
        {
            "role": "user",
            "content": "Here is the JSON data:\n\n{inputjson}"
        },
        {
            "role": "assistant",
            "content": ""
        }
    ]
}



final_formatter = {
    "messages": [
        {
            "role": "system",
            "content": "You are provided with a JSON object that contains a list of functions and associated vulnerabilities in a smart contract. I need you to extract this information and format it as a CSV. The CSV should have three columns and no repeating rows. Please only give the CSV file data without any other content:\n\ndataname - {dataname}\nvulnerability - Extract the vulnerability name\nfunction_name - Extract the function name."
        },
        {
            "role": "user",
            "content": "Here is the JSON data:\n\n{inputjson}"
        },
        {
            "role": "assistant",
            "content": ""
        }
    ]
}


summarizer1 = {
    "messages": [
        {
            "role": "system",
            "content": "Given an input, convert it into a structured JSON format output. Do not output anything other than the JSON.\n\nFormat:\n{\n    \"output_list\": [\n        {\n            \"function_name\": \"<function_name_1>\",\n            \"code\": \"<code of the function1>\",\n            \"vulnerability\": \"<short_vulnera_desc_1>\",\n            \"reason\": \"<reason_1>\"\n        },\n        {\n            \"function_name\": \"<function_name_2>\",\n            \"code\": \"<code of the function2>\",\n            \"vulnerability\": \"<short_vulnera_desc_2>\",\n            \"reason\": \"<reason_2>\"\n        }\n    ]\n}"
        },
        {
            "role": "user",
            "content": "Input: {content}"
        },
        {
            "role": "assistant",
            "content": ""
        }
    ]
}

summarizer2 = {
    "messages": [
        {
            "role": "system",
            "content": "Given an input, convert it into a structured JSON format output. Do not output anything other than the JSON.\n\nFormat:\n{\n    \"output_list\": [\n        {\n            \"function_name\": \"<function_name_1>\",\n            \"vulnerability\": \"<short_vulnera_desc_1>\",\n            \"criticism\": \"<criticism for reasoning and explanation for scoring>\",\n            \"correctness\": <0~9>,\n            \"severity\": <0~9>,\n            \"profitability\": <0~9>\n        },\n        {\n            \"function_name\": \"<function_name_2>\",\n            \"vulnerability\": \"<short_vulnera_desc_2>\",\n            \"criticism\": \"<criticism for reasoning and explanation for scoring>\",\n            \"correctness\": <0~9>,\n            \"severity\": <0~9>,\n            \"profitability\": <0~9>\n        }\n    ]\n}"
        },
        {
            "role": "user",
            "content": "Input: {content}"
        },
        {
            "role": "assistant",
            "content": ""
        }
    ]
}
ranker_prompt = {
    "messages": [
        {
            "role": "system",
            "content": "Given an input JSON, sort the vulnerabilities based on severity and output the top {topk} most severe vulnerabilities in a JSON format. Do not output anything other than the JSON.\n\nInput JSON:\n{vulnerability}"
        },
        {
            "role": "assistant",
            "content": ""
        }
    ]
}



def write_to_file(file_path, content, write='w'):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    try:
        # Try to serialize content to JSON
        json_content = json.dumps(content, indent=4)
        with open(file_path, write) as file:
            file.write(json_content)
    except (TypeError, ValueError):
        # Fallback to writing the content as is if JSON serialization fails
        with open(file_path, write) as file:
            file.write(content)




def read_file_to(file_paths):
    outputs = []
    for i in file_paths:
        with open(i, 'r') as file:
            o = file.read()
            outputs.append(o)
            print("file: ",i)
            print(o)
    # print(outputs)
    return str(outputs)


def parse_config(cfg_path, model_id):
    # Load the JSON file
    with open(cfg_path, 'r') as file:
        config = json.load(file)
    
    # Choose the section based on the model
    model_params = config.get(model_id)
    
    # Convert parameter values to appropriate types if necessary
    for key in model_params:
        if isinstance(model_params[key], str):
            if model_params[key].isdigit():
                model_params[key] = int(model_params[key])
            else:
                try:
                    model_params[key] = float(model_params[key])
                except ValueError:
                    pass  # Leave it as a string if it can't be converted
    return model_params


import json
import subprocess
import os
import solcx
import re


def get_required_solc_version(solidity_file):
    """
    Reads the Solidity file and extracts the required compiler version from the pragma statement.
    If the version is below 0.4.11, default to 0.4.11 (the minimum supported version by py-solc-x).
    """
    with open(solidity_file, 'r') as file:
        content = file.read()
        match = re.search(r"pragma solidity \^?(\d+\.\d+\.\d+);", content)
        if match:
            version = match.group(1)
            # Check if the version is below 0.4.11
            if version < "0.4.11":
                print(f"Version {version} is not supported; defaulting to 0.4.11.")
                return "0.4.11"
            return version
    return None

def generate_solidity_ast(solidity_file, output_file="ast.json"):
    """
    Generate an AST in JSON format for the given Solidity file using solcx, with the required compiler version.
    """
    # Get the required Solidity version from the pragma statement
    required_version = get_required_solc_version(solidity_file)
    if required_version is None:
        print("Could not determine the Solidity version from the pragma statement.")
        return
    
    # Ensure the required version of solc is installed
    solcx.install_solc(required_version)
    solcx.set_solc_version(required_version)
    
    # Compile Solidity file to get AST
    try:
        ast_json = solcx.compile_files(
            [solidity_file],
            output_values=["ast"]
        )

        # Write the AST JSON output to a file
        with open(output_file, "w") as file:
            json.dump(ast_json, file)
        
        print(f"AST successfully generated and saved to {output_file}")
    except solcx.exceptions.SolcError as e:
        print("Error generating AST:", e)
        raise


def load_solidity_ast(filename):
    """
    Load the generated AST JSON file into a Python dictionary.
    """
    with open(filename, 'r') as file:
        ast_data = json.load(file)
    return ast_data

def get_function_definitions(ast_data):
    """
    Extract function definitions from the Solidity AST.
    """
    functions = {}
    print(json.dumps(ast_data, indent=2))
    def traverse(node):
        # Check if the current node is a function definition
        if node.get("name") == "FunctionDefinition":
            func_name = node.get("attributes", {}).get("name")
            if func_name:
                functions[func_name] = node
                print(f"Found function: {func_name}")
        
        # Traverse children recursively
        for child in node.get("children", []):
            traverse(child)
    
    # Start traversing from each top-level child in "children"
    if "children" in ast_data:
        for top_node in ast_data["children"]:
            # Handle cases where a node has multiple layers of "children" within itself
            if "children" in top_node:
                for sub_node in top_node["children"]:
                    traverse(sub_node)
            else:
                traverse(top_node)
    else:
        print("Error: No 'children' key found in AST data.")
    
    return functions

def get_called_functions(func_node):
    """
    Extract called functions from a function definition node in the AST.
    """
    calls = set()
    
    def traverse(node):
        if node.get("name") == "FunctionCall":
            func_name = node.get("attributes", {}).get("value") or node.get("attributes", {}).get("name")
            print("FUNCTION NAME: ",func_name)
            if func_name:
                calls.add(func_name)
        for child in node.get("children", []):
            traverse(child)
    
    traverse(func_node)
    return calls

def find_related_functions(solidity_file, target_function_name):
    """
    Generate AST, load it, and find the target function and all related functions in the Solidity code.
    """
    # Generate AST file from Solidity code
    ast_file = "ast.json"
    generate_solidity_ast(solidity_file, ast_file)
    
    # Load the AST data
    ast_data = load_solidity_ast(ast_file)
    functions = get_function_definitions(ast_data)
    
    if target_function_name not in functions:
        print(target_function_name)
        raise ValueError(f"Function '{target_function_name}' not found in the provided code.")
    
    # Get related functions by analyzing function calls within the target function
    related_function_names = get_called_functions(functions[target_function_name])
    
    # Include the target function in the output
    related_functions = {target_function_name: functions[target_function_name]}
    
    # Add all related functions to the output
    for func_name in related_function_names:
        if func_name in functions:
            related_functions[func_name] = functions[func_name]
    
    return related_functions

