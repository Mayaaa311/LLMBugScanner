import json
import logging
import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_community.chat_models import ChatOllama
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
                 topk = 3,
                 log_dir='logger', result_dir='result', output="output",n_auditors=3, config = "config/llama.cfg"):
        self.output = output
        self.n_auditors = n_auditors
        self.result_dir = result_dir

        # Create the logger directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir
        
        # Set the log filename with the current date and time
        log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
        log_path = os.path.join(log_dir, log_filename)
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_path, filemode='w')
        self.logger = logging.getLogger(__name__)
        
        self.model_id=model_id
        params = parse_config(cfg_path = config, model_id = model_id)
        if model_id == "llama2":
            self.llm_aud = LlamaCpp(**params)
            self.llm_critic = LlamaCpp(**params)
            self.llm_ranker = LlamaCpp(**params) 
        else:
            self.llm_aud=ChatOllama(model=model_id, **params)
            self.llm_critic = ChatOllama(model=model_id, **params)
            self.llm_ranker = ChatOllama(model=model_id, **params)               
        self.topk = topk
        # Initialize and set prompt templates
        self.auditor_prompt = self.set_template(auditor_template_path,['code'])
        self.critic_prompt = self.set_template(critic_template_path,['code','vulnerability'])
        self.ranker_prompt = self.set_template(ranker_template_path,['vulnerability','topk'])
        
        # Create RunnableSequence instances
        self.auditor_chain = self.auditor_prompt | self.llm_aud
        self.critic_chain = self.critic_prompt | self.llm_critic
        self.ranker_chain = self.ranker_prompt | self.llm_ranker

        self.ranked_vulnerabilities = ""
        run_info = f'''Detector initialized with parameters: 
            model_id={model_id}, 
            auditor_template_path={auditor_template_path}, 
            critic_template_path={critic_template_path}, 
            ranker_template_path={ranker_template_path}, 
            topk={topk}, 
            log_dir={log_dir}, 
            result_dir={result_dir}, 
            output={output}, 
            n_auditors={n_auditors}, 
            config_path={config}, 
            parsed_config_params={params}
            '''

        self.logger.info(run_info)
        write_to_file(f"{self.result_dir}/{self.output}_{self.model_id}/{self.output}_run_info", run_info)
        
    def set_template(self, auditor_template_path, input_var):
        with open(auditor_template_path, 'r') as file:
            auditor_template = file.read()
        print(auditor_template)
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
        for i in range(self.n_auditors):

            response = self.auditor_chain.invoke({"code": code,"topk": self.topk}).content
            self.logger.info(f'response from auditor {i+1}: {response}')
            responses.append(response)
            write_to_file(f"{self.result_dir}/{self.output}_{self.model_id}/{self.output}_auditor.json", response,write='a')
        return responses

    def run_critic(self, code, vulnerabilities):
        # evaluations = []

        response = self.critic_chain.invoke({"auditor_resp": str(vulnerabilities)}).content
        write_to_file(f"{self.result_dir}/{self.output}_{self.model_id}/{self.output}_critic.json", response)
        self.logger.info(f'response from critic: {response}')
        return response
    
    def run_ranker(self, vulnerability) -> list:
        response = self.ranker_chain.invoke({"topk": self.topk, "vulnerability":vulnerability}).content
        self.logger.info(f'response from ranker: {response}')
        write_to_file(f"{self.result_dir}/{self.output}_{self.model_id}/{self.output}_rank.json", str(response))
        return response
    
    def run_pipeline(self, code: str):
        # Step 1: Generate vulnerabilities using auditors
        vulnerabilities = self.run_auditor(code)

        # Step 2: Evaluate vulnerabilities using critic
        evaluations = self.run_critic(code, vulnerabilities)

        
        # Step 3: Rank vulnerabilities based on critic's evaluation
        self.ranked_vulnerabilities = self.run_ranker(evaluations)

        return self.ranked_vulnerabilities


    def save_results(self, path=None):
        if path is None:
            os.makedirs(self.result_dir, exist_ok=True)
            path = os.path.join(self.result_dir, self.output)
        # Write the extracted JSON to the output file
        # with open(path, 'w') as file:
        #     json.dump(vulnerabilities, file, indent=2)
        
        self.logger.info(f'Results saved to {path}')

def main():
    # Define the file path
    file_path = "data/2018-13074.sol"
    sample_code=""
    # Read the file content
    with open(file_path, "r") as file:
        sample_code = file.read()

    # Initialize the detector
    detector = Detector(
        # model_id= "deepseek-coder-v2",
        # model_id = "codeqwen",
        model_id = "llama3",
        auditor_template_path='templates/auditor_v1.txt',
        critic_template_path='templates/critic_v1.txt',
        log_dir='log',
        result_dir='result',
        output = '2018-13074',
        topk=3,
        n_auditors=1,
    )

    # Run the pipeline with the sample code
    detector.run_pipeline(sample_code)
    detector.save_results()

if __name__ == "__main__":
    main()
