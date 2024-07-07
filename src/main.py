from sandbox.bug_detector import Detector

detector = Detector(
    # model_id="TheBloke/Llama-2-7B-GGUF",
    # model_file="llama-2-7b.Q5_K_M.gguf"
    # model_file="llama-2-7b.Q3_K_M.gguf"
    model_path="models/llama-2-7b.Q5_K_M.gguf"
)

sample_code = """
pragma solidity ^0.8.0;
mapping(address => uint256) public balances;

function deposit() public payable {
    balances[msg.sender] += msg.value;
}

function withdraw(uint256 amount) public {
    require(balances[msg.sender] >= amount, "Insufficient balance");
    payable(msg.sender).transfer(amount);
    balances[msg.sender] -= amount;
}
"""

vulnerabilities = detector.run_pipeline(sample_code)
for vulnerability in vulnerabilities:
    print(vulnerability)
    detector.logger.info(f'Ranked Vulnerability: {json.dumps(vulnerability, indent=2)}')

detector.save_results()  # Save results to default result folder

# Or save to a specific path
# detector.save_results(path="path/to/your/file.txt")

