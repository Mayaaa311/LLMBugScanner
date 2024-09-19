from llama_cpp import Llama
from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM
import torch
from lens.Base import BaseLLM
from lens.utils import parse_config
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

class LlamaCpp_LLM(BaseLLM):
    def __init__(self, model_id, model_path = None, model_params_path=None, quantize = False):
        self.model_id = model_id
        self.model_path = model_path
        self.model_params = None
        if model_params_path is not None:
            self.model_params = self.load_params(model_params_path)
        self.tokenizer = None
        self.prompt = None
        self.model = None

    def load_model(self):
        # Load model and tokenizer
        self.model = Llama.from_pretrained(
                repo_id=self.model_id,
                filename=self.model_path,
                **self.model_params
            )

        # # Ensure that callback_manager is a valid object
        # if isinstance(self.model_params.get("callback_manager"), str) and self.model_params["callback_manager"] == "default":
        #     self.model_params["callback_manager"] = CallbackManager([StreamingStdOutCallbackHandler()])

    def load_params(self, model_params_path):
        if model_params_path is not None:
            self.model_params = parse_config(cfg_path=model_params_path, model_id=self.model_id)
            print("Loaded parameters: ", self.model_params)
            return self.model_params 
        return None

    def invoke(self, prompt):
        """
        Replaces placeholders in the prompt with values from input_dict and invokes the model.

        Args:
        - input_dict: A dictionary containing the values to replace in the prompt, e.g., {"code": "...", "topk": 3}

        Returns:
        - response: The generated response from the model.
        """
        # Render the prompt by replacing placeholders with actual values
        rendered_prompt = str(prompt)

                # Invoke the model with the processed prompt using Llama's create_chat_completion
        response = self.model.create_chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": rendered_prompt
                }
            ]
        )

        # Extract the generated response (depends on your Llama model's output format)
        return response['choices'][0]['message']['content']

 
    def handle_response(self, response) -> dict:
        # Process the response as needed
        return {"response": response}

    def __call__(self, prompt) -> str:
        return self.invoke(prompt)
    def __or__(self, prompt):
        if isinstance(prompt, PromptTemplate):
            self.prompt = prompt.template  # Convert to string using the template attribute
        else:
            self.prompt = str(prompt)  # If it's not a PromptTemplate, just convert it to string
        return self