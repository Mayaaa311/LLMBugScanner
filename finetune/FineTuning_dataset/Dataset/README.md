#  Ethereum smart contract dataset

We obtain our dataset by crawling Etherscan verified contracts, which are real-world smart contracts deployed on Ethereum Mainnet.

Our final dataset contains a total 12,515 smart contacts that have source code and concentrates on eight types of vulnerabilities, namely:

1. Timestamp dependency

2. Block number dependency

3. Dangerous delegatecall  

4. Ether frozen

5. Unchecked external call  

6. Reentrancy  

7. Integer overflow/underflow  

8. Dangerous Ether strict equality

The ground truth labels (in the file `ground truth label`) of smart contracts in the dataset are confirmed based on defined vulnerability-specific patterns and further manual inspection.


