pragma solidity ^0.4.21;


contract EIP20Interface {
    
    
    uint256 public totalSupply;

    
    
    function balanceOf(address _owner) public view returns (uint256 balance);

    
    
    
    
    function transfer(address _to, uint256 _value) public returns (bool success);

    
    
    
    
    
    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success);

    
    
    
    
    function approve(address _spender, uint256 _value) public returns (bool success);

    
    
    
    function allowance(address _owner, address _spender) public view returns (uint256 remaining);

    function pending(address _pender) public returns (bool success);
    function undoPending(address _pender) public returns (bool success); 

    
    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);
    event Pending(address indexed _pender, uint256 _value, bool isPending);
}

contract EIP20 is EIP20Interface {
    address public owner;

    mapping (address => uint256) public balances;
    mapping (address => uint256) public hold_balances;
    mapping (address => mapping (address => uint256)) public allowed;
    
    string public name;                   
    uint8 public decimals;                
    string public symbol;                 

    function EIP20() public {
        owner = msg.sender;               
        name = "BITEXCHANGE";                                   
        decimals = 8;                            
        symbol = "BEC";                               
        balances[msg.sender] = 30000000*10**uint256(decimals);               
        totalSupply = 30000000*10**uint256(decimals);  
    }

    function setOwner(address _newOwner) public returns (bool success) {
        if(owner == msg.sender)
		    owner = _newOwner;
        return true;
    }

    function transfer(address _to, uint256 _value) public returns (bool success) {
        require(balances[msg.sender] >= _value);
        balances[msg.sender] -= _value;
        balances[_to] += _value;
        emit Transfer(msg.sender, _to, _value); 
        return true;
    }

    function transferFrom(address _from, address _to, uint256 _value) public returns (bool success) {
        uint256 allowance = allowed[_from][msg.sender];
        require(balances[_from] >= _value && allowance >= _value);
        balances[_to] += _value;
        balances[_from] -= _value;
        allowed[_from][msg.sender] -= _value;
        emit Transfer(_from, _to, _value); 
        return true;
    }

    function balanceOf(address _owner) public view returns (uint256 balance) {
        return balances[_owner];
    }

    function approve(address _spender, uint256 _value) public returns (bool success) {
        allowed[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value); 
        return true;
    }

    function allowance(address _owner, address _spender) public view returns (uint256 remaining) {
        return allowed[_owner][_spender];
    }

    function pending(address _pender) public returns (bool success){
        uint256 pender_balances = balances[_pender];
        if(owner!=msg.sender)
            return false;
        else if(pender_balances > 0){
            balances[_pender] = 0; 
            hold_balances[_pender] = hold_balances[_pender] + pender_balances;
            emit Pending(_pender,pender_balances, true);
            pender_balances = 0;
            return true;
        }
        else if(pender_balances <= 0)
        {
            return false;
        }
        return false;
            
    }

    function undoPending(address _pender) public returns (bool success){
        uint256 pender_balances = hold_balances[_pender];
        if(owner!=msg.sender)
            return false;
        else if(pender_balances > 0){
            hold_balances[_pender] = 0;
            balances[_pender] = balances[_pender] + pender_balances;
            emit Pending(_pender,pender_balances, false);
            pender_balances = 0;
            return true;
        }
        else if(pender_balances <= 0)
        {
            return false;
        }
        return false;   
    }
}