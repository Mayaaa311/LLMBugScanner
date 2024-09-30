from transformers import AutoTokenizer
import transformers
import torch
from lens.Base import BaseLLM
from lens.utils import parse_config

class pipeline_LLM(BaseLLM):
    def __init__(self, model_id, model_params_path=None):
        self.model_id = model_id
        self.model_params = None
        if model_params_path is not None:
            self.model_params = self.load_params(model_params_path)
        self.tokenizer = None
        self.model = None


    def load_model(self):

        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id,  trust_remote_code=True)

        self.model =transformers.pipeline(
            "text-generation",
            model=self.model_id,
            torch_dtype=torch.float16,
            device_map="auto",
        )

    def load_params(self, model_params_path):
        if model_params_path is not None:
            self.model_params = parse_config(cfg_path=model_params_path, model_id=self.model_id)
            print("Loaded parameters: ", self.model_params)
            return self.model_params 
        return None
    
    def invoke(self, prompt) -> str:
        prompt = str(prompt)[6:-1]
       
        sequences = self.model(
            prompt,
            do_sample=True,
            top_k=50,
            temperature=0.01,
            top_p=0.95,
            num_return_sequences=1,
            eos_token_id=self.tokenizer.eos_token_id,
            max_length=10000,
        )

        return sequences[0]['generated_text'][len(prompt):]

    def handle_response(self, response) -> dict:
        # Process the response as needed
        return {"response": response}
    
    def __call__(self, prompt) -> str:
        return self.invoke(prompt)
    def __or__(self, prompt):
        return prompt | self.model 
