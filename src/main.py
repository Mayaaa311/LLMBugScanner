from lens import BugScanner
from lens import ChatOllamaLLM
from lens import Huggingface_LLM
from lens import LlamaCpp_LLM
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
    critic_model =  ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.json")
    ranker_model = ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.json")

    auditor_models = [
                        # LlamaCpp_LLM(model_id="bartowski/Nxcode-CQ-7B-orpo-GGUF",
	                    #             model_path="Nxcode-CQ-7B-orpo-IQ1_M.gguf",model_params_path="config/temp0.json")
                        # Huggingface_LLM(model_id="AlfredPros/CodeLlama-7b-Instruct-Solidity", model_params_path = "config/temp0.json"),
                        Huggingface_LLM(model_id = "m-a-p/OpenCodeInterpreter-CL-13B", model_params_path = "config/temp0.json"),
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
    detector.run_pipeline(code_path="data/2018-10299.sol", topk="3",  output="2018-10299_OpenCodeInterpreter_k3", result_dir = "result_10299")

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
