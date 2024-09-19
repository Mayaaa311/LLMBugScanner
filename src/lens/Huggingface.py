from transformers import BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM
import torch
from lens.Base import BaseLLM
from lens.utils import parse_config
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler

class Huggingface_LLM(BaseLLM):
    def __init__(self, model_id, model_params_path=None, quantize = False):
        self.model_id = model_id
        self.model_params = None
        if model_params_path is not None:
            self.model_params = self.load_params(model_params_path)
        self.tokenizer = None
        self.model = None
        self.quantize = quantize
    def quantize_config(self):
                # Initialize the tokenizer and model with 4-bit quantization
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
            load_in_8bit_fp32_cpu_offload=True,
            device_map="cuda"
        )
        return bnb_config
    
    def load_model(self):

        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id,  trust_remote_code=True)
        # if self.quantize:
        #     self.model = AutoModelForCausalLM.from_pretrained(self.model_id, quantization_config=self.quantize_config(), device_map="balanced_low_0", **self.model_params)
        # else:
        if self.model_params is not None and self.model_params:
            self.model = AutoModelForCausalLM.from_pretrained(self.model_id, device_map="auto", **self.model_params)
        else:
            self.model = AutoModelForCausalLM.from_pretrained(self.model_id, device_map="auto")
        # # Ensure that callback_manager is a valid object
        # if isinstance(self.model_params.get("callback_manager"), str) and self.model_params["callback_manager"] == "default":
        #     self.model_params["callback_manager"] = CallbackManager([StreamingStdOutCallbackHandler()])

    def load_params(self, model_params_path):
        if model_params_path is not None:
            self.model_params = parse_config(cfg_path=model_params_path, model_id=self.model_id)
            print("Loaded parameters: ", self.model_params)
            return self.model_params 
        return None
    
    def invoke(self, prompt) -> str:
        prompt = str(prompt)[6:-1]
        print(prompt)
        # Tokenize the input prompt
        input_ids = self.tokenizer(prompt, return_tensors="pt", truncation=True).input_ids.cuda()
        # Run the model to generate an output
        outputs = self.model.generate(input_ids=input_ids, max_new_tokens=1024, do_sample=True, top_p=0.9, temperature=0.001, pad_token_id=1)
        # Detokenize and return the generated output
        response = self.tokenizer.batch_decode(outputs.detach().cpu().numpy(), skip_special_tokens=True)[0][len(prompt):]
        return response

    def handle_response(self, response) -> dict:
        # Process the response as needed
        return {"response": response}
    
    def __call__(self, prompt) -> str:
        return self.invoke(prompt)
    def __or__(self, prompt):
        return prompt | self.model 
