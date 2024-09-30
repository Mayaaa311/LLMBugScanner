from transformers import AutoTokenizer
from transformers import GemmaTokenizer, AutoModelForCausalLM

import torch
from lens.Base import BaseLLM
from lens.utils import parse_config

class gemma_LLM(BaseLLM):
    def __init__(self, model_id, model_params_path=None):
        self.model_id = model_id
        self.model_params = None
        if model_params_path is not None:
            self.model_params = self.load_params(model_params_path)
        self.tokenizer = None
        self.model = None


    def load_model(self):

        # Load model and tokenizer
        self.tokenizer = GemmaTokenizer.from_pretrained(self.model_id)

        self.model =AutoModelForCausalLM.from_pretrained(self.model_id)

    def load_params(self, model_params_path):
        if model_params_path is not None:
            self.model_params = parse_config(cfg_path=model_params_path, model_id=self.model_id)
            print("Loaded parameters: ", self.model_params)
            return self.model_params 
        return None
    
    def invoke(self, prompt) -> str:
        prompt = str(prompt)[6:-1]
        inputs = self.tokenizer(prompt, return_tensors="pt")
        prompt_len = inputs["input_ids"].shape[-1]
        outputs = self.model.generate(**inputs, max_new_tokens=100)

        return self.tokenizer.decode(outputs[0])

    def handle_response(self, response) -> dict:
        # Process the response as needed
        return {"response": response}
    
    def __call__(self, prompt) -> str:
        return self.invoke(prompt)
    def __or__(self, prompt):
        return prompt | self.model 
