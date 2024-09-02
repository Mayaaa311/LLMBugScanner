from lens import BugScanner
from lens import ChatOllamaLLM
from lens import Huggingface_LLM
from lens import read_file_to
def main():
    # currently testing on models:
    # model_id = "deepseek-coder-v2"
    # model_id = "codeqwen",
    # model_id = "llama3",
    # model_id = "codellama",
    # model_id = "Nxcode",

    # ChatOllamaLLM(model_id="deepseek-coder-v2",model_params_path="config/temp0.9.json"),
    # ChatOllamaLLM(model_id="codeqwen",model_params_path="config/temp0.9.json"),
    # ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.9.json"),
    # ChatOllamaLLM(model_id="codellama",model_params_path="config/temp0.9.json"),
    # ChatOllamaLLM(model_id="starcoder2",model_params_path="config/temp0.9.json"),
    # Huggingface_LLM(model_id="AlfredPros/CodeLlama-7b-Instruct-Solidity", model_params_path = "config/temp0.json")

    critic_model = ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.json")
    ranker_model = ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.json")

    auditor_models = [
                        # Huggingface_LLM(model_id="AlfredPros/CodeLlama-7b-Instruct-Solidity", model_params_path = "config/temp0.json")
                        # ChatOllamaLLM(model_id="deepseek-coder-v2",model_params_path="config/temp0.json"),
                        # ChatOllamaLLM(model_id="codeqwen",model_params_path="config/temp0.9.json"),
                        ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.json"),
                        # ChatOllamaLLM(model_id="codellama",model_params_path="config/temp0.9.json"),
                        # ChatOllamaLLM(model_id="starcoder2",model_params_path="config/temp0.9.json"),
                        ]
    # Initialize the detector with multiple auditors
    detector = BugScanner(
                        # auditor_models=auditor_models,
                        critic_model=critic_model,
                        # ranker_model=ranker_model,
                        # auditor_template_path='templates/auditor_v1.txt',
                        critic_template_path='templates/critic_v1.txt',
                        # ranker_template_path='templates/topk.txt'
                        )

    # Run the pipeline with the sample code
    # detector.run_pipeline(code_path="data/2018-10299.sol", topk="10",  output="2018-10299_codellama-S-k10-prompt2", result_dir = "result_10299")
    
    outputs = read_file_to(["result_10299/2018-10299_k3_n5_t0/codellama_auditor.json"
                            ,"result_10299/2018-10299_k3_n5_t0/codeqwen_auditor.json",
                            # "result_10299/2018-10299_k3_n5_t0/deepseek-coder-v2_auditor.json",
                            # "result_10299/2018-10299_k3_n5_t0/llama3_auditor.json",
                            # "result_10299/2018-10299_k3_n5_t0/starcoder2_auditor.json"
                            ])
    # detector.create_chain("templates/auditor_v1.txt","templates/critic_v1.txt","templates/topk.txt")
    detector.run_critic(str(outputs),"result_10299/2018-10299_k3_n5_t0")


if __name__ == "__main__":
    main()
