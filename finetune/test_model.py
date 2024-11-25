import torch
from peft import AutoPeftModelForCausalLM
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from nltk.translate.bleu_score import sentence_bleu
from datasets import load_dataset
from random import randint

from safetensors.torch import load_file
from safetensors.torch import save_file
adapter_path = 'finetune/model/final_models/gemma_messi_5ep_CVE_10ep/adapter_model.safetensors'
# adapter_path = "finetune/model/final_models/codellama_CVE_10ep/adapter_model.safetensors"  # Replace with the actual path
state_dict = load_file(adapter_path)

# Inspect the keys and their shapes
for key, tensor in state_dict.items():
    print(f"{key}: {tensor.shape}")


# Keys to truncate
embed_tokens_key = "base_model.model.model.embed_tokens.weight"
lm_head_key = "base_model.model.lm_head.weight"

# Target shapes
target_shape = (32016, 4096)

# Truncate embed_tokens.weight
if embed_tokens_key in state_dict:
    print(f"Original shape of {embed_tokens_key}: {state_dict[embed_tokens_key].shape}")
    state_dict[embed_tokens_key] = state_dict[embed_tokens_key][:target_shape[0], :]
    print(f"Adjusted shape of {embed_tokens_key}: {state_dict[embed_tokens_key].shape}")

# Truncate lm_head.weight
if lm_head_key in state_dict:
    print(f"Original shape of {lm_head_key}: {state_dict[lm_head_key].shape}")
    state_dict[lm_head_key] = state_dict[lm_head_key][:target_shape[0], :]
    print(f"Adjusted shape of {lm_head_key}: {state_dict[lm_head_key].shape}")

# Save the modified state_dict to a new safetensors file

print(f"Modified checkpoint saved to {adapter_path}")
save_file(state_dict, adapter_path)

# from peft import PeftModel

# from safetensors.torch import load_file, save_file
# import torch

# # Load adapter checkpoint
# checkpoint_path = "finetune/model/final_models/codellama_CVE_10ep/adapter_model.safetensors"
# state_dict = load_file(checkpoint_path)

# # Expected shapes
# target_vocab_size = 32016  # Update this to your model's vocab size
# hidden_size = 4096  # Typically matches the embedding size

# # Truncate weights
# state_dict["base_model.model.model.embed_tokens.weight"] = state_dict["base_model.model.model.embed_tokens.weight"][:target_vocab_size, :]
# state_dict["base_model.model.lm_head.weight"] = state_dict["base_model.model.lm_head.weight"][:target_vocab_size, :]

# # Save the modified checkpoint
# save_file(state_dict, "finetune/model/final_models/adapter_model_fixed.safetensors")



# # peft_model_id = "/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/model/Nxcode_finetuned"
# model_id ='AlfredPros/CodeLlama-7b-Instruct-Solidity'
# adapter_model_path = "finetune/model/final_models/codellama_CVE_10ep"


# model = AutoModelForCausalLM.from_pretrained(model_id,  device_map="auto",  torch_dtype=torch.float16)
# tokenizer = AutoTokenizer.from_pretrained(model_id)


# model = PeftModel.from_pretrained(model, adapter_model_path, is_trainable=False, merge_adapter=True)

# messages = [
#     {"role": "user", "content": "whats your name"}
# ]
# inputs = tokenizer("whats your name",return_tensors="pt").input_ids


# outputs = model.generate(inputs)

# print("loaded! ")
# # # load into pipeline
# # pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

 
# # # Load our test dataset
# # eval_dataset = load_dataset("json", data_files="finetune/FineTuning_dataset/gptlens_dataset/fine_tuning_data.jsonl", split="train")
# # rand_idx = randint(0, len(eval_dataset))
 
# # # Test on sample
# # prompt = pipe.tokenizer.apply_chat_template(eval_dataset[rand_idx]["messages"][:3], tokenize=False, add_generation_prompt=True)
# # outputs = pipe(prompt, max_new_tokens=256, do_sample=False, temperature=0.1, top_k=50, top_p=0.1, eos_token_id=pipe.tokenizer.eos_token_id, pad_token_id=pipe.tokenizer.pad_token_id)
 

# # print(f"Query:\n{eval_dataset[rand_idx]['messages'][1]['content']}")
# # print(f"Original Answer:\n{eval_dataset[rand_idx]['messages'][2]['content']}")
# # print(f"Generated Answer:\n{outputs[0]['generated_text'][len(prompt):].strip()}")


# # # from tqdm import tqdm
 

# # # def evaluate_bleu(sample, predicted_answer):
# # #     reference = [sample["messages"][2]["content"].split()]
# # #     candidate = predicted_answer.split()
# # #     bleu_score = sentence_bleu(reference, candidate)
# # #     return bleu_score
 
# # # bleu_scores = []
# # # number_of_eval_samples = len(eval_dataset)
# # # print("Number of samples in test set:", number_of_eval_samples)

# # # # Iterate over eval dataset and predict
# # # for sample in tqdm(eval_dataset.shuffle().select(range(number_of_eval_samples))):
# # #     # Prepare prompt for prediction
# # #     prompt = pipe.tokenizer.apply_chat_template(sample["messages"][:2], tokenize=False, add_generation_prompt=True)
# # #     outputs = pipe(prompt, max_new_tokens=256, do_sample=False, temperature=0.1, top_k=50, top_p=0.1, eos_token_id=pipe.tokenizer.eos_token_id, pad_token_id=pipe.tokenizer.pad_token_id)
# # #     predicted_answer = outputs[0]['generated_text'][len(prompt):].strip()
    
# # #     # Evaluate BLEU score
# # #     bleu_score = evaluate_bleu(sample, predicted_answer)
# # #     bleu_scores.append(bleu_score)
 
# # # # Compute average BLEU score
# # # average_bleu_score = sum(bleu_scores) / len(bleu_scores)
 
# # # print(f"Average BLEU Score: {average_bleu_score * 100:.2f}%")