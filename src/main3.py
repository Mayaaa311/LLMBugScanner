from lens import BugScanner
from lens import ChatOllamaLLM
from lens import Huggingface_LLM
from lens import LlamaCpp_LLM
from lens import pipeline_LLM
from lens import gemma_LLM
from lens import read_file_to
def main():
    # currently testing on models:
    # model_id = "deepseek-coder-v2"
    # model_id = "codeqwen",
    # model_id = "llama3",
    # model_id = "codellama",
    # model_id = "starcoder2",
    # model_id = "AlfredPros/CodeLlama-7b-Instruct-Solidity",
    # model_id = "bartowski/Nxcode-CQ-7B-orpo-GGUF"
    # model_id = "m-a-p/OpenCodeInterpreter-CL-13B"


    # ChatOllamaLLM(model_id="deepseek-coder-v2",model_params_path="config/temp0.json"),
    # ChatOllamaLLM(model_id="codeqwen",model_params_path="config/temp0.json"),
    # ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.json"),
    # ChatOllamaLLM(model_id="codellama",model_params_path="config/temp0.json"),
    # ChatOllamaLLM(model_id="starcoder2",model_params_path="config/temp0.json"),
    # Huggingface_LLM(model_id="AlfredPros/CodeLlama-7b-Instruct-Solidity", model_params_path = "config/temp0.json")
    # LlamaCpp_LLM(model_id="bartowski/Nxcode-CQ-7B-orpo-GGUF", model_path="Nxcode-CQ-7B-orpo-IQ1_M.gguf",model_params_path="config/temp0.json")

    # critic_model = Huggingface_LLM(model_id="AlfredPros/CodeLlama-7b-Instruct-Solidity", model_params_path = "config/temp0.json", quantize = True)
    # critic_model =  ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.json")
    # ranker_model = ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.json")

    auditor_models = [
                        # Huggingface_LLM(model_id="AlfredPros/CodeLlama-7b-Instruct-Solidity", model_params_path = "config/temp0.json"),
                        # Huggingface_LLM(model_id = "m-a-p/OpenCodeInterpreter-DS-6.7B"),
                        # Huggingface_LLM(model_id = "NTQAI/Nxcode-CQ-7B-orpo"),
                        # Huggingface_LLM(model_id="Artigenz/Artigenz-Coder-DS-6.7B"),
                        # Huggingface_LLM(model_id="bigcode/starcoder2-15b"),
                        # Huggingface_LLM(model_id="deepseek-ai/DeepSeek-Coder-V2-Lite-Instruct"),
                        pipeline_LLM(model_id="Qwen/CodeQwen1.5-7B"),
                        pipeline_LLM(model_id="meta-llama/Llama-3.1-8B-Instruct"),
                        pipeline_LLM(model_id="meta-llama/CodeLlama-7b-hf"),
                        # Huggingface_LLM(model_id="WisdomShell/CodeShell-7B-Chat"),
                        # gemma_LLM(model_id="google/codegemma-7b"),

                        
                        # LlamaCpp_LLM(model_id="bartowski/Nxcode-CQ-7B-orpo-GGUF",
	                    #             model_path="Nxcode-CQ-7B-orpo-IQ1_M.gguf",model_params_path="config/temp0.json")


                        # ChatOllamaLLM(model_id="deepseek-coder-v2",model_params_path="config/temp0.json"),
                        # ChatOllamaLLM(model_id="codeqwen",model_params_path="config/temp0.json"),
                        # ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.json"),
                        # ChatOllamaLLM(model_id="codellama",model_params_path="config/temp0.json"),
                        # ChatOllamaLLM(model_id="starcoder2",model_params_path="config/temp0.json"),
                        ]
    # Initialize the detector with multiple auditors
    detector = BugScanner(
                        auditor_models=auditor_models,
                        # critic_model=critic_model,
                        # ranker_model=ranker_model,
                        auditor_template_path='templates/auditor_v1.txt',
                        # critic_template_path='templates/critic_v2.txt',
                        # ranker_template_path='templates/topk.txt'
                        )
    # detector.create_chain("templates/auditor_v1.txt","templates/critic_v1.txt","templates/topk.txt")
    # Run the pipeline with the sample code
    data_to_run = [
        # "data_full/CVE_clean/2018-18425.sol"
                #    "data_full/CVE_clean/2018-19830.sol", 
                   "data_full/CVE_clean/2019-15078.sol", 
                   "data_full/CVE_clean/2019-15079.sol"
                   ]
    for data in data_to_run:
        name = data.split('/')[-1].rsplit('.', 1)[0]
        detector.run_pipeline(code_path=data, topk="5",  output=name+"_auditor_only_k5", result_dir = "result_sep29")

    # outputs = read_file_to([
    #                         "result_10299/2018-10299_k3_n5_t0/codellama_auditor.json"
    #                         # "result_10299/2018-10299_k3_n5_t0/codeqwen_auditor.json",
    #                         # "result_10299/2018-10299_k3_n5_t0/deepseek-coder-v2_auditor.json",
    #                         # "result_10299/2018-10299_k3_n5_t0/llama3_auditor.json",
    #                         # "result_10299/2018-10299_k3_n5_t0/starcoder2_auditor.json"
    #                         ])
    # code = read_file_to(["data/2018-10299.sol"
    #                     ])
    # detector.run_critic(str(outputs),"result_10299/2018-10299_k3_n5_t0/critic2-codellama", code = str(code))


if __name__ == "__main__":
    main()
