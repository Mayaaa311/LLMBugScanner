from lens.llama_detector import Detector
def main():
    # Define the file path
    file_path = "data/2018-10666.sol"
    sample_code=""
    # Read the file content
    with open(file_path, "r") as file:
        sample_code = file.read()

    # Initialize the detector
    detector = Detector(
        model_id= "codellama",
        auditor_template_path='templates/auditor_v1.txt',
        critic_template_path='templates/critic_v1.txt',
        log_dir='log',
        result_dir='result',
        output = '2018-10666',
        topk=5,
        n_auditors=2,
    )

    # Run the pipeline with the sample code
    detector.run_pipeline(sample_code)
    detector.save_results()

if __name__ == "__main__":
    main()
