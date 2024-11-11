pragma solidity ^0.4.24;

interface tokenRecipient { function receiveApproval(address _from, uint256 _value, address _token, bytes _extraData) external; }

contract Ownable {
  address public owner;

  
  function Ownable() {
    owner = msg.sender;
  }

  
  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }
}

contract Pausable is Ownable {
  event Pause();
  event Unpause();

  bool public paused = false;


  
  modifier whenNotPaused() {
    require(!paused);
    _;
  }

  
  modifier whenPaused() {
    require(paused);
    _;
  }

  
  function pause() onlyOwner whenNotPaused public {
    paused = true;
    emit Pause();
  }

  
  function unpause() onlyOwner whenPaused public {
    paused = false;
    emit Unpause();
  }
}

contract BlockchainMoneyEngine is Pausable {
  address public owner;

  
  string public name;
  string public symbol;
  uint8 public decimals = 18;
  
  uint256 public totalSupply;

  
  mapping (address => uint256) public balanceOf;
  mapping (address => mapping (address => uint256)) public allowance;

  
  event Transfer(address indexed from, address indexed to, uint256 value);

  
  event Burn(address indexed from, uint256 value);

  
  function BlockchainMoneyEngine(
    uint256 initialSupply,
    string tokenName,
    string tokenSymbol
  ) public {
    totalSupply = initialSupply * 10 ** uint256(decimals);  
    balanceOf[msg.sender] = totalSupply;                
    name = tokenName;                                   
    symbol = tokenSymbol;                               
    owner = msg.sender;
  }

  function setName(string _name)
  onlyOwner()
  public
  {
    name = _name;
  }

  function setSymbol(string _symbol)
  onlyOwner()
  public
  {
    symbol = _symbol;
  }

  
  function _transfer(address _from, address _to, uint _value) internal {
    
    require(_to != 0x0);
    
    require(balanceOf[_from] >= _value);
    
    require(balanceOf[_to] + _value >= balanceOf[_to]);
    
    uint previousBalances = balanceOf[_from] + balanceOf[_to];
    
    balanceOf[_from] -= _value;
    
    balanceOf[_to] += _value;
    emit Transfer(_from, _to, _value);
    
    assert(balanceOf[_from] + balanceOf[_to] == previousBalances);
  }
  
  function destruct() public {
    if (owner == msg.sender) {
      selfdestruct(owner);
    }
  }
  
  
  function transfer(address _to, uint256 _value) public whenNotPaused {
    _transfer(msg.sender, _to, _value);
  }

  
  function transferFrom(address _from, address _to, uint256 _value) public whenNotPaused returns (bool success) {
    require(_value <= allowance[_from][msg.sender]);     
    allowance[_from][msg.sender] -= _value;
    _transfer(_from, _to, _value);
    return true;
  }

  
  function approve(address _spender, uint256 _value) public whenNotPaused
  returns (bool success) {
    allowance[msg.sender][_spender] = _value;
    return true;
  }

  
   
  function approveAndCall(address _spender, uint256 _value, bytes _extraData)
  public
  returns (bool success) {
    tokenRecipient spender = tokenRecipient(_spender);
    if (approve(_spender, _value)) {
      spender.receiveApproval(msg.sender, _value, this, _extraData);
      return true;
    }
  }

  
  function burn(uint256 _value) public returns (bool success) {
    require(balanceOf[msg.sender] >= _value);   
    balanceOf[msg.sender] -= _value;            
    totalSupply -= _value;                      
    emit Burn(msg.sender, _value);
    return true;
  }

  
  function burnFrom(address _from, uint256 _value) public returns (bool success) {
    require(balanceOf[_from] >= _value);                
    require(_value <= allowance[_from][msg.sender]);    
    balanceOf[_from] -= _value;                         
    allowance[_from][msg.sender] -= _value;             
    totalSupply -= _value;                              
    emit Burn(_from, _value);
    return true;
  }
}