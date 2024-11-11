 
pragma solidity >0.5.0 <0.8.0;

 
import { Lib_AddressManager } from "./Lib_AddressManager.sol";

 
contract Lib_ResolvedDelegateProxy {

     


     
     
     
     
     
     
     
     
    mapping(address=>string) private implementationName;
    mapping(address=>Lib_AddressManager) private addressManager;


     

     
    constructor(
        address _libAddressManager,
        string memory _implementationName
    )
    {
        addressManager[address(this)] = Lib_AddressManager(_libAddressManager);
        implementationName[address(this)] = _implementationName;
    }


     

    fallback()
        external
    {
        address target = addressManager[address(this)].getAddress((implementationName[address(this)]));
        require(
            target != address(0),
            "Target address must be initialized."
        );

        (bool success, bytes memory returndata) = target.delegatecall(msg.data);

        if (success == true) {
            assembly {
                return(add(returndata, 0x20), mload(returndata))
            }
        } else {
            assembly {
                revert(add(returndata, 0x20), mload(returndata))
            }
        }
    }
}
