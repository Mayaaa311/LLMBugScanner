from transformers import Trainer, TrainingArguments

# Path to the checkpoint
checkpoint_dir = "finetune/model/Deepseek_finetuning_MessiQ_critic/checkpoint-860"

# Load the training state
from transformers import TrainerState
import os

state_file = os.path.join(checkpoint_dir, "trainer_state.json")

try:
    with open(state_file, "r") as f:
        import json
        trainer_state = json.load(f)

    # Extract loss history
    loss_history = trainer_state.get("log_history", [])
    for entry in loss_history:
        if "loss" in entry:
            print(f"Step: {entry.get('step')}, Loss: {entry.get('loss')}")
except FileNotFoundError:
    print(f"No 'trainer_state.json' found in {checkpoint_dir}.")

import matplotlib.pyplot as plt

# Extract loss and steps
steps = []
losses = []

for entry in loss_history:
    if "loss" in entry:
        steps.append(entry.get("step"))
        losses.append(entry.get("loss"))

# Check if we have data to plot
if steps and losses:
    # Plot the loss over steps
    plt.figure(figsize=(10, 6))
    plt.plot(steps, losses, marker='o', linestyle='-', color='b')
    plt.title("Loss Over Steps")
    plt.xlabel("Steps")
    plt.ylabel("Loss")
    plt.grid(True)
    plt.show()
    plt.savefig(checkpoint_dir+'/plt_loss.jpg')
    print("figure saved to : ", checkpoint_dir+'/plt_loss.jpg')
else:
    print("No loss data found to plot.")

# Extract and display training information
training_info = trainer_state.get("training_args", {})
log_history = trainer_state.get("log_history", [])

def format_seconds_to_hhmmss(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}"

try:
    train_runtime = trainer_state.get("train_runtime", None)
    train_loss = trainer_state.get("train_loss", None)
    train_samples_per_second = trainer_state.get("train_samples_per_second", None)
    train_steps_per_second = trainer_state.get("train_steps_per_second", None)
    epochs = training_info.get("num_train_epochs", None)

    # Calculate per-epoch time if runtime and epochs are available
    per_epoch_time = None
    if train_runtime and epochs:
        per_epoch_time = train_runtime / epochs

    print("\nTraining Information:")
    print({
        'train_runtime': format_seconds_to_hhmmss(train_runtime) if train_runtime else 'N/A',
        'train_samples_per_second': train_samples_per_second,
        'train_steps_per_second': train_steps_per_second,
        'train_loss': train_loss,
        'epoch': epochs,
        'per_epoch_time': format_seconds_to_hhmmss(per_epoch_time) if per_epoch_time else 'N/A'
    })

    # Number of training data
    train_dataset_size = training_info.get("train_batch_size", None) * training_info.get("gradient_accumulation_steps", 1) * training_info.get("per_device_train_batch_size", 1)
    print(f"Number of training data: {train_dataset_size}")

except Exception as e:
    print("Error extracting training information:", str(e))
