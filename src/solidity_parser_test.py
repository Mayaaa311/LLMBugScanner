
from lens.utils import *
# Usage example
solidity_file = "data_full/CVE_clean/2018-10299.sol"
target_function = "batchTransfer"
related_functions = find_related_functions(solidity_file, target_function)

# Print function names and structures
for func_name, func_node in related_functions.items():
    print(f"Function Name: {func_name}")
    print(json.dumps(func_node, indent=2))  # Pretty-printing the function node JSON
