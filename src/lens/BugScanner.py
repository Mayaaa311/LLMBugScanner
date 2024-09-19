import json
import logging
import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
import torch
from lens.utils import write_to_file
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("using", device)


class BugScanner:
    def __init__(self, auditor_models = None, critic_model = None, ranker_model = None, auditor_template_path=None, 
                 critic_template_path=None, 
                 ranker_template_path=None,
                 log_dir='logger', result_dir='result'):
        self.output = "output"
        self.result_dir = result_dir
        self.auditor_template_path = None
        self.critic_template_path = None
        self.ranker_template_path = None
        self.llm_auditors = None
        self.llm_critic = None
        self.llm_ranker = None
        self.critic_chain = None
        self.auditor_chain = None
        self.ranker_chain = None
        self.topk = None
        self.ranked_vulnerabilities = ""   
        
        # Create the logger directory if it doesn't exist
        os.makedirs(log_dir, exist_ok=True)
        self.log_dir = log_dir
        
        # Set the log filename with the current date and time
        log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
        log_path = os.path.join(log_dir, log_filename)
        
        # Initialize logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=log_path, filemode='w')
        self.logger = logging.getLogger(__name__)
        
        self.load_all_models(auditor_models, critic_model, ranker_model)
        self.create_chain(auditor_template_path, critic_template_path, ranker_template_path)
    def load_all_models(self, auditor_models, critic_model, ranker_model):
        # Initialize the models using the provided classes and parameters
        if auditor_models is not None:
            self.llm_auditors = auditor_models
            # Load the models
            for auditor in self.llm_auditors:
                auditor.load_model()
        
        if critic_model is not None:
            self.llm_critic = critic_model
            self.llm_critic.load_model()
        if ranker_model is not None:
            self.llm_ranker = ranker_model
            self.llm_ranker.load_model()
    def set_template(self, template_path, input_var):
        with open(template_path, 'r') as file:
            template = file.read()
        return PromptTemplate(input_variables=input_var, template=template)
    
    def create_chain(self, auditor_template_path, critic_template_path, ranker_template_path):
           # set prompt path
        if auditor_template_path is not None:
            self.auditor_template_path = auditor_template_path        
            self.auditor_prompt = self.set_template(self.auditor_template_path, ['code','topk'])
            self.auditor_chain = [self.auditor_prompt | auditor for auditor in self.llm_auditors]

        if critic_template_path is not None: 
            self.critic_template_path = critic_template_path
            self.critic_prompt = self.set_template(self.critic_template_path, ['code', 'vulnerability'])
            self.critic_chain = self.critic_prompt | self.llm_critic
        if ranker_template_path is not None:
            self.ranker_template_path = ranker_template_path
            self.ranker_prompt = self.set_template(self.ranker_template_path, ['vulnerability', 'topk'])
            self.ranker_chain = self.ranker_prompt | self.llm_ranker
    
        
    def run_auditor(self, code, write_to):
        responses = []
        input_dict = {"code": code, "topk": self.topk}
        for i, auditor in enumerate(self.auditor_chain):
            response = auditor.invoke(input_dict)
            self.logger.info(f'response from auditor {self.llm_auditors[i]}: {response}')
            responses.append(response)
            print("Auditor response written to : ", write_to+f"/{self.llm_auditors[i].model_id}_auditor.json")
            write_to_file(write_to+f"/{self.llm_auditors[i].model_id}_auditor.json", response, write='w')
        return responses

    def run_critic(self, vulnerabilities, write_to, code = None):

        if code is not None: #currently not used
            response = self.critic_chain.invoke({"auditor_resp": str(vulnerabilities),"code":code})
        else:
            response = self.critic_chain.invoke({"auditor_resp": str(vulnerabilities)})
        write_to_file(write_to+f"/{self.llm_critic.model_id}_critic.json", response)
        self.logger.info(f'response from critic: {response}')
        return response
    
    def run_ranker(self, vulnerability, write_to) -> list:
        response = self.ranker_chain.invoke({"topk": self.topk, "vulnerability": vulnerability})
        self.logger.info(f'response from ranker: {response}')
        write_to_file(write_to+f"/{self.llm_ranker.model_id}_rank.json", str(response))
        return response

    def save_run(self,write_to):
        run_info = f'''Run Info:
            auditor_template_path={self.auditor_template_path}, 
            critic_template_path={self.critic_template_path}, 
            ranker_template_path={self.ranker_template_path}, 
            topk={self.topk}, 
            log_dir={self.log_dir}, 
            result_dir={self.result_dir}, 
            output={self.output}, 
            n_auditors={len(self.llm_auditors)}, 
            '''
        if self.llm_auditors is not None:
            for i, auditor in enumerate(self.llm_auditors):
                run_info += f'Auditor {i+1}: model_id={auditor.model_id}, params={auditor.model_params}\n'
        if self.llm_critic is not None:
            run_info += f'Critic: model_id={self.llm_critic.model_id}, params={self.llm_critic.model_params}\n'
        if self.llm_ranker is not None:
            run_info += f'Ranker: model_id={self.llm_ranker.model_id}, params={self.llm_ranker.model_params}\n'
        
        self.logger.info(run_info)
        write_to_file(write_to+"/run_info.txt", run_info)

    def run_pipeline(self, code_path="", topk="3", output=None, result_dir = None):
        with open(code_path, "r") as file:
            code = file.read()
        if output is not None:
            self.output = output
        self.topk = topk
        if result_dir is not None:
            self.result_dir = result_dir
        write_to = f"{self.result_dir}/{self.output}"

        
        # Step 1: Generate vulnerabilities using auditors
        vulnerabilities = self.run_auditor(code, write_to)
        if(self.critic_chain is not None):
        # Step 2: Evaluate vulnerabilities using critic   
            evaluations = self.run_critic( vulnerabilities, write_to, code = code)
        if(self.ranker_chain is not None):
        # Step 3: Rank vulnerabilities based on critic's evaluation
            self.ranked_vulnerabilities = self.run_ranker(evaluations, write_to)
        self.save_run(write_to)

        return self.ranked_vulnerabilities


# def main():
#     # Example with multiple auditors and models
#     from ChatOllama import ChatOllamaLLM
#     # auditor_models = [
#     #                 ChatOllamaLLM(model_id="deepseek-coder-v2",model_params_path="config/temp0.9.json"),
#     #                 ChatOllamaLLM(model_id="codeqwen",model_params_path="config/temp0.9.json"),
#     #                 ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.9.json"),
#     #                 ChatOllamaLLM(model_id="codellama",model_params_path="config/temp0.9.json"),
#     #                 ChatOllamaLLM(model_id="starcoder2",model_params_path="config/temp0.9.json"),
#     #                 ]
#     auditor_models = [ChatOllamaLLM(model_id="codellama",model_params_path="config/llama.json")]  # Add more models if needed
#     critic_model = ChatOllamaLLM(model_id="codellama",model_params_path="config/llama.json")
#     ranker_model = ChatOllamaLLM(model_id="codellama",model_params_path="config/llama.json")
    
#     # Initialize the detector with multiple auditors
#     detector = BugScanner(auditor_models=auditor_models,
#                         critic_model=critic_model,
#                         ranker_model=ranker_model,
#                         auditor_template_path='templates/auditor_v1.txt',
#                         critic_template_path='templates/critic_v1.txt',
#                         ranker_template_path='templates/topk.txt')

#     # Run the pipeline with the sample code
#     detector.run_pipeline(code_path="data/2018-10299.sol", topk="2",  output="2018-10299-codellama-test-k2", result_dir = "result_10299")


# if __name__ == "__main__":
#     main()
