from transformers import AutoTokenizer
from transformers import GemmaTokenizer, AutoModelForCausalLM
from transformers import GemmaTokenizer,BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM,  LlamaForCausalLM, AutoModel

from lens.Base import BaseLLM, param1, param2
import torch
from lens.utils import parse_config
generation_params=param1
class gemma_LLM(BaseLLM):
    def __init__(self, model_id, prompt_path,model_params_path=None):
        self.model_id = model_id
        self.model_params = None
        if model_params_path is not None:
            self.model_params = self.load_params(model_params_path)
        self.tokenizer = None
        self.model = None
        self.prompt_path = prompt_path


    def load_model(self):

        # Load model and tokenizer
        self.tokenizer = GemmaTokenizer.from_pretrained(self.model_id)

        use_4bit = True
        bnb_4bit_compute_dtype = "float16"
        bnb_4bit_quant_type = "nf4"
        use_double_nested_quant = True
        compute_dtype = getattr(torch, bnb_4bit_compute_dtype)

        # BitsAndBytesConfig 4-bit config
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=use_4bit,
            bnb_4bit_use_double_quant=use_double_nested_quant,
            bnb_4bit_quant_type=bnb_4bit_quant_type,
            bnb_4bit_compute_dtype=compute_dtype,
            load_in_8bit_fp32_cpu_offload=True
        )
        self.model = AutoModelForCausalLM.from_pretrained(self.model_id, 
                                                            quantization_config = bnb_config, 
                                                            # device_map="auto", 
                                                            trust_remote_code=True)

    def load_params(self, model_params_path):
        if model_params_path is not None:
            self.model_params = parse_config(cfg_path=model_params_path, model_id=self.model_id)
            print("Loaded parameters: ", self.model_params)
            return self.model_params 
        return None
    
    def invoke(self, prompt) -> str:
        prompt_input = self.prompt.format_prompt(**prompt)
        prompt = str(prompt_input)[6:-1]
        inputs = self.tokenizer(prompt, return_tensors="pt")
        prompt_len = inputs["input_ids"].shape[-1]
        outputs = self.model.generate(**inputs, **generation_params)

        return self.tokenizer.decode(outputs[0])

    def handle_response(self, response) -> dict:
        # Process the response as needed
        return {"response": response}
    
    def __call__(self, prompt) -> str:
        return self.invoke(prompt)
    def __or__(self, prompt):
        return prompt | self.model 
