import json
import os


def write_to_file(file_path, content, write='w'):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write the content to the file
    with open(file_path, write) as file:
        file.write(content)


def read_file_to(file_paths):
    outputs = []
    with open(file_paths, 'r') as file:
        o = json.load(file)
        outputs.append(outputs)
    return str(outputs)


def parse_config(cfg_path, model_id):
    # Load the JSON file
    with open(cfg_path, 'r') as file:
        config = json.load(file)
    
    # Choose the section based on the model
    model_params = config.get(model_id, config.get('llama3', {}))
    
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
