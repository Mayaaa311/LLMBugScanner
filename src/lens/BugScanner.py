import json
import logging
import os
from datetime import datetime
from langchain_core.prompts import PromptTemplate
# from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
import torch
from lens.Huggingface import Huggingface_LLM
from lens.utils import write_to_file
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print("using", device)


class BugScanner:
    def __init__(self, auditor_models = None, critic_model = None, ranker_model = None, summarizer_model = None,
                 log_dir='logger', result_dir='result'):
        self.result_dir = result_dir
        self.llm_auditors = auditor_models
        self.llm_critic = critic_model
        self.llm_ranker = ranker_model
        self.llm_summarizer = summarizer_model
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
        
        # self.load_all_models(auditor_models, critic_model, ranker_model,summarizer_model)

    def load_all_models(self, auditor_models, critic_model, ranker_model, summarizer_model):
        # Initialize the models using the provided classes and parameters

        if auditor_models:
            # Load the models
            for auditor in self.llm_auditors:
                auditor.load_model()
                auditor.load_template(['code','topk'])
        
        if critic_model:
            self.llm_critic.load_model()
            self.llm_critic.load_template(['code', 'vulnerability'])
        if ranker_model:
            self.llm_ranker.load_model()
            self.llm_ranker.load_template(['vulnerability', 'topk'])
        if summarizer_model:
            self.llm_summarizer.load_model()
            self.llm_summarizer.load_template(['content'])
        
    def run_auditor(self, code, write_to):
        input_dict = {"code": code, "topk": self.topk}
        for i, auditor in enumerate(self.llm_auditors):
            if not os.path.isfile(write_to+f"/{self.llm_auditors[i].model_id.replace('/','_')}_auditor.json"):
                response = auditor.invoke(input_dict)
                write_to_file(write_to+f"/{self.llm_auditors[i].model_id.replace('/','_')}_auditor_{i}.json", response, write='w')
                print("Auditor response written to : ", write_to+f"/{self.llm_auditors[i].model_id.replace('/','_')}_auditor.json")
            else:
                print("Auditor response found: ", write_to+f"/{self.llm_auditors[i].model_id.replace('/','_')}_auditor.json")
            

    def run_critic(self, vulnerabilities, write_to, code = None, idx = 0):
        if not os.path.isfile(write_to+f"/{self.llm_critic.model_id.replace('/','_')}_critic_{idx}.json"):
            if code is not None: 
                print("using code in critic!")
                response = self.llm_critic.invoke({"auditor_resp": vulnerabilities,"code":code})
            else:
                response = self.llm_critic.invoke({"auditor_resp": vulnerabilities})
            print("Critic response written to : ", write_to+f"/{self.llm_critic.model_id.replace('/','_')}_critic_a{idx}.json")
            write_to_file(write_to+f"/{self.llm_critic.model_id.replace('/','_')}_critic_{idx}.json", response)
        else:
            print("Critic response found : ", write_to+f"/{self.llm_critic.model_id.replace('/','_')}_critic_a{idx}.json")

    
    def run_ranker(self, vulnerability, write_to) -> list:
        response = None
        if not os.path.isfile(write_to+f"/{self.llm_ranker.model_id.replace('/','_')}_rank.json"):
            response = self.llm_ranker.invoke({"topk": self.topk, "vulnerability": vulnerability})
            write_to_file(write_to+f"/{self.llm_ranker.model_id.replace('/','_')}_rank.json", str(response))
        return response

    def run_summarizer(self, content, write_to,idx = 0) -> list:
        if not os.path.isfile(write_to+f"/{self.llm_summarizer.model_id.replace('/','_')}_summarized.json"):
            response = self.llm_summarizer.invoke({"content": content})
            write_to_file(write_to+f"/{self.llm_summarizer.model_id.replace('/','_')}_summarized.json", str(response))
        return write_to+f"/{self.llm_summarizer.model_id.replace('/','_')}_summarized_{idx}.json"
    
    def run_llm_on_dir_list(self, dir_list, func, append_name, *args, **kwargs):
        result = []
        for dir in dir_list:
            files = [f for f in os.listdir(dir)]
            name = dir.split('/')
            write_to = '/'.join(name[:-1]) + '/' + append_name

            for file in files:
                file_path = os.path.join(dir, file)  
                auditor_idx =  file.split('/')[-1].split('.')[-2].split('_')[-1]
                with open(file_path, "r") as f:
                    o = f.read()
                    func(o, write_to, *args, **kwargs, idx = auditor_idx) 

            result.append(write_to)
        return result
    
    def run_batch_auditor(self, code_folder):
        code_path = [f for f in os.listdir(code_folder) if f.endswith('.sol')]
        auditor_result_dirs = [] 
        self.load_all_models(True, False, False, False)
        for file in code_path:
            # Step 1: Generate vulnerabilities using auditors
            data_path = os.path.join(code_folder, file)
            with open(data_path, "r") as f:
                code = f.read()
                name = file.split('/')[-1].rsplit('.', 1)[0]
                write_to = f"{self.result_dir}/{name}"
                self.run_auditor(code, write_to+"/auditor")
                auditor_result_dirs.append(write_to+"/auditor")

        for model in self.llm_auditors:
            del model.model  # This removes the model from memory
            torch.cuda.empty_cache()  
        
        print("all auditor output write to : ", auditor_result_dirs)
        return auditor_result_dirs
    def run_batch_summarizer1(self, auditor_result_dirs):

        self.load_all_models(False, False, False, True)
        summarized_vulnerabilities_dirs = self.run_llm_on_dir_list(auditor_result_dirs, self.run_summarizer, "auditor_summary")
        print("all auditor summary write to : ", summarized_vulnerabilities_dirs)
        return summarized_vulnerabilities_dirs

    def run_batch_critic(self, summarized_vulnerabilities_dirs,code_folder):
        self.load_all_models(False, True, False, False)
        critic_output_dir = []
        for dir in summarized_vulnerabilities_dirs:
            files = [f for f in os.listdir(dir)]
            name = dir.split('/')
            write_to = '/'.join(name[:-1]) + '/' + "critic"
            
            code_file_name = code_folder+'/'+name[-2]+'.sol'

            for file in files:
                file_path = os.path.join(dir, file)  
                auditor_idx =  file.split('/')[-1].split('.')[-2].split('_')[-1]
                print("FILEPATH: ", file_path)
                with open(file_path, "r") as f:
                    o = f.read()
                    with open(code_file_name, "r") as f1:
                        code = f1.read()
                        self.run_critic(o, write_to, code = code, idx = auditor_idx) 

            critic_output_dir.append(write_to)

        print("all critic write to : ", critic_output_dir)
        
        del self.llm_critic.model  # This removes the model from memory
        torch.cuda.empty_cache()  

        return critic_output_dir
    def run_batch_summarizer2(self, critic_output_dir):
        if self.llm_summarizer.model is None:
            self.load_all_models(False, False, False, True)
        self.llm_summarizer.load_template(['content'], prompt_path = 'templates/summarizer2.txt')
        summarized_vulnerabilities_dirs = self.run_llm_on_dir_list(critic_output_dir, self.run_summarizer, "critic_summary")
        print("all critic summary write to : ", summarized_vulnerabilities_dirs)
        return summarized_vulnerabilities_dirs

    def run_batch_ranker(self, summarized_vulnerabilities_dirs):
        self.load_all_models(False, False, True, False)
        
        ranker_dirs = []
        if(self.llm_ranker is not None):
            for dir in summarized_vulnerabilities_dirs:
                files = [f for f in os.listdir(dir)]
                name = dir.split('/')
                write_to = '/'.join(name[:-1])+'/ranker'
                critic_folder_data = []
                
                for file in files:
                    file_path = os.path.join(dir, file)  
                    with open(file_path, "r") as f:
                        o = f.read()
                        critic_folder_data.append(o)
                self.run_ranker(str(critic_folder_data), write_to) 
                ranker_dirs.append(write_to)
        print("ranker output write to : ", ranker_dirs)
        return ranker_dirs

    def run_batch_output_formatter(self, ranker_dirs):
        if self.llm_summarizer.model is None:
            self.load_all_models(False, False, False, True)
        self.llm_summarizer.load_template(['dataname','inputjson'], prompt_path = 'templates/output_formatter.txt')
        sum_dirs = []
        for dir in ranker_dirs:
            files = [f for f in os.listdir(dir)]
            name = dir.split('/')
            write_to = '/'.join(name[:-1])+'/final_output'

            i = 0
            for file in files:
                file_path = os.path.join(dir, file)  
                with open(file_path, "r") as f:
                    o = f.read() 
                    if not os.path.isfile(write_to+f"/{self.llm_summarizer.model_id.replace('/','_')}_summarized{i}.csv"):
                        response = self.llm_summarizer.invoke({"dataname": name[-2], "inputjson":o})
                        write_to_file(write_to+f"/{self.llm_summarizer.model_id.replace('/','_')}_summarized{i}.csv", str(response))
            sum_dirs.append(write_to)
        return sum_dirs

    def recreate_subfolder_name_list(self, folder, name):
        files = [f for f in os.listdir(folder)]
        final =[]
        for i in files:
            final.append(folder+'/'+i+'/'+name)
        return final

    def run_pipeline(self, code_folder, result_dir, topk="3"):

        self.topk = topk
        if result_dir is not None:
            self.result_dir = result_dir

        # -------------------------------RUN AUDITOR---------------------------------
        auditor_result_dirs =  self.run_batch_auditor(code_folder)
         # -------------------------------RUN AUDITOR SUMMARIZER---------------------------------
        summarized_vulnerabilities_dirs = self.run_batch_summarizer1(auditor_result_dirs)
        # -------------------------------RUN CRITIC---------------------------------
        critic_output_dir = self.run_batch_critic(summarized_vulnerabilities_dirs, code_folder) 
        # -------------------------------RUN CRITIC SUMMARIZER---------------------------------
        summarized_vulnerabilities_dirs = self.run_batch_summarizer2(critic_output_dir)
        # -------------------------------RUNNING RANKER---------------------------------
        ranker_dirs = self.run_batch_ranker(summarized_vulnerabilities_dirs)
        # -------------------------------RUNNING FINAL SUMMARIZER---------------------------------
        self.run_batch_output_formatter(ranker_dirs)
    


