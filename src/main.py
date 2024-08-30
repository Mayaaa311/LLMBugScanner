from lens.BugScanner import BugScanner
from lens.ChatOllama import ChatOllamaLLM
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
    auditor_models = [
                      ChatOllamaLLM(model_id="starcoder2",model_params_path="config/llama.json"),
                      ]  # Add more models if needed
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
    # detector.run_pipeline(code_path="data/2018-10299.sol", topk="10",  output="2018-10299_k10_n1_t0_test", result_dir = "result_10299")
    # detector.run_pipeline(code_path="data/2018-10299.sol", topk="3",  output="2018-10299", result_dir = "result_10299")
    # ===================================
    auditor_models = [
                        ChatOllamaLLM(model_id="deepseek-coder-v2",model_params_path="config/temp0.9.json"),
                        ChatOllamaLLM(model_id="codeqwen",model_params_path="config/temp0.9.json"),
                        ChatOllamaLLM(model_id="llama3",model_params_path="config/temp0.9.json"),
                        ChatOllamaLLM(model_id="codellama",model_params_path="config/temp0.9.json"),
                        ChatOllamaLLM(model_id="starcoder2",model_params_path="config/temp0.9.json"),
                        ]
    # Initialize the detector with multiple auditors
    detector = BugScanner(auditor_models=auditor_models,
                        critic_model=critic_model,
                        ranker_model=ranker_model,
                        auditor_template_path='templates/auditor_v1.txt',
                        critic_template_path='templates/critic_v1.txt',
                        ranker_template_path='templates/topk.txt')

    # Run the pipeline with the sample code
    detector.run_pipeline(code_path="data/2018-10299.sol", topk="3",  output="2018-10299_k3_n5_t9", result_dir = "result_10299")
    detector.run_pipeline(code_path="data/2018-10299.sol", topk="10",  output="2018-10299_k10_n5_t9", result_dir = "result_10299")



if __name__ == "__main__":
    main()
