pragma solidity ^0.4.23;




contract Ownable {
  address public owner;


  event OwnershipTransferred(address indexed previousOwner, address indexed newOwner);


  
  function Ownable() public {
    owner = msg.sender;
  }

  
  modifier onlyOwner() {
    require(msg.sender == owner);
    _;
  }

  
  function transferOwnership(address newOwner) public onlyOwner {
    require(newOwner != address(0));
    emit OwnershipTransferred(owner, newOwner);
    owner = newOwner;
  }

}




contract ERC721Basic {
  event Transfer(address indexed _from, address indexed _to, uint256 _tokenId);
  event Approval(address indexed _owner, address indexed _approved, uint256 _tokenId);
  event ApprovalForAll(address indexed _owner, address indexed _operator, bool _approved);

  function balanceOf(address _owner) public view returns (uint256 _balance);
  function ownerOf(uint256 _tokenId) public view returns (address _owner);
  function exists(uint256 _tokenId) public view returns (bool _exists);

  function approve(address _to, uint256 _tokenId) public;
  function getApproved(uint256 _tokenId) public view returns (address _operator);

  function setApprovalForAll(address _operator, bool _approved) public;
  function isApprovedForAll(address _owner, address _operator) public view returns (bool);

  function transferFrom(address _from, address _to, uint256 _tokenId) public;
  function safeTransferFrom(address _from, address _to, uint256 _tokenId) public;
  function safeTransferFrom(
    address _from,
    address _to,
    uint256 _tokenId,
    bytes _data
  )
    public;
}




contract ERC721Enumerable is ERC721Basic {
  function totalSupply() public view returns (uint256);
  function tokenOfOwnerByIndex(address _owner, uint256 _index) public view returns (uint256 _tokenId);
  function tokenByIndex(uint256 _index) public view returns (uint256);
}



contract ERC721Metadata is ERC721Basic {
  function name() public view returns (string _name);
  function symbol() public view returns (string _symbol);
  function tokenURI(uint256 _tokenId) public view returns (string);
}



contract ERC721 is ERC721Basic, ERC721Enumerable, ERC721Metadata {
}




library AddressUtils {

  
  function isContract(address addr) internal view returns (bool) {
    uint256 size;
    
    
    
    
    
    
    assembly { size := extcodesize(addr) }  
    return size > 0;
  }

}




library SafeMath {

  
  function mul(uint256 a, uint256 b) internal pure returns (uint256 c) {
    if (a == 0) {
      return 0;
    }
    c = a * b;
    assert(c / a == b);
    return c;
  }

  
  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    
    
    
    return a / b;
  }

  
  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    assert(b <= a);
    return a - b;
  }

  
  function add(uint256 a, uint256 b) internal pure returns (uint256 c) {
    c = a + b;
    assert(c >= a);
    return c;
  }
}




contract ERC721Receiver {
  
  bytes4 constant ERC721_RECEIVED = 0xf0b9e5ba;

  
  function onERC721Received(address _from, uint256 _tokenId, bytes _data) public returns(bytes4);
}




