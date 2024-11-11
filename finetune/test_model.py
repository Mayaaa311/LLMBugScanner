import torch
from peft import AutoPeftModelForCausalLM
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from nltk.translate.bleu_score import sentence_bleu
from datasets import load_dataset
from random import randint
 
# peft_model_id = "/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/model/Nxcode_finetuned"
peft_model_id = "NTQAI/Nxcode-CQ-7B-orpo"
# peft_model_id = args.output_dir
 
# Load Model with PEFT adapter
# model = AutoPeftModelForCausalLM.from_pretrained(
#   peft_model_id,
#   device_map="auto",
#   torch_dtype=torch.float16
# )

model = AutoModelForCausalLM.from_pretrained(peft_model_id,  device_map="auto",  torch_dtype=torch.float16)
tokenizer = AutoTokenizer.from_pretrained(peft_model_id)
# load into pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

 
# Load our test dataset
eval_dataset = load_dataset("jsonl", data_files="/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/FineTuning_dataset/fine_tuning_data.jsonl", split="train")
rand_idx = randint(0, len(eval_dataset))
 
# Test on sample
prompt = pipe.tokenizer.apply_chat_template(eval_dataset[rand_idx]["messages"][:3], tokenize=False, add_generation_prompt=True)
outputs = pipe(prompt, max_new_tokens=256, do_sample=False, temperature=0.1, top_k=50, top_p=0.1, eos_token_id=pipe.tokenizer.eos_token_id, pad_token_id=pipe.tokenizer.pad_token_id)
 

print(f"Query:\n{eval_dataset[rand_idx]['messages'][1]['content']}")
print(f"Original Answer:\n{eval_dataset[rand_idx]['messages'][2]['content']}")
print(f"Generated Answer:\n{outputs[0]['generated_text'][len(prompt):].strip()}")


from tqdm import tqdm
 

def evaluate_bleu(sample, predicted_answer):
    reference = [sample["messages"][2]["content"].split()]
    candidate = predicted_answer.split()
    bleu_score = sentence_bleu(reference, candidate)
    return bleu_score
 
bleu_scores = []
number_of_eval_samples = len(eval_dataset)
print("Number of samples in test set:", number_of_eval_samples)

# Iterate over eval dataset and predict
for sample in tqdm(eval_dataset.shuffle().select(range(number_of_eval_samples))):
    # Prepare prompt for prediction
    prompt = pipe.tokenizer.apply_chat_template(sample["messages"][:2], tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=False, temperature=0.1, top_k=50, top_p=0.1, eos_token_id=pipe.tokenizer.eos_token_id, pad_token_id=pipe.tokenizer.pad_token_id)
    predicted_answer = outputs[0]['generated_text'][len(prompt):].strip()
    
    # Evaluate BLEU score
    bleu_score = evaluate_bleu(sample, predicted_answer)
    bleu_scores.append(bleu_score)
 
# Compute average BLEU score
average_bleu_score = sum(bleu_scores) / len(bleu_scores)
 
print(f"Average BLEU Score: {average_bleu_score * 100:.2f}%")