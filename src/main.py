from lens.detector import Detector
def main():
        # model_id = "codeqwen",
        # model_id = "llama3",
        # model_id = "codellama",
        # model_id = "Nxcode",
    # Initialize the detector
    deepseek = Detector(
        model_id= "deepseek-coder-v2",
        auditor_template_path='templates/auditor_v1.txt',
        critic_template_path='templates/critic_v1.txt',
        log_dir='log',
        result_dir='result'
    )
    # Run the pipeline with the sample code
    deepseek.run_pipeline(code_path = "data/2018-10299.sol", topk="10", n_auditors = 1, output= '2018-10299')
    deepseek.run_pipeline(code_path = "data/2018-10299.sol", topk="3", n_auditors = 1, output= '2018-10299')
    deepseek.run_pipeline(code_path = "data/2018-10299.sol", topk="all", n_auditors = 1, output= '2018-10299')





if __name__ == "__main__":
    main()
