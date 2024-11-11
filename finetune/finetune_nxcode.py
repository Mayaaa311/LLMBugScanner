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

# Print CUDA versions for verification
# print(f"PyTorch CUDA Version: {torch.version.cuda}")
# print(f"torchvision CUDA Version: {torchvision.version.cuda}")

# Load dataset
dataset = load_dataset("json", data_files="finetune/FineTuning_dataset/Dataset/train_dataset.json", split="train")
# dataset = load_dataset("philschmid/dolly-15k-oai-style", split="train")
print(dataset[3]["messages"])

print(dataset.column_names)  # Should show ['text']

# Hugging Face model id
model_name = "NTQAI/Nxcode-CQ-7B-orpo"

# Fine-tuned model name
new_model = "Nxcode-CQ-7B-finetune"


################################################################################
# bitsandbytes parameters
################################################################################

# Activate 4-bit precision base model loading
use_4bit = True

# Compute dtype for 4-bit base models
bnb_4bit_compute_dtype = "float16"

# Quantization type (fp4 or nf4)
bnb_4bit_quant_type = "nf4"

# Activate nested quantization for 4-bit base models (double quantization)
use_nested_quant = False

# Enable fp16/bf16 training (set bf16 to True with an A100)
fp16 = False
bf16 = False



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
    device_map="auto"
)
model.config.use_cache = True
model.config.pretraining_tp = 1

# Load LLaMA tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
tokenizer.pad_token = tokenizer.eos_token
tokenizer.padding_side = "right" # Fix weird overflow issue with fp16 training

# Load LoRA configuration
peft_config = LoraConfig(
    r=32, #Rank
    lora_alpha=8,
    # target_modules=[
    #     'q_proj',
    #     'k_proj',
    #     'v_proj',
    #     'dense'
    # ],
    target_modules = 'all-linear',
    bias="none",
    lora_dropout=0.05,  # Conventional
    task_type="CAUSAL_LM",
)
model.enable_input_require_grads() 
model.gradient_checkpointing_enable()

training_arguments = TrainingArguments(
    output_dir="finetune/model",
    num_train_epochs=2,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=2,
    optim="adamw_torch_fused",
    logging_steps=10,
    save_strategy="epoch", 
    fp16=fp16,
    bf16=bf16,
    learning_rate=2e-4,                     # learning rate, based on QLoRA paper
    max_grad_norm=0.3,                      # max gradient norm based on QLoRA paper
    warmup_ratio=0.03,   
    lr_scheduler_type="constant",           # use constant learning rate scheduler
    push_to_hub=False,    
    report_to="tensorboard"
)

# Set supervised fine-tuning parameters
trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
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
trainer.train()

trainer.save_model()