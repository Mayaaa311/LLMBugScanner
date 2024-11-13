# Possible improvements: handling cases when there are multiple bugs, having label that includes the code section, like in the labels
# also need to do some sort of train-test split

import csv
import json
import os

# dataset_file = open("train_data/train.csv", 'a', newline='')
dataset = []

# read in the labels
label_file = open("../data_full/CVE_label/CVElabel3_full.json")
label_data = json.load(label_file)
label_file.close()

# read in the descriptions
desc_file = open("../data_full/CVE_label/CVE2description.json")
desc_data = json.load(desc_file)
desc_file.close()

# read in the prompt
prompt_file = open("../templates/auditor_v1.txt")
prompt = prompt_file.read()
prompt_file.close()

# iterate over the items (leave out testing set)
for i, cve_file in enumerate(os.listdir("../data_full/CVE/")):
    proper_cve_name = "CVE-" + cve_file[:-4]
    
    # initialize text in format required by AutoTrain
    this_text = [{"content":"", "role":"user"}, {"content":"", "role":"assistant"}]
    
    # read in the solidity file
    code_file = open("../data_full/CVE/"+cve_file)
    code = code_file.read()
    code_file.close()
    
    # put the code from this contract into the prompt
    formatted_prompt = prompt.replace("{code}", code).replace("\"", '\'')
    this_text[0]["content"] = formatted_prompt
    
    # now format the correct response. If there are multiple bugs, just keep the first one
    try:
        resp = {
            'function_name':label_data[proper_cve_name]["vulnerable_function_name"].replace("\"", '\''),
            'vulnerability':label_data[proper_cve_name]["vulnerability_type"].replace("\"", '\''),
            'reason':desc_data[proper_cve_name].replace("\"", '\''),
        }
    except:
        print(f"Skipped ({i})", proper_cve_name)
        i -= 1
        continue
    this_text[1]["content"] = resp
    print(f"Processed ({i})", proper_cve_name)
    
    dataset.append(this_text)
    
# # write everything to the csv
# fieldnames = ["text"]
# writer = csv.DictWriter(dataset_file, fieldnames=fieldnames)
# writer.writeheader()
# writer.writerows(dataset)
# dataset_file.close()

jsonl_file = open("train_data/train.jsonl", 'w')
for item in dataset:
    json.dump({"text":item}, jsonl_file)
    jsonl_file.write('\n')
    