import json
import logging
import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
import torch
from utils import write_to_file
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("using", device)


class BugScanner:
    def __init__(self, auditor_models, critic_model, ranker_model, model_params_path="config/llama.json", auditor_template_path='templates/auditor_v1.txt', 
                 critic_template_path='templates/critic_v1.txt', 
                 ranker_template_path='templates/topk.txt',
                 log_dir='logger', result_dir='result'):
        self.output = "output"
        self.n_auditors = len(auditor_models)
        self.result_dir = result_dir
        self.auditor_template_path = auditor_template_path
        self.critic_template_path = critic_template_path
        self.ranker_template_path = ranker_template_path
        
        # Create the logger directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir
        
        # Set the log filename with the current date and time
        log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
        log_path = os.path.join(log_dir, log_filename)
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_path, filemode='w')
        self.logger = logging.getLogger(__name__)
        
        # Initialize the models using the provided classes and parameters
        self.llm_auditors = auditor_models
        self.llm_critic = critic_model
        self.llm_ranker = ranker_model

        # Load the models
        for auditor in self.llm_auditors:
            auditor.load_model()
        self.llm_critic.load_model()
        self.llm_ranker.load_model()

        self.topk = "3"
        self.ranked_vulnerabilities = ""

    def set_template(self, template_path, input_var):
        with open(template_path, 'r') as file:
            template = file.read()
        return PromptTemplate(input_variables=input_var, template=template)

    def run_auditor(self, code: str):
        responses = []
        for i, auditor in enumerate(self.auditor_chain):
            response = auditor.invoke({"code": code, "topk": self.topk})
            self.logger.info(f'response from auditor {self.llm_auditors[i]}: {response}')
            responses.append(response)
            write_to_file(f"{self.result_dir}/{self.output}_{self.llm_auditors[i]}_k{self.topk}_n{self.n_auditors}/{self.output}_auditor_{i+1}.json", response, write='a')
        return responses

    def run_critic(self, code, vulnerabilities):
        response = self.critic_chain.invoke({"auditor_resp": str(vulnerabilities)})
        write_to_file(f"{self.result_dir}/{self.output}_{self.llm_critic.model_id}_critic.json", response)
        self.logger.info(f'response from critic: {response}')
        return response
    
    def run_ranker(self, vulnerability) -> list:
        response = self.ranker_chain.invoke({"topk": self.topk, "vulnerability": vulnerability})
        self.logger.info(f'response from ranker: {response}')
        write_to_file(f"{self.result_dir}/{self.output}_{self.llm_ranker.model_id}_rank.json", str(response))
        return response

    def save_run(self):
        run_info = f'''Run Info:
            auditor_template_path={self.auditor_template_path}, 
            critic_template_path={self.critic_template_path}, 
            ranker_template_path={self.ranker_template_path}, 
            topk={self.topk}, 
            log_dir={self.log_dir}, 
            result_dir={self.result_dir}, 
            output={self.output}, 
            n_auditors={self.n_auditors}, 
            '''
        for i, auditor in enumerate(self.llm_auditors):
            run_info += f'Auditor {i+1}: model_id={auditor.model_name}, params={auditor.model_params}\n'
        run_info += f'Critic: model_id={self.llm_critic.model_name}, params={self.llm_critic.model_params}\n'
        run_info += f'Ranker: model_id={self.llm_ranker.model_name}, params={self.llm_ranker.model_params}\n'
        
        self.logger.info(run_info)
        write_to_file(f"{self.result_dir}/{self.output}_run_info.txt", run_info)

    def run_pipeline(self, code_path="", topk="3", output="output", n_auditors=1,
                 auditor_template_path='templates/auditor_v1.txt', 
                 critic_template_path='templates/critic_v1.txt', 
                 ranker_template_path='templates/topk.txt'):
        with open(code_path, "r") as file:
            code = file.read()
        self.output = output
        self.topk = topk

        # set prompt path
        self.auditor_template_path = auditor_template_path
        self.critic_template_path = critic_template_path
        self.ranker_template_path = ranker_template_path

        # Initialize and set prompt templates
        self.auditor_prompt = self.set_template(self.auditor_template_path, ['code'])
        self.critic_prompt = self.set_template(self.critic_template_path, ['code', 'vulnerability'])
        self.ranker_prompt = self.set_template(self.ranker_template_path, ['vulnerability', 'topk'])
        
        # Create RunnableSequence instances
        self.auditor_chain = [self.auditor_prompt | auditor for auditor in self.llm_auditors]
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
    # Example with multiple auditors and models
    from ChatOllama import ChatOllamaLLM
    
    auditor_models = [ChatOllamaLLM(model_id="deepseek-coder-v2",model_params_path="config/llama.json")]  # Add more models if needed
    critic_model = ChatOllamaLLM(model_id="deepseek-coder-v2",model_params_path="config/llama.json")
    ranker_model = ChatOllamaLLM(model_id="deepseek-coder-v2",model_params_path="config/llama.json")
    
    # Initialize the detector with multiple auditors
    detector = BugScanner(auditor_models=auditor_models,
                        critic_model=critic_model,
                        ranker_model=ranker_model,
                        auditor_template_path='templates/auditor_v1.txt',
                        critic_template_path='templates/critic_v1.txt',
                        ranker_template_path='templates/topk.txt')

    # Run the pipeline with the sample code
    detector.run_pipeline(code_path="data/2018-10299.sol", topk="10", output="2018-10299")


if __name__ == "__main__":
    main()
