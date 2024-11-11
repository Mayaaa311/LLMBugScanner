import torch
from peft import AutoPeftModelForCausalLM
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from datasets import load_dataset
from random import randint

# Define the PEFT model ID
peft_model_id = "NTQAI/Nxcode-CQ-7B-orpo"

# Load Model with PEFT adapter
model = AutoModelForCausalLM.from_pretrained(
    peft_model_id,
    device_map="auto",
    torch_dtype=torch.float16
)
tokenizer = AutoTokenizer.from_pretrained(peft_model_id)

# Load pipeline for text generation
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer)

# Load the test dataset
eval_dataset = load_dataset("json", data_files="/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/FineTuning_dataset/fine_tuning_data.jsonl", split="train")

# Open a file in write mode to store all outputs
with open("/home/hice1/yyuan394/scratch/LLMBugScanner/finetune/FineTuning_dataset/new_label_dataset.txt", "w") as file:
    for sample in eval_dataset:
        # # Apply the template directly to messages
        # messages = [message["text"] for message in sample["messages"][:3] if "text" in message]
        # prompt = "\n".join(messages)  # Join messages as a prompt
        
        # # Generate text based on the prompt
        # generated_output = pipe(prompt, max_new_tokens=1000, do_sample=True, top_k=50)
        
        # Write the generated output to the file
        # file.write(f"{generated_output[0]['generated_text']}\n\n")  # Adding newline for clarity
        # Apply the template to the first 3 messages of each sample
        prompt = pipe.tokenizer.apply_chat_template(sample["messages"][:3], tokenize=False, add_generation_prompt=True)
          # Use text generation to continue from the assistant's last output
        generated_output = pipe(prompt, max_new_tokens=5000, do_sample=True, top_k=50)
          # Write the generated output to the file

        if generated_output and "generated_text" in generated_output[0]:
            file.write(f"{generated_output[0]['generated_text']}\n\n")  # Adding newline for clarity
        else:
            file.write("Error: No generated text\n\n")            
        # Write the output to the file
        # file.write(f"{generated_output}\n")  # Separate each output with a newline for clarity