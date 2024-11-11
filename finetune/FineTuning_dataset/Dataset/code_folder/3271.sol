pragma solidity ^0.4.24;

 
 
 
 
 
 
 
 
 
 
 

contract hodlEthereum {
    event Hodl(address indexed hodler, uint indexed amount);
    event Party(address indexed hodler, uint indexed amount);
    mapping (address => uint) public hodlers;

     
    uint constant partyTime = 1535760000;

     
    function hodl() payable public {
        hodlers[msg.sender] += msg.value;
        emit Hodl(msg.sender, msg.value);
    }

     
    function party() public {
        require (block.timestamp > partyTime && hodlers[msg.sender] > 0);
        uint value = hodlers[msg.sender];
        hodlers[msg.sender] = 0;
        msg.sender.transfer(value);
        emit Party(msg.sender, value);
    }
}