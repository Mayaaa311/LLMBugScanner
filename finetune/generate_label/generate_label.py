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
eval_dataset = load_dataset("json", data_files="/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/FineTuning_dataset/fine_tuning_data.jsonl", split="train")
rand_idx = randint(0, len(eval_dataset))


# Open a file in write mode to store all outputs
with open("/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/FineTuning_dataset/new_label_dataset.txt", "w") as file:
    for sample in eval_dataset:
        # Apply the template to the first 3 messages of each sample
        prompt = pipe.tokenizer.apply_chat_template(sample["messages"][:3], tokenize=False, add_generation_prompt=True)
          # Use text generation to continue from the assistant's last output
        generated_output = pipe(prompt, max_new_tokens=1000, do_sample=True, top_k=50)
              
        # Write the output to the file
        file.write(f"{generated_output}\n")  # Separate each output with a newline for clarity


