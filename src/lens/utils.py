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
