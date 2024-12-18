import os
import torch
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    HfArgumentParser,
    TrainingArguments,
    pipeline,
    logging,
)
from peft import LoraConfig, PeftModel
from trl import SFTTrainer
     
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"  
torch.set_grad_enabled(True)

torch.cuda.empty_cache()

if torch.cuda.is_available():
    print("CUDA is available.")
    print(f"CUDA device count: {torch.cuda.device_count()}")
    print(f"Current CUDA device: {torch.cuda.current_device()}")
    print(f"Device name: {torch.cuda.get_device_name(torch.cuda.current_device())}")
else:
    print("CUDA is not available.")
# Print CUDA versions for verification
# print(f"PyTorch CUDA Version: {torch.version.cuda}")
# print(f"torchvision CUDA Version: {torchvision.version.cuda}")

# Load dataset
dataset = load_dataset("json", data_files="finetune/FineTuning_dataset/Dataset/fine_tuning_data2.jsonl", split="train")
# eval_dataset=load_dataset("json", data_files="finetune/FineTuning_dataset/gptlens_dataset/test_dataset.json")

# dataset = load_dataset("philschmid/dolly-15k-oai-style", split="train")
# print(dataset[3]["messages"])

# print(dataset.column_names)  # Should show ['text']

# Hugging Face model id
checkpoint_path =None
# checkpoint_path = 'finetune/model/Nxcode_finetuning_specfunc_alllinear/checkpoint-7000'
checkpoint_path = 'finetune/model/deepseek_finetuning_specfunc_alllinear/checkpoint-2000'
model_name = "deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"
# model_name = "NTQAI/Nxcode-CQ-7B-orpo"

# Fine-tuned model name
new_model = "finetune/model/deepseek_finetuning_specfunc_alllinear"
# new_model = "finetune/model/Nxcode_finetuning_specfunc_alllinear"
################################################################################
# bitsandbytes parameters
################################################################################

# Activate 4-bit precision base model loading
use_4bit = False

# Compute dtype for 4-bit base models
bnb_4bit_compute_dtype = "float16"

# Quantization type (fp4 or nf4)
bnb_4bit_quant_type = "nf4"

# Activate nested quantization for 4-bit base models (double quantization)
use_nested_quant = False

# Enable fp16/bf16 training (set bf16 to True with an A100)
fp16 = False
bf16 = True



# Load tokenizer and model with QLoRA configuration
compute_dtype = getattr(torch, bnb_4bit_compute_dtype)

bnb_config = BitsAndBytesConfig(
    load_in_4bit=use_4bit,
    bnb_4bit_quant_type=bnb_4bit_quant_type,
    bnb_4bit_compute_dtype=compute_dtype,
    bnb_4bit_use_double_quant=use_nested_quant,
)

# Check GPU compatibility with bfloat16
if compute_dtype == torch.float16 and use_4bit:
    major, _ = torch.cuda.get_device_capability()
    if major >= 8:
        print("=" * 80)
        print("Your GPU supports bfloat16: accelerate training with bf16=True")
        print("=" * 80)

# Load base model
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    torch_dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True
)
model.config.use_cache = True
model.config.pretraining_tp = 1

# Load LLaMA tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right" # Fix weird overflow issue with fp16 training



peft_config = LoraConfig(
    r=32,
    lora_alpha=8,
    # target_modules='all-linear',
    target_modules = [
        "self_attn.q_proj",
        "self_attn.k_proj",
        "self_attn.v_proj",
        "self_attn.o_proj",
        "mlp.gate_proj",
        "mlp.up_proj",
        "mlp.down_proj",
        "lm_head"
    ],
    bias="none",
    lora_dropout=0.05,
    task_type="CAUSAL_LM",
)

print("--------------LORA CONFIG-----------------")
# Print LoRA configuration
peft_config_dict = vars(peft_config)
for key, value in peft_config_dict.items():
    print(f"{key}: {value}")

model.enable_input_require_grads() 
model.gradient_checkpointing_enable()

training_arguments = TrainingArguments(
    output_dir=new_model,
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,
    optim="adamw_torch_fused",
    logging_steps=10,
    save_strategy="steps",  
    save_steps=1000,   
    fp16=fp16,
    bf16=bf16,
    learning_rate=2e-4,                     # learning rate, based on QLoRA paper
    max_grad_norm=0.3,                      # max gradient norm based on QLoRA paper
    warmup_ratio=0.03,   
    lr_scheduler_type="constant",           # use constant learning rate scheduler
    push_to_hub=False,    
    report_to="tensorboard"
)
print("--------------TRAINING CONFIG-----------------")
# Convert to dictionary and print
args_dict = training_arguments.to_dict()
for key, value in args_dict.items():
    print(f"{key}: {value}")

# Set supervised fine-tuning parameters
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    eval_dataset=dataset, 
    peft_config=peft_config,
    max_seq_length=256,
    tokenizer=tokenizer,
    args=training_arguments,
    packing=True,
    dataset_kwargs={
        "add_special_tokens": False, # We template with special tokens
        "append_concat_token": False, # No need to add additional separator token
    }
)

# Train model
trainer.train(resume_from_checkpoint=checkpoint_path)

trainer.save_model()