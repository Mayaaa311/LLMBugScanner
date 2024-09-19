from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM
import torch
import accelerate

use_4bit = True
bnb_4bit_compute_dtype = "float16"
bnb_4bit_quant_type = "nf4"
use_double_nested_quant = True
compute_dtype = getattr(torch, bnb_4bit_compute_dtype)

# BitsAndBytesConfig 4-bit config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=use_4bit,
    bnb_4bit_use_double_quant=use_double_nested_quant,
    bnb_4bit_quant_type=bnb_4bit_quant_type,
    bnb_4bit_compute_dtype=compute_dtype,
    load_in_8bit_fp32_cpu_offload=True
)

# Load model in 4-bit
tokenizer = AutoTokenizer.from_pretrained("AlfredPros/CodeLlama-7b-Instruct-Solidity")
model = AutoModelForCausalLM.from_pretrained("AlfredPros/CodeLlama-7b-Instruct-Solidity", quantization_config=bnb_config, device_map="balanced_low_0")

# Make input
input='Make a smart contract to create a whitelist of approved wallets. The purpose of this contract is to allow the DAO (Decentralized Autonomous Organization) to approve or revoke certain wallets, and also set a checker address for additional validation if needed. The current owner address can be changed by the current owner.'

# Make prompt template
prompt = f"""### Instruction:
Use the Task below and the Input given to write the Response, which is a programming code that can solve the following Task:

### Task:
{input}

### Solution:
"""

# Tokenize the input
input_ids = tokenizer(prompt, return_tensors="pt", truncation=True).input_ids.cuda()
# Run the model to infere an output
outputs = model.generate(input_ids=input_ids, max_new_tokens=1024, do_sample=True, top_p=0.9, temperature=0.001, pad_token_id=1)

# Detokenize and display the generated output
print(tokenizer.batch_decode(outputs.detach().cpu().numpy(), skip_special_tokens=True)[0][len(prompt):])
