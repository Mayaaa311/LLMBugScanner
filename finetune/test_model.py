import torch
from peft import AutoPeftModelForCausalLM
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from nltk.translate.bleu_score import sentence_bleu
from trl import setup_chat_format
from datasets import load_dataset
from random import randint
import sys
 
# peft_model_id = "model/Nxcode_finetuned/checkpoint-11/"
# peft_model_id = "NTQAI/Nxcode-CQ-7B-orpo"
# peft_model_id = "AlfredPros/CodeLlama-7b-Instruct-Solidity"
# peft_model_id = args.output_dir

peft_model_id = sys.argv[1]
finetuned = float(sys.argv[2])
dataset_file = sys.argv[3]
#peft_config = LoraConfig(
#        lora_alpha=128,
#        lora_dropout=0.05,
#        r=256,
#        bias="none",
#        target_modules="all-linear",
#        task_type="CAUSAL_LM",
#)

# Load Model with PEFT adapter - Use this for pre-trained models
if finetuned == 1.0:
    model = AutoPeftModelForCausalLM.from_pretrained(
        peft_model_id,
        device_map="auto",
        torch_dtype=torch.float16,
        trust_remote_code=True
    )
else:
    model = AutoModelForCausalLM.from_pretrained(peft_model_id,  device_map="auto",  torch_dtype=torch.float16, trust_remote_code=True)

tokenizer = AutoTokenizer.from_pretrained(peft_model_id)
model, tokenizer = setup_chat_format(model, tokenizer)

# load into pipeline
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

 
# Load our test dataset
eval_dataset = load_dataset("json", data_files=dataset_file, split="train")
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

def evaluate_acc(sample, predicted_answer):
    func_correct = 0.0
    vul_correct = 0.0
    sample = sample["messages"][2]["content"]
    vul_start_loc = sample.find("type") + 6
    vul_end_loc = sample.find(" in ") - 1
    func_start_loc = sample.find("function") + 10
    func_end_loc = sample.find(".") - 1
    vul = sample[vul_start_loc:vul_end_loc]
    func = sample[func_start_loc:func_end_loc]
    if predicted_answer.find(vul) > 0:
        vul_correct = 1.0
    if predicted_answer.find(func) > 0:
        func_correct = 1.0

    print("Vul", vul, "Func", func)
    return func_correct, vul_correct
    
 
bleu_scores = []
func_accs = []
vul_accs = []
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
    func_acc, vul_acc = evaluate_acc(sample, predicted_answer)
    evaluate_acc(sample, predicted_answer)
    func_accs.append(func_acc)
    vul_accs.append(vul_acc)
    bleu_scores.append(bleu_score)
 
# Compute average BLEU score
average_bleu_score = sum(bleu_scores) / len(bleu_scores)
average_func_score = sum(func_accs) / len(func_accs)
average_vul_score = sum(vul_accs) / len(vul_accs)
 
print(f"Average BLEU Score: {average_bleu_score * 100:.2f}%")
print(f"Average Function Accuracy: %.2f" % (average_func_score * 100))
print(f"Average Vulnerability Accuracy: %.2f" % (average_vul_score * 100))
