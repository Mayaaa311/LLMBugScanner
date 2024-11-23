import torch
from peft import AutoPeftModelForCausalLM, get_peft_model
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from trl import setup_chat_format
from datasets import Dataset, load_dataset
import sys

dataset_file1 = sys.argv[4]
try:
    dataset_file2 = sys.argv[5]
except:
    dataset_file2 = None

dataset = load_dataset("json", data_files=dataset_file1, split="train")
if dataset_file2:
    dataset2 = load_dataset("json", data_files=dataset_file2, split="train")
model_id = sys.argv[1]
finetune = float(sys.argv[3])

# Hugging Face model id
# model_id =  "Artigenz/Artigenz-Coder-DS-6.7B" # or `mistralai/Mistral-7B-v0.1`
# model_id = "NTQAI/Nxcode-CQ-7B-orpo" 
# model_id = "AlfredPros/CodeLlama-7b-Instruct-Solidit

# BitsAndBytesConfig int-4 config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True, bnb_4bit_use_double_quant=True, bnb_4bit_quant_type="nf4", bnb_4bit_compute_dtype=torch.bfloat16
)
 
# Load model and tokenizer
if finetune == 1.0:
    model = AutoPeftModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
        quantization_config=bnb_config,
        torch_dtype=torch.float16,
        trust_remote_code=True, 
    )
else:
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        device_map="auto",
#     attn_implementation="flash_attention_2",
        torch_dtype=torch.bfloat16,
        quantization_config=bnb_config,
        trust_remote_code=True
    )
tokenizer = AutoTokenizer.from_pretrained(model_id)
tokenizer.padding_side = 'right' # to prevent warnings
 
# # set chat template to OAI chatML, remove if you start from a fine-tuned model
if finetune != 1.0:
    
    #model.enable_gradient_checkpointing(gradient_checkpointing_kwargs={"use_reentrant": False})
    model, tokenizer = setup_chat_format(model, tokenizer)
    model.resize_token_embeddings(len(tokenizer))

from peft import LoraConfig
 
# LoRA config based on QLoRA paper & Sebastian Raschka experiment
peft_config = LoraConfig(
        lora_alpha=16, # was 128 originally, 16 gave length problems, tried 64 for many
        #lora_dropout=0.05,
        r=8, # was 256
        bias="none",
        target_modules="all-linear",
        task_type="CAUSAL_LM",
)


# Load LoRA adapters here instead so we can double train
model = get_peft_model(model, peft_config)

from transformers import TrainingArguments
 
args1 = TrainingArguments(
    #output_dir="model/codellama_finetuned/codellama_5ep/", # directory to save and repository id
    output_dir=sys.argv[2],
    num_train_epochs=5,                     # number of training epochs
    per_device_train_batch_size=1,          # batch size per device during training
    gradient_accumulation_steps=2,          # number of steps before performing a backward/update pass
    gradient_checkpointing=False,            # use gradient checkpointing to save memory
    optim="adamw_torch_fused",              # use fused adamw optimizer
    logging_steps=100,                       # log every 10 steps
    save_strategy="no",                     # don't save checkpoints to save space
    learning_rate=2e-4,                     # learning rate, based on QLoRA paper
    bf16=True,                              # use bfloat16 precision
    #tf32=True,                              # use tf32 precision
    max_grad_norm=0.3,                      # max gradient norm based on QLoRA paper
    warmup_ratio=0.03,                      # warmup ratio based on QLoRA paper
    lr_scheduler_type="constant",           # use constant learning rate scheduler
#     push_to_hub=True,                       # push model to hub
    report_to="tensorboard",                # report metrics to tensorboard
)

args2 = TrainingArguments(
    #output_dir="model/codellama_finetuned/codellama_5ep/", # directory to save and repository id
    output_dir=sys.argv[2],
    num_train_epochs=10,                     # number of training epochs
    per_device_train_batch_size=1,          # batch size per device during training
    gradient_accumulation_steps=2,          # number of steps before performing a backward/update pass
    gradient_checkpointing=False,            # use gradient checkpointing to save memory
    optim="adamw_torch_fused",              # use fused adamw optimizer
    logging_steps=10,                       # log every 10 steps
    save_strategy="no",                     # don't save checkpoints to save space
    learning_rate=2e-4,                     # learning rate, based on QLoRA paper
    bf16=True,                              # use bfloat16 precision
    #tf32=True,                              # use tf32 precision
    max_grad_norm=0.3,                      # max gradient norm based on QLoRA paper
    warmup_ratio=0.03,                      # warmup ratio based on QLoRA paper
    lr_scheduler_type="constant",           # use constant learning rate scheduler
#     push_to_hub=True,                       # push model to hub
    report_to="tensorboard",                # report metrics to tensorboard
)

from trl import SFTTrainer
 
max_seq_length = 3072 # max sequence length for model and packing of the dataset
 
trainer1 = SFTTrainer(
    model=model,
    args=args1,
    train_dataset=dataset,
    #peft_config=peft_config,
    max_seq_length=max_seq_length,
    tokenizer=tokenizer,
    #packing=True,
    dataset_kwargs={
        "add_special_tokens": False,  # We template with special tokens
        "append_concat_token": False, # No need to add additional separator token
    }
)

if dataset_file2:
    trainer2 = SFTTrainer(
        model=model,
        args=args2,
        train_dataset=dataset2,
        #peft_config=peft_config,
        max_seq_length=max_seq_length,
        tokenizer=tokenizer,
        packing=False,
        dataset_kwargs={
            "add_special_tokens": False,  # We template with special tokens
            "append_concat_token": False, # No need to add additional separator token
        }
    )

# freeze everything but the lora layers
for name, param in model.named_parameters():
    if "lora" not in name:  # Freeze all layers except LoRA layers
        param.requires_grad = False

# start training, the model will be automatically saved to the hub and the output directory
trainer1.train()
print("EOS token is", tokenizer.eos_token_id, "for tokenizer", tokenizer)

if dataset_file2:

    trainer2.train() 

# save model
    trainer2.save_model()
else:
    trainer1.save_model()



