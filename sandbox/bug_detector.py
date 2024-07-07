import json
import logging
import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import CTransformers
from langchain_core.runnables import RunnableSequence
import torch

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("using", device)

class Detector:
    def __init__(self, model_id, model_file, 
                 auditor_template_path='templates/auditor_basic.txt', 
                 critic_template_path='templates/critic_basic.txt', 
                 log_dir='logger', result_dir='result', n_auditors=3):
        
        self.model_id = model_id
        self.model_file = model_file
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
        
        # Initialize the models
        self.llm_aud = CTransformers(model=model_id, model_file=model_file, model_type="llama", device=device)
        self.llm_critic = CTransformers(model=model_id, model_file=model_file, model_type="llama", device=device)
        
        # Initialize and set prompt templates
        self.set_auditor_template(auditor_template_path)
        self.set_critic_template(critic_template_path)
        
        # Create RunnableSequence instances
        self.auditor_chain = self.auditor_prompt | self.llm_aud
        self.critic_chain = self.critic_prompt | self.llm_critic

        self.ranked_vulnerabilities = ""

    def set_auditor_template(self, auditor_template_path):
        with open(auditor_template_path, 'r') as file:
            auditor_template = file.read()
        # self.logger.info(f'this is auditor template: {auditor_template}')
        self.auditor_prompt = PromptTemplate(input_variables=["code"], template=auditor_template)

    def set_critic_template(self, critic_template_path):
        with open(critic_template_path, 'r') as file:
            critic_template = file.read()
        # self.logger.info(f'this is critic template: {critic_template}')
        self.critic_prompt = PromptTemplate(input_variables=["vulnerability", "code"], template=critic_template)
        
    def clean_json(self, response: str) -> str:
        pass  # User can define their own cleaning function

    def run_auditor(self, code: str) -> list:
        vulnerabilities = []
        for _ in range(self.n_auditors):
            self.logger.info(f'code: {code}')

            response = self.auditor_chain.invoke({"code": code})
            self.logger.info(f'response from auditor: {response.strip()}')
            try:
                response_json = json.loads(response)
                vulnerabilities.append(response_json)
            except json.JSONDecodeError:
                self.logger.error(f"Failed to parse JSON: {response}")
        self.logger.info(f'Vulnerabilities found: {json.dumps(vulnerabilities, indent=2)}')
        return vulnerabilities

    def run_critic(self, code: str, vulnerabilities: list) -> list:
        evaluations = []
        for vulnerability in vulnerabilities:
            response = self.critic_chain.invoke({"code": code, "vulnerability": json.dumps(vulnerability)})
            self.logger.info(f'response from critic: {response}')
            try:
                response_json = json.loads(response)
                evaluations.append(response_json)
            except json.JSONDecodeError:
                self.logger.error(f"Failed to parse JSON: {response}")
        self.logger.info(f'Evaluations: {json.dumps(evaluations, indent=2)}')
        return evaluations

    def run_pipeline(self, code: str):
        # Step 1: Generate vulnerabilities using auditors
        vulnerabilities = self.run_auditor(code)

        # Step 2: Evaluate vulnerabilities using critic
        evaluations = self.run_critic(code, vulnerabilities)

        # Step 3: Rank vulnerabilities based on critic's evaluation
        self.ranked_vulnerabilities = sorted(evaluations, key=lambda x: (x.get('correctness_score', 0), x.get('severity_score', 0)), reverse=True)

        return self.ranked_vulnerabilities

    def save_results(self, path=None):
        if path is None:
            os.makedirs(self.result_dir, exist_ok=True)
            path = os.path.join(self.result_dir, "ranked_vulnerabilities.txt")
        with open(path, 'w') as file:
            json.dump(self.ranked_vulnerabilities, file, indent=2)
        self.logger.info(f'Results saved to {path}')
