from transformers import GemmaTokenizer,BitsAndBytesConfig, AutoTokenizer, AutoModelForCausalLM,  LlamaForCausalLM, AutoModel, pipeline
import transformers
from langchain_core.prompts import PromptTemplate
import torch
from lens.Base import BaseLLM, param1, param2
from lens.utils import parse_config
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
import os
import time
os.environ["TOKENIZERS_PARALLELISM"] = "false"
from peft import AutoPeftModelForCausalLM
from trl import setup_chat_format
generation_params=param1
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
class Huggingface_LLM(BaseLLM):
    def __init__(self, model_id, prompt_path, model_params_path=None):
        self.model_id = model_id
        self.model_params = None
        if model_params_path is not None:
            self.model_params = self.load_params(model_params_path)
        self.tokenizer = None
        self.model = None
        self.prompt_path = prompt_path


    def load_model(self):

        # Load model and tokenizer
        if self.model_id == "google/codegemma-7b":
            self.tokenizer =GemmaTokenizer.from_pretrained(self.model_id, trust_remote_code=True)
        # elif self.model_id == 'finetune/model/final_models/codellama_CVE_10ep':
        #     self.tokenizer = AutoTokenizer.from_pretrained('AlfredPros/CodeLlama-7B-Instruct-Solidity',  trust_remote_code=True)
        # elif self.model_id == 'finetune/model/final_models/gemma_messi_5ep_CVE_10ep':
        #     self.tokenizer = AutoTokenizer.from_pretrained('TechxGenus/CodeGemma-7b',  trust_remote_code=True)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_id,  trust_remote_code=True)
        
        
        
        self.tokenizer.model_max_length = 35000
        if self.model_id == "THUDM/codegeex2-6b":
            self.model = AutoModel.from_pretrained("THUDM/codegeex2-6b", trust_remote_code=True)
            self.model = self.model.eval()
            return
    

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
        if self.model_id == 'finetune/model/final_models/codellama_CVE_10ep':

            self.model = AutoPeftModelForCausalLM.from_pretrained(self.model_id, quantization_config = bnb_config, device_map="auto",  trust_remote_code=True)

        elif self.model_id == 'finetune/model/final_models/gemma_messi_5ep_CVE_10ep' :
            print("peftmodel set")
            self.model = AutoPeftModelForCausalLM.from_pretrained(self.model_id,  quantization_config = bnb_config, device_map="auto",  trust_remote_code=True)
         # tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        else:
            self.model = AutoModelForCausalLM.from_pretrained(self.model_id, 
                                                            quantization_config = bnb_config, 
                                                            device_map="auto", 
                                                            trust_remote_code=True)
            

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
        prompt_input = self.prompt.format_prompt(**prompt)
        
        prompt = str(prompt_input)[6:-1]
        prompt = (
            prompt.replace('\\n', '\n')
                    .replace('\\"', '"')
                    .replace('{{', '{')
                    .replace('}}', '}')
                    .strip()
        )
        # print("PROMPT: ",prompt)
        if (self.model_id == "AlfredPros/CodeLlama-7b-Instruct-Solidity" ):
            # Tokenize the input prompt
            input_ids = self.tokenizer(prompt, return_tensors="pt", truncation=True).input_ids.to(device)
            # Run the model to generate an output
            outputs = self.model.generate(input_ids=input_ids, **generation_params)
            # Detokenize and return the generated output
            response = self.tokenizer.batch_decode(outputs.detach().cpu().numpy(), skip_special_tokens=True)[0][len(prompt):]
            return response
        # elif (self.model_id == 'finetune/model/final_models/codellama_CVE_10ep' )or (self.model_id == 'finetune/model/final_models/gemma_messi_5ep_CVE_10ep'):
        #     self.model, self.tokenizer = setup_chat_format(self.model, self.tokenizer)
        #             # load into pipeline
        #     pipe = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
        #     # Test on sample
        #     prompt = pipe.tokenizer.apply_chat_template([{'role': 'user', 'content': prompt }],return_tensors="pt", add_generation_prompt=True)
        #     outputs = pipe(prompt, eos_token_id=pipe.tokenizer.eos_token_id, pad_token_id=pipe.tokenizer.pad_token_id, **generation_params)
            
        #     return outputs[0]['generated_text'][len(prompt):].strip()
        elif self.model_id == "WisdomShell/CodeShell-7B-Chat":
            history = []
            return self.model.chat(prompt, history, self.tokenizer)
        elif self.model_id == "THUDM/codegeex2-6b" or self.model_id == "bigcode/starcoder2-7b":
            # remember adding a language tag for better performance
            inputs = self.tokenizer.encode(prompt, return_tensors="pt").to(device)
            outputs = self.model.generate(inputs, **generation_params)
            return self.tokenizer.decode(outputs[0])
        elif self.model_id == "m-a-p/OpenCodeInterpreter-DS-6.7B":

            inputs = self.tokenizer.apply_chat_template(
                [{'role': 'user', 'content': prompt }],
                return_tensors="pt"
            ).to(device)

            # Generate model output based on the inputs
            outputs = self.model.generate(inputs, pad_token_id=self.tokenizer.eos_token_id,eos_token_id=self.tokenizer.eos_token_id,**generation_params)

            # Decode the generated output, skipping special tokens
            generated_text = self.tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
            return generated_text
        else:
            messages = [
                {"role": "user", "content": prompt}
            ]
            inputs = self.tokenizer.apply_chat_template(messages, add_generation_prompt=True, return_tensors="pt").to(device)
            outputs = self.model.generate(inputs, **generation_params, eos_token_id=self.tokenizer.eos_token_id)
            
            return self.tokenizer.decode(outputs[0][len(inputs[0]):], skip_special_tokens=True)
    def handle_response(self, response) -> dict:
        # Process the response as needed
        return {"response": response}
    
    def __call__(self, prompt) -> str:
        return self.invoke(prompt)
    def __or__(self, prompt):
        return prompt | self.model 