contract ERC721BasicToken is ERC721Basic {
  using SafeMath for uint256;
  using AddressUtils for address;

  
  
  bytes4 constant ERC721_RECEIVED = 0xf0b9e5ba;

  
  mapping (uint256 => address) internal tokenOwner;

  
  mapping (uint256 => address) internal tokenApprovals;

  
  mapping (address => uint256) internal ownedTokensCount;

  
  mapping (address => mapping (address => bool)) internal operatorApprovals;

  
  modifier onlyOwnerOf(uint256 _tokenId) {
    require(ownerOf(_tokenId) == msg.sender);
    _;
  }

  
  modifier canTransfer(uint256 _tokenId) {
    require(isApprovedOrOwner(msg.sender, _tokenId));
    _;
  }

  
  function balanceOf(address _owner) public view returns (uint256) {
    require(_owner != address(0));
    return ownedTokensCount[_owner];
  }

  
  function ownerOf(uint256 _tokenId) public view returns (address) {
    address owner = tokenOwner[_tokenId];
    require(owner != address(0));
    return owner;
  }

  
  function exists(uint256 _tokenId) public view returns (bool) {
    address owner = tokenOwner[_tokenId];
    return owner != address(0);
  }

  
  function approve(address _to, uint256 _tokenId) public {
    address owner = ownerOf(_tokenId);
    require(_to != owner);
    require(msg.sender == owner || isApprovedForAll(owner, msg.sender));

    if (getApproved(_tokenId) != address(0) || _to != address(0)) {
      tokenApprovals[_tokenId] = _to;
      emit Approval(owner, _to, _tokenId);
    }
  }

  
  function getApproved(uint256 _tokenId) public view returns (address) {
    return tokenApprovals[_tokenId];
  }

  
  function setApprovalForAll(address _to, bool _approved) public {
    require(_to != msg.sender);
    operatorApprovals[msg.sender][_to] = _approved;
    emit ApprovalForAll(msg.sender, _to, _approved);
  }

  
  function isApprovedForAll(address _owner, address _operator) public view returns (bool) {
    return operatorApprovals[_owner][_operator];
  }

  
  function transferFrom(address _from, address _to, uint256 _tokenId) public canTransfer(_tokenId) {
    require(_from != address(0));
    require(_to != address(0));

    clearApproval(_from, _tokenId);
    removeTokenFrom(_from, _tokenId);
    addTokenTo(_to, _tokenId);

    emit Transfer(_from, _to, _tokenId);
  }

  
  function safeTransferFrom(
    address _from,
    address _to,
    uint256 _tokenId
  )
    public
    canTransfer(_tokenId)
  {
    
    safeTransferFrom(_from, _to, _tokenId, "");
  }

  
  function safeTransferFrom(
    address _from,
    address _to,
    uint256 _tokenId,
    bytes _data
  )
    public
    canTransfer(_tokenId)
  {
    transferFrom(_from, _to, _tokenId);
    
    require(checkAndCallSafeTransfer(_from, _to, _tokenId, _data));
  }

  
  function isApprovedOrOwner(address _spender, uint256 _tokenId) internal view returns (bool) {
    address owner = ownerOf(_tokenId);
    return _spender == owner || getApproved(_tokenId) == _spender || isApprovedForAll(owner, _spender);
  }

  
  function _mint(address _to, uint256 _tokenId) internal {
    require(_to != address(0));
    addTokenTo(_to, _tokenId);
    emit Transfer(address(0), _to, _tokenId);
  }

  
  function _burn(address _owner, uint256 _tokenId) internal {
    clearApproval(_owner, _tokenId);
    removeTokenFrom(_owner, _tokenId);
    emit Transfer(_owner, address(0), _tokenId);
  }

  
  function clearApproval(address _owner, uint256 _tokenId) internal {
    require(ownerOf(_tokenId) == _owner);
    if (tokenApprovals[_tokenId] != address(0)) {
      tokenApprovals[_tokenId] = address(0);
      emit Approval(_owner, address(0), _tokenId);
    }
  }

  
  function addTokenTo(address _to, uint256 _tokenId) internal {
    require(tokenOwner[_tokenId] == address(0));
    tokenOwner[_tokenId] = _to;
    ownedTokensCount[_to] = ownedTokensCount[_to].add(1);
  }

  
  function removeTokenFrom(address _from, uint256 _tokenId) internal {
    require(ownerOf(_tokenId) == _from);
    ownedTokensCount[_from] = ownedTokensCount[_from].sub(1);
    tokenOwner[_tokenId] = address(0);
  }

  
  function checkAndCallSafeTransfer(
    address _from,
    address _to,
    uint256 _tokenId,
    bytes _data
  )
    internal
    returns (bool)
  {
    if (!_to.isContract()) {
      return true;
    }
    bytes4 retval = ERC721Receiver(_to).onERC721Received(_from, _tokenId, _data);
    return (retval == ERC721_RECEIVED);
  }
}




