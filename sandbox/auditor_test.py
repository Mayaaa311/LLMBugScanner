import json
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("using", device)

# Configuration
model_path = "models/llama-2-7b.Q5_K_M.gguf"
n_gpu_layers = -1
n_batch = 1000

# Initialize callback manager
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Initialize the model
llm = LlamaCpp(
    model_path=model_path,
    n_gpu_layers=n_gpu_layers,
    n_batch=n_batch,
    callback_manager=callback_manager,
    verbose=True
)

# Define the auditor prompt template
auditor_template = """
you are a code auditor, find bug in this code:
:\n{code}\n
return your evaluation in json format: 

"""

auditor_prompt = PromptTemplate.from_template(auditor_template)

# Sample smart contract code to audit
sample_code = """
    def add_numbers(a, b):
        result = a + b
        return result

    print(add_numbers(3, 5) 

"""

# Create the chain and run the auditor
auditor_chain = auditor_prompt | llm
response = auditor_chain.invoke({"code": sample_code})
print("response is here: ",response.split)
