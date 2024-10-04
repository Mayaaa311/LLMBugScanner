import json
import logging
import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
import torch
from lens.Huggingface import Huggingface_LLM
from lens.utils import write_to_file
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("using", device)


class BugScanner:
    def __init__(self, auditor_models = None, critic_model = None, ranker_model = None, summarizer_model = None,
                 log_dir='logger', result_dir='result'):
        self.output = "output"
        self.result_dir = result_dir
        self.llm_auditors = None
        self.llm_critic = None
        self.llm_ranker = None
        if summarizer_model is None:
            summarizer_model =  Huggingface_LLM(model_id = "AlfredPros/CodeLlama-7b-Instruct-Solidity", prompt_path= 'templates/summarizer.txt')
        self.llm_summarizer = None
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
        
        self.load_all_models(auditor_models, critic_model, ranker_model,summarizer_model)

    def load_all_models(self, auditor_models, critic_model, ranker_model, summarizer_model):
        # Initialize the models using the provided classes and parameters
        if auditor_models is not None:
            self.llm_auditors = auditor_models
            # Load the models
            for auditor in self.llm_auditors:
                auditor.load_model()
                auditor.load_template(['code','topk'])
        
        if critic_model is not None:
            self.llm_critic = critic_model
            self.llm_critic.load_model()
            self.llm_critic.load_template(['code', 'vulnerability'])
        if ranker_model is not None:
            self.llm_ranker = ranker_model
            self.llm_ranker.load_model()
            self.llm_ranker.load_template(['vulnerability', 'topk'])
        if summarizer_model is not None:
            self.llm_summarizer = summarizer_model
            self.llm_summarizer.load_model()
            self.llm_summarizer.load_template(['content'])
        
    def run_auditor(self, code, write_to):
        responses = []
        input_dict = {"code": code, "topk": self.topk}
        for i, auditor in enumerate(self.llm_auditors):
            response = auditor.invoke(input_dict)
            responses.append(response)
            print("Auditor response written to : ", write_to+f"/{self.llm_auditors[i].model_id.replace('/','_')}_auditor.json")
            write_to_file(write_to+f"/{self.llm_auditors[i].model_id.replace('/','_')}_auditor.json", response, write='w')
        return responses

    def run_critic(self, vulnerabilities, write_to, code = None):
        responses = []
        for i,vulnerability in enumerate(vulnerabilities):
            if code is not None: 
                response = self.llm_critic.invoke({"auditor_resp": vulnerability,"code":code})
            else:
                response = self.llm_critic.invoke({"auditor_resp": vulnerability})
            print("Critic response written to : ", write_to+f"/critic/{self.llm_critic.model_id.replace('/','_')}_critic_{i}.json")
            write_to_file(write_to+f"/{self.llm_critic.model_id.replace('/','_')}_critic_{i}.json", response)
            responses.append(response)
        return responses
    
    def run_ranker(self, vulnerability, write_to) -> list:
        response = self.llm_ranker.invoke({"topk": self.topk, "vulnerability": vulnerability})
        write_to_file(write_to+f"/{self.llm_ranker.model_id.replace('/','_')}_rank.json", str(response))
        return response

    def run_summarizer(self, content, write_to) -> list:
        response = self.llm_ranker.invoke({"content": content})
        write_to_file(write_to+f"/{self.llm_ranker.model_id.replace('/','_')}_summarized.json", str(response))
        return response

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
        vulnerabilities = self.run_auditor(code, write_to+"/auditor")

        summarized_vulnerabilities = []
        for vul in vulnerabilities:
            summarized_vulnerabilities.append(self.run_summarizer(vul, write_to+"/auditor"))

        if(self.llm_critic is not None):
        # Step 2: Evaluate vulnerabilities using critic   
            evaluations = self.run_critic( summarized_vulnerabilities, write_to+"/critic", code = code)

        summarized_eval = []
        for eval in evaluations:
            summarized_eval.append(self.run_summarizer(eval, write_to+"/critic"))

        if(self.llm_ranker is not None):
        # Step 3: Rank vulnerabilities based on critic's evaluation
            ranked_vulnerabilities = self.run_ranker(summarized_eval, write_to+"/ranker")


        self.llm_summarizer.load_template(['dataname','input'], prompt_path = 'templates/output_formatter.txt')
        summarized_output = self.llm_ranker.invoke({"dataname":code_path.split('/')[-1], "input": ranked_vulnerabilities})
        write_to_file(write_to+f"/{self.llm_ranker.model_id.replace('/','_')}_summarized.csv", summarized_output)

        return self.ranked_vulnerabilities