contract ERC721Token is ERC721, ERC721BasicToken {
  
  string internal name_;

  
  string internal symbol_;

  
  mapping (address => uint256[]) internal ownedTokens;

  
  mapping(uint256 => uint256) internal ownedTokensIndex;

  
  uint256[] internal allTokens;

  
  mapping(uint256 => uint256) internal allTokensIndex;

  
  mapping(uint256 => string) internal tokenURIs;

  
  function ERC721Token(string _name, string _symbol) public {
    name_ = _name;
    symbol_ = _symbol;
  }

  
  function name() public view returns (string) {
    return name_;
  }

  
  function symbol() public view returns (string) {
    return symbol_;
  }

  
  function tokenURI(uint256 _tokenId) public view returns (string) {
    require(exists(_tokenId));
    return tokenURIs[_tokenId];
  }

  
  function tokenOfOwnerByIndex(address _owner, uint256 _index) public view returns (uint256) {
    require(_index < balanceOf(_owner));
    return ownedTokens[_owner][_index];
  }

  
  function totalSupply() public view returns (uint256) {
    return allTokens.length;
  }

  
  function tokenByIndex(uint256 _index) public view returns (uint256) {
    require(_index < totalSupply());
    return allTokens[_index];
  }

  
  function _setTokenURI(uint256 _tokenId, string _uri) internal {
    require(exists(_tokenId));
    tokenURIs[_tokenId] = _uri;
  }

  
  function addTokenTo(address _to, uint256 _tokenId) internal {
    super.addTokenTo(_to, _tokenId);
    uint256 length = ownedTokens[_to].length;
    ownedTokens[_to].push(_tokenId);
    ownedTokensIndex[_tokenId] = length;
  }

  
  function removeTokenFrom(address _from, uint256 _tokenId) internal {
    super.removeTokenFrom(_from, _tokenId);

    uint256 tokenIndex = ownedTokensIndex[_tokenId];
    uint256 lastTokenIndex = ownedTokens[_from].length.sub(1);
    uint256 lastToken = ownedTokens[_from][lastTokenIndex];

    ownedTokens[_from][tokenIndex] = lastToken;
    ownedTokens[_from][lastTokenIndex] = 0;
    
    
    

    ownedTokens[_from].length--;
    ownedTokensIndex[_tokenId] = 0;
    ownedTokensIndex[lastToken] = tokenIndex;
  }

  
  function _mint(address _to, uint256 _tokenId) internal {
    super._mint(_to, _tokenId);

    allTokensIndex[_tokenId] = allTokens.length;
    allTokens.push(_tokenId);
  }

  
  function _burn(address _owner, uint256 _tokenId) internal {
    super._burn(_owner, _tokenId);

    
    if (bytes(tokenURIs[_tokenId]).length != 0) {
      delete tokenURIs[_tokenId];
    }

    
    uint256 tokenIndex = allTokensIndex[_tokenId];
    uint256 lastTokenIndex = allTokens.length.sub(1);
    uint256 lastToken = allTokens[lastTokenIndex];

    allTokens[tokenIndex] = lastToken;
    allTokens[lastTokenIndex] = 0;

    allTokens.length--;
    allTokensIndex[_tokenId] = 0;
    allTokensIndex[lastToken] = tokenIndex;
  }

}



contract ChallengeToken is ERC721Token, Ownable {
    mapping (uint256 => bool) public isCommunityChallenge;
    mapping (uint256 => string) public titles;
    mapping (uint256 => mapping (address => uint256)) public rewards;
    mapping (uint256 => address[]) public verifiers;
    mapping (uint256 => mapping (address => bool)) public confirmations;
    mapping (uint256 => uint256) public totalRewards;

    function create(string _title, bool _isCommunityChallenge) external {
        uint256 index = allTokens.length + 1;

        _mint(msg.sender, index);

        titles[index] = _title;
        isCommunityChallenge[index] = _isCommunityChallenge;

        BoughtToken(msg.sender, index);
    }

    function createWithReward(string _title, bool _isCommunityChallenge, uint256 _amount, address _verifier) payable external {
        require(msg.value == _amount);
        require(confirmations[index][_verifier] == false);

        uint256 index = allTokens.length + 1;

        _mint(msg.sender, index);

        titles[index] = _title;

        totalRewards[index] += msg.value;

        if (rewards[index][_verifier] == 0) {
            verifiers[index].push(_verifier);
            rewards[index][_verifier] = msg.value;
        } else {
            rewards[index][_verifier] += msg.value;
        }

        isCommunityChallenge[index] = _isCommunityChallenge;

        BoughtToken(msg.sender, index);
    }

    function confirm(uint256 _index) external {
        confirmations[_index][msg.sender] = true;
    }

    function addReward(uint256 _index, uint256 _amount, address _verifier) payable external {
        require(msg.value == _amount);

        require(confirmations[_index][_verifier] == false);

        if (rewards[_index][_verifier] == 0) {
            verifiers[_index].push(_verifier);
            rewards[_index][_verifier] = msg.value;
        } else {
            rewards[_index][_verifier] += msg.value;
        }
    }

    function claimReward(uint256 _index, address _verifier) external {
        require(ownerOf(_index) == msg.sender);
        require(confirmations[_index][_verifier] == true);

        uint256 reward = rewards[_index][_verifier];

        rewards[_index][_verifier] = 0;
        totalRewards[_index] -= reward;

        msg.sender.transfer(reward);
    }

    function acceptChallenge(uint256 _index) external returns (bool) {
        if (isCommunityChallenge[_index] == true) {
            ChallengeAccepted(msg.sender, _index);
            return true;
        } else {
            return false;
        }
    }

    function myTokens() external view returns (uint256[])
    {
        return ownedTokens[msg.sender];
    }

    function getToken(uint256 _tokenId) external view
        returns (bool tokenType_, string tokenTitle_, uint256 tokenReward_, address[] verifiers_)
    {
        tokenType_ = isCommunityChallenge[_tokenId];
        tokenTitle_ = titles[_tokenId];
        tokenReward_ = totalRewards[_tokenId];
        verifiers_ = verifiers[_tokenId];
    }

    function ChallengeToken() ERC721Token("Challenge Token", "CDO") public {
    }

    
    event ChallengeAccepted(address _person, uint256 _index);
    event BoughtToken(address indexed buyer, uint256 tokenId);
}