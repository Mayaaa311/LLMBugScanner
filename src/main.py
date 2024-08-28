from lens.BugScanner import BugScanner
from lens.ChatOllama import ChatOllamaLLM
def main():
    # currently testing on models:
    # model_id = "deepseek-coder-v2"
    # model_id = "codeqwen",
    # model_id = "llama3",
    # model_id = "codellama",
    # model_id = "Nxcode",
    
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
