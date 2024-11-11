/**
 *  $$$$$$\  $$\                 $$\                           
 * $$  __$$\ $$ |                $$ |                          
 * $$ /  \__|$$$$$$$\   $$$$$$\  $$ |  $$\  $$$$$$\   $$$$$$\  
 * \$$$$$$\  $$  __$$\  \____$$\ $$ | $$  |$$  __$$\ $$  __$$\ 
 *  \____$$\ $$ |  $$ | $$$$$$$ |$$$$$$  / $$$$$$$$ |$$ |  \__|
 * $$\   $$ |$$ |  $$ |$$  __$$ |$$  _$$<  $$   ____|$$ |      
 * \$$$$$$  |$$ |  $$ |\$$$$$$$ |$$ | \$$\ \$$$$$$$\ $$ |      
 *  \______/ \__|  \__| \_______|\__|  \__| \_______|\__|
 * $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
 * ____________________________________________________________
*/

pragma solidity >=0.4.23 <0.6.0;

import "./interfaces/ERC20Interface.sol";
import "./Mocks/SafeMath.sol";

contract RedpacketVault {
    using SafeMath for uint256;
    ERC20Interface private erc20;
    
    address public erc20Address;
    uint256 public totalAmount = 0; // Total amount of deposit
    uint256 public totalBalance = 0; // Total balance of deposit after Withdrawal

    struct Commitment {                     // Deposit Commitment
        uint256         status;             // If there is no this commitment or balance is zeor, false
        uint256         amount;             // Deposit balance
        address payable sender;             // Who make this deposit
        uint256         timestamp;          // Deposit timestamp
        string          memo;               // Memo while send redpacket
        address[]       takenAddresses;     // 
        uint256         withdrawTimes;
        uint256         cliff;
    }
    // Mapping of commitments, must be private. The key is hashKey = hash(commitment,recipient)
    // The contract will hide the recipient and commitment while make deposit.
    mapping(bytes32 => Commitment) private commitments; 
    address public operator;
    address public redpacketManagerAddress;

    event RedPacketDeposit(address indexed sender, bytes32 indexed hashKey, uint256 amount, uint256 timestamp);
    event RedPacketWithdraw(address indexed sender, address indexed recipient, bytes32 indexed hashKey, uint256 amount, uint256 timestamp);

    function sendRedpacketDepositEvent(address _sender, bytes32 _hashkey, uint256 _amount, uint256 _timestamp) external onlyRedpacketManager {
      emit RedPacketDeposit(_sender, _hashkey, _amount, _timestamp);
    }

    function sendRedpacketWithdrawEvent(address _sender, address _recipient, bytes32 _hashkey, uint256 _amount, uint256 _timestamp) external onlyRedpacketManager {
      emit RedPacketWithdraw(_sender, _recipient, _hashkey, _amount, _timestamp);
    }

    modifier onlyOperator {
        require(msg.sender == operator, "Only operator can call this function.");
        _;
    }

    modifier onlyRedpacketManager {
        require(msg.sender == redpacketManagerAddress, "Only redpacket manager contract can call this function.");
        _;
    }

    constructor(address _erc20Address) public {
        operator = msg.sender;
        erc20Address = _erc20Address;
        erc20 = ERC20Interface(erc20Address);
    }

    function setStatus(bytes32 _hashkey, uint256 _status) external onlyRedpacketManager {
        commitments[_hashkey].status = _status;
    }
    
    function setAmount(bytes32 _hashkey, uint256 _amount) external onlyRedpacketManager {
        commitments[_hashkey].amount = _amount;
    }
    
    function setSender(bytes32 _hashkey, address payable _sender) external onlyRedpacketManager {
        commitments[_hashkey].sender = _sender;
    }
    
    function setTimestamp(bytes32 _hashkey, uint256 _timestamp) external onlyRedpacketManager {
        commitments[_hashkey].timestamp = _timestamp;
    }
    
    function setMemo(bytes32 _hashkey, string calldata _memo) external onlyRedpacketManager {
        commitments[_hashkey].memo = _memo;
    }
    
    function setWithdrawTimes(bytes32 _hashkey, uint256 _times) external onlyRedpacketManager {
        commitments[_hashkey].withdrawTimes = _times;
    }
    
    function setCliff(bytes32 _hashkey, uint256 _cliff) external onlyRedpacketManager {
        commitments[_hashkey].cliff = _cliff;
    }
    
    function initTakenAddresses(bytes32 _hashkey) external onlyRedpacketManager {
        commitments[_hashkey].takenAddresses = new address[](0);
    }
    
    function isTaken(bytes32 _hashkey, address _address) external view returns(bool) {
        bool has = false;
        for(uint256 i = 0; i < commitments[_hashkey].takenAddresses.length; i++) {
            if(_address == commitments[_hashkey].takenAddresses[i]) {has = true; break;}
        }
        return has;
    }
    
    function addTakenAddress(bytes32 _hashkey, address _address) external onlyRedpacketManager {
        commitments[_hashkey].takenAddresses.push(_address);
    }
    
    function getStatus(bytes32 _hashkey) external view onlyRedpacketManager returns(uint256) {
        return commitments[_hashkey].status;
    }
    
    function getAmount(bytes32 _hashkey) external view onlyRedpacketManager returns(uint256) {
        return commitments[_hashkey].amount;
    }
    
    function getSender(bytes32 _hashkey) external view onlyRedpacketManager returns(address payable) {
        return commitments[_hashkey].sender;
    }
    
    function getTimestamp(bytes32 _hashkey) external view onlyRedpacketManager returns(uint256) {
        return commitments[_hashkey].timestamp;
    }
    
    function getMemo(bytes32 _hashkey) external view onlyRedpacketManager returns(string memory) {
        return commitments[_hashkey].memo;
    }
    
    function getWithdrawTimes(bytes32 _hashkey) external view onlyRedpacketManager returns(uint256) {
        return commitments[_hashkey].withdrawTimes;
    }
    
    function getCliff(bytes32 _hashkey) external view onlyRedpacketManager returns(uint256) {
        return commitments[_hashkey].cliff;
    }
    
    function updateOperator(address _operator) external onlyOperator {
        operator = _operator;
    }

    function updateRedpacketManagerAddress(address _redpacketManager, uint256 _allowance) external onlyOperator returns(bool) {
        redpacketManagerAddress = _redpacketManager;
        // Approve redpacket manager contract
        safeApprove(erc20Address, _redpacketManager, _allowance);
        return true;
    }

    function getRedpacketAllowance() external view returns(uint256) {
      return erc20.allowance(address(this), redpacketManagerAddress);
    }

    function addTotalAmount(uint256 _amount) external onlyRedpacketManager {
        totalAmount = totalAmount.add(_amount);
    }

    function addTotalBalance(uint256 _amount) external onlyRedpacketManager {
        totalBalance = totalBalance.add(_amount);
    }

    function subTotalBalance(uint256 _amount) external onlyRedpacketManager {
        totalBalance = totalBalance.sub(_amount);
    }

    function safeApprove(address token, address to, uint value) internal {
        // bytes4(keccak256(bytes('approve(address,uint256)')));
        (bool success, bytes memory data) = token.call(abi.encodeWithSelector(0x095ea7b3, to, value));
        require(success && (data.length == 0 || abi.decode(data, (bool))), 'TransferHelper: APPROVE_FAILED');
    }
}
