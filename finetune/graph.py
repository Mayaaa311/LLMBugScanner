

# from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
# import matplotlib.pyplot as plt

# # Path to the event file
# event_file2 = "finetune/model/Nxcode_finetuning_MessiQ_20ep_byfunc_new/runs/Dec07_01-06-12_atl1-1-02-009-32-0.pace.gatech.edu/events.out.tfevents.1733551741.atl1-1-02-009-32-0.pace.gatech.edu.2568810.0"
# event_file= 'finetune/model/Nxcode_finetuning_MessiQ_20ep_byfunc_new/runs/Dec07_01-13-56_atl1-1-03-012-28-0.pace.gatech.edu/events.out.tfevents.1733552040.atl1-1-03-012-28-0.pace.gatech.edu.4064358.0'

# event_acc = EventAccumulator(event_file)
# event_acc.Reload()
# # Print available scalar tags
# print("Available scalar tags:", event_acc.Tags()['scalars'])
# event_acc2 = EventAccumulator(event_file2)
# event_acc2.Reload()

# # Check available tags
# print("Available tags:", event_acc.Tags())

# # Extract data for the 'train/loss' scalar
# scalars = event_acc.Scalars("train/loss")
# # Extract data for the 'train/loss' scalar
# scalars2 = event_acc2.Scalars("train/loss")

# # Extract steps (epochs) and loss values
# epochs = [scalar.step/100 for scalar in scalars]
# epochs2 = [scalar.step+25 for scalar in scalars2]
# losses = [scalar.value for scalar in scalars]
# losses2 = [scalar.value for scalar in scalars2]


# # Plotting
# plt.figure(figsize=(10, 6))
# plt.plot(epochs, losses, marker="o", linestyle="-", color="blue", label="Training Loss (Dataset 1)")
# plt.plot(epochs2, losses2, marker="o", linestyle="-", color="#FDB813", label="Training Loss (Dataset 2)")
# plt.title("Training Loss over Epochs")
# plt.xlabel("Epoch")
# plt.ylabel("Loss")
# plt.grid(True)
# plt.legend()

# # Save and show the plot
# output_path = "finetune/model/Nxcode_finetuning_MessiQ_20ep_byfunc_new/epoch_graph_combined.png"
# plt.savefig(output_path, dpi=300)
# plt.show()
# plt.close()

# print(f"Graph saved to {output_path}")


from tensorboard.backend.event_processing.event_accumulator import EventAccumulator
import os

# Path to the TensorFlow events file
events_file_path = "finetune/model/Deepseek_finetuning_MessiQ_critic/runs/Dec13_03-04-19_atl1-1-01-005-13-0.pace.gatech.edu/events.out.tfevents.1734077061.atl1-1-01-005-13-0.pace.gatech.edu"

# Check if file exists
if not os.path.exists(events_file_path):
    print(f"File not found: {events_file_path}")
else:
    # Load the event accumulator
    event_acc = EventAccumulator(events_file_path)
    event_acc.Reload()

    # Extract available keys
    available_tags = event_acc.Tags()
    print("Available Tags:", available_tags)

    # Extract scalar values (e.g., loss, runtime, accuracy)
    scalar_data = {}
    for tag in available_tags.get('scalars', []):
        scalar_data[tag] = [scalar.value for scalar in event_acc.Scalars(tag)]
        print(f"{tag}: {scalar_data[tag]}")

    # Example: Extract runtime or training information
    if "runtime" in scalar_data:
        print(f"Runtime: {scalar_data['runtime'][-1]} seconds")
    else:
        print("Runtime data not found.")

    # Example: Extract loss if available
    if "loss" in scalar_data:
        print(f"Final Loss: {scalar_data['loss'][-1]}")
    else:
        print("Loss data not found.")
