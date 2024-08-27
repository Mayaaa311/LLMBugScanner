import json
import logging
import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_community.chat_models import ChatOllama
from transformers import pipeline
# Load model directly
from transformers import AutoTokenizer, AutoModelForCausalLM
from tokenizers import Tokenizer
import torch
import re
import configparser
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("using", device)

def parse_config(cfg_path = "config/llama.cfg",model_id = "llama3"):
    # Initialize the config parser
    config = configparser.ConfigParser()
    config.read(cfg_path)
    # Choose the section based on the model
    model_section = model_id if model_id in config else 'llama3'
    # Extract parameters from the chosen section
    model_params = {key: config.get(model_section, key) for key in config[model_section]}
    # Convert parameter values to appropriate types if necessary
    for key in model_params:
        if model_params[key].isdigit():
            model_params[key] = int(model_params[key])
        else:
            try:
                model_params[key] = float(model_params[key])
            except ValueError:
                pass  # Leave it as a string if it can't be converted
    return model_params
def write_to_file(file_path, content, write = 'w'):
    # Create the directory if it doesn't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write the content to the file
    with open(file_path, write) as file:
        file.write(content)

class Detector:
    def __init__(self,
                 model_id="llama3",
                 auditor_template_path='templates/auditor_v1.txt', 
                 critic_template_path='templates/critic_v1.txt', 
                 ranker_template_path = 'templates/topk.txt',
                 log_dir='logger', result_dir='result', config = "config/llama.cfg"):
        self.output = "output"
        self.n_auditors = 1
        self.result_dir = result_dir
        self.auditor_template_path= auditor_template_path
        self.critic_template_path = critic_template_path
        self.ranker_template_path = ranker_template_path
        self.config = config

        # Create the logger directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir
        
        # Set the log filename with the current date and time
        log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
        log_path = os.path.join(log_dir, log_filename)
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_path, filemode='w')
        self.logger = logging.getLogger(__name__)
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
        self.model_id=model_id
        params = parse_config(cfg_path = config, model_id = model_id)
        self.params = params
        if model_id == "llama2":
            self.llm_aud = LlamaCpp(**params)
            self.llm_critic = LlamaCpp(**params)
            self.llm_ranker = LlamaCpp(**params) 
        if model_id == "Nxcode":
            self.llm_aud = pipeline("text-generation", model="NTQAI/Nxcode-CQ-7B-orpo", **params)
            self.llm_critic = pipeline("text-generation", model="NTQAI/Nxcode-CQ-7B-orpo", **params)
            self.llm_ranker = pipeline("text-generation", model="NTQAI/Nxcode-CQ-7B-orpo", **params)
        else:
            self.llm_aud=ChatOllama(model=model_id, n_ctx=4096,verbose=True,callback_manager = callback_manager)
            self.llm_critic = ChatOllama(model=model_id, **params,verbose=True,callback_manager = callback_manager)
            self.llm_ranker = ChatOllama(model=model_id, **params,verbose=True,callback_manager = callback_manager)               
        self.topk = "3"
        self.ranked_vulnerabilities = ""

        

    def set_template(self, auditor_template_path, input_var):
        with open(auditor_template_path, 'r') as file:
            auditor_template = file.read()
        tokenizer = Tokenizer.from_pretrained("TheBloke/Llama-2-70B-fp16")
        return PromptTemplate(input_variables=input_var, template=auditor_template)


    def clean_json(self, response: str) -> dict:
        try:
            # Load the JSON string into a dictionary
            parsed_response = json.loads(response)
            return parsed_response
        except json.JSONDecodeError as e:
            # Handle JSON decoding error
            print(f"JSONDecodeError: {e}")
            return {}

    def run_auditor(self, code: str):
        responses = []
        write_to_file(f"{self.result_dir}/{self.output}_{self.model_id}_k{self.topk}_n{self.n_auditors}/{self.output}_auditor.json", "",write='w')

        for i in range(self.n_auditors):

            response = self.auditor_chain.invoke({"code": code,"topk": self.topk}).content
            self.logger.info(f'response from auditor {i+1}: {response}')
            responses.append(response)
            write_to_file(f"{self.result_dir}/{self.output}_{self.model_id}_k{self.topk}_n{self.n_auditors}/{self.output}_auditor.json", response,write='a')
        return responses

    def run_critic(self, code, vulnerabilities):
        # evaluations = []

        response = self.critic_chain.invoke({"auditor_resp": str(vulnerabilities)}).content
        write_to_file(f"{self.result_dir}/{self.output}_{self.model_id}_k{self.topk}_n{self.n_auditors}/{self.output}_critic.json", response)
        self.logger.info(f'response from critic: {response}')
        return response
    
    def run_ranker(self, vulnerability) -> list:
        response = self.ranker_chain.invoke({"topk": self.topk, "vulnerability":vulnerability}).content
        self.logger.info(f'response from ranker: {response}')
        write_to_file(f"{self.result_dir}/{self.output}_{self.model_id}_k{self.topk}_n{self.n_auditors}/{self.output}_rank.json", str(response))
        return response
    def save_run(self):
        self.run_info = f'''Run Info: 
            config_path={self.config}, 
            parsed_config_params={self.params}
            model_id={self.model_id}, 
            auditor_template_path={self.auditor_template_path}, 
            critic_template_path={self.critic_template_path}, 
            ranker_template_path={self.ranker_template_path}, 
            topk={self.topk}, 
            log_dir={self.log_dir}, 
            result_dir={self.result_dir}, 
            output={self.output}, 
            n_auditors={self.n_auditors}, 
            '''
        self.logger.info(self.run_info)
        write_to_file(f"{self.result_dir}/{self.output}_{self.model_id}_k{self.topk}_n{self.n_auditors}/{self.output}_run_info", self.run_info)

    
    def run_pipeline(self, code_path = "", topk = "3",output = "output", n_auditors = 1,
                 auditor_template_path='templates/auditor_v1.txt', 
                 critic_template_path='templates/critic_v1.txt', 
                 ranker_template_path = 'templates/topk.txt',):
        code = ""
        with open(code_path, "r") as file:
            code = file.read()
        self.output = output
        self.topk = topk
        self.n_auditors = n_auditors

        # set prompt path
        self.auditor_template_path=auditor_template_path
        self.critic_template_path =critic_template_path
        self.ranker_template_path = ranker_template_path

        # Initialize and set prompt templates
        self.auditor_prompt = self.set_template(self.auditor_template_path,['code'])
        self.critic_prompt = self.set_template(self.critic_template_path,['code','vulnerability'])
        self.ranker_prompt = self.set_template(self.ranker_template_path,['vulnerability','topk'])
        
        # Create RunnableSequence instances
        self.auditor_chain = self.auditor_prompt | self.llm_aud
        self.critic_chain = self.critic_prompt | self.llm_critic
        self.ranker_chain = self.ranker_prompt | self.llm_ranker
        # Step 1: Generate vulnerabilities using auditors
        vulnerabilities = self.run_auditor(code)

        # Step 2: Evaluate vulnerabilities using critic
        evaluations = self.run_critic(code, vulnerabilities)

        
        # Step 3: Rank vulnerabilities based on critic's evaluation
        self.ranked_vulnerabilities = self.run_ranker(evaluations)

        return self.ranked_vulnerabilities


def main():
    #  This is an example showing how to create a deepseek based pipeline, asking iit to generate top 10 vulnerabilities
    # with 1 auditor. Saved in result/2018-10299, log in log

    # Initialize the detector
    detector = Detector(
        model_id= "deepseek-coder-v2",
        # model_id = "codeqwen",
        # model_id = "llama3",
        # model_id = "codellama",
        # model_id = "Nxcode",
        auditor_template_path='templates/auditor_v1.txt',
        critic_template_path='templates/critic_v1.txt',
        log_dir='log',
        result_dir='result'
    )

    # Run the pipeline with the sample code
    detector.run_pipeline(code_path = "data/2018-10299.sol", topk="10", n_auditors = 1, output= '2018-10299')





if __name__ == "__main__":
    main()
