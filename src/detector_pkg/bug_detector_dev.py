# still under development...


import json
import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("using", device)


class Detector_dev:
    def __init__(self, model_path, 
                 log_dir='logger', n_auditors=3,
                 n_gpu_layers=-1, n_batch=1024):
        
        self.model_path = model_path
        self.n_auditors = n_auditors

        # Create the logger directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir
        
        # Initialize callback manager
        self.callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

        # Initialize the model
        self.llm_aud = LlamaCpp(
            model_path=model_path,
            n_gpu_layers=n_gpu_layers,
            n_batch=n_batch,
            callback_manager=self.callback_manager,
            verbose=True
        )

        # Define the auditor prompt template
        self.auditor_template = """
        You are a smart contract auditor, identify and explain severe vulnerabilities 
        in the provided smart contract. Make sure that they are exploitable in the real 
        world and beneficial to attackers. Provide each identified vulnerability with
        intermediate reasoning and its associated function. Remember, you must 
        provide the entire function code and do not use "...". Make your 
        reasoning comprehensive and detailed. Smart contract code:\n{code}\n

        You should only output in below json format:
        {{
            "output_list": [
                {{
                    "function_name": "<function_name_1>",
                    "code": "<original_function_code_1>",
                    "vulnerability": "<short_vulnera_desc_1>",
                    "reason": "<reason_1>"
                }},
                {{
                    "function_name": "<function_name_2>",
                    "code": "<original_function_code_2>",
                    "vulnerability": "<short_vulnera_desc_2>",
                    "reason": "<reason_2>"
                }}
            ]
        }}
        """
        self.auditor_prompt = PromptTemplate.from_template(self.auditor_template)

    def run_auditor(self, code: str) -> dict:
        auditor_chain = self.auditor_prompt | self.llm_aud
        response = auditor_chain.invoke({"code": code})
        try:
            response_json = json.loads(response)
            return response_json
        except json.JSONDecodeError:
            print(f"Failed to parse JSON: {response}")
            return {}

# Example usage
if __name__ == "__main__":
    model_path = "models/llama-2-7b.Q5_K_M.gguf"
    log_dir = 'logger'
    
    detector = Detector_dev(model_path, log_dir)
    
    # Sample smart contract code to audit
    sample_code = """
    pragma solidity ^0.8.0;

    contract Vulnerable {
        address private owner;

        constructor() {
            owner = msg.sender;
        }

        function withdraw() public {
            require(msg.sender == owner);
            payable(msg.sender).transfer(address(this).balance);
        }
    }
    """
    
    # Run the auditor
    result = detector.run_auditor(sample_code)
    print(json.dumps(result, indent=2))
