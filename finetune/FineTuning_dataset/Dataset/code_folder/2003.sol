pragma solidity ^0.4.24;

 

contract ZTHReceivingContract {
    function tokenFallback(address _from, uint _value, bytes _data) public returns (bool);
}

contract ZTHInterface {
    function transfer(address _to, uint _value) public returns (bool);
    function approve(address spender, uint tokens) public returns (bool);
}

contract Zlots is ZTHReceivingContract {
    using SafeMath for uint;

    address private owner;
    address private bankroll;

     
    uint  totalSpins;
    uint  totalZTHWagered;

     
    uint contractBalance;

     
    bool    public gameActive;

    address private ZTHTKNADDR;
    address private ZTHBANKROLL;
    ZTHInterface private     ZTHTKN;

    mapping (uint => bool) validTokenBet;

     
    event HouseRetrievedTake(
        uint timeTaken,
        uint tokensWithdrawn
    );

     
    event TokensWagered(
        address _wagerer,
        uint _wagered
    );

    event LogResult(
        address _wagerer,
        uint _result,
        uint _profit,
        uint _wagered,
        bool _win
    );

    event Loss(
        address _wagerer
    );

    event Jackpot(
        address _wagerer
    );

    event EightXMultiplier(
        address _wagerer
    );

    event ReturnBet(
        address _wagerer
    );

    event TwoAndAHalfXMultiplier(
        address _wagerer
    );

    event OneAndAHalfXMultiplier(
        address _wagerer
    );

    modifier onlyOwner {
        require(msg.sender == owner);
        _;
    }

    modifier onlyBankroll {
        require(msg.sender == bankroll);
        _;
    }

    modifier onlyOwnerOrBankroll {
        require(msg.sender == owner || msg.sender == bankroll);
        _;
    }

     
    modifier gameIsActive {
        require(gameActive == true);
        _;
    }

    constructor(address ZethrAddress, address BankrollAddress) public {

         
        ZTHTKNADDR = ZethrAddress;
        ZTHBANKROLL = BankrollAddress;

         
        owner         = msg.sender;
        bankroll      = ZTHBANKROLL;

         
        ZTHTKN = ZTHInterface(ZTHTKNADDR);
        ZTHTKN.approve(ZTHBANKROLL, 2**256 - 1);
        
         
        ZTHTKN.approve(owner, 2**256 - 1);

         
        validTokenBet[5e18]  = true;
        validTokenBet[10e18] = true;
        validTokenBet[25e18] = true;
        validTokenBet[50e18] = true;

        gameActive  = true;
    }

     
    function() public payable {  }

     
    struct TKN { address sender; uint value; }
    function tokenFallback(address _from, uint _value, bytes  ) public returns (bool){
        TKN memory          _tkn;
        _tkn.sender       = _from;
        _tkn.value        = _value;
        _spinTokens(_tkn);
        return true;
    }

    struct playerSpin {
        uint200 tokenValue;  
        uint48 blockn;       
    }

     
    mapping(address => playerSpin) public playerSpins;

     
    function _spinTokens(TKN _tkn) private {

        require(gameActive);
        require(_zthToken(msg.sender));
        require(validTokenBet[_tkn.value]);
        require(jackpotGuard(_tkn.value));

        require(_tkn.value < ((2 ** 200) - 1));    
        require(block.number < ((2 ** 48) - 1));   

        address _customerAddress = _tkn.sender;
        uint    _wagered         = _tkn.value;

        playerSpin memory spin = playerSpins[_tkn.sender];

        contractBalance = contractBalance.add(_wagered);

         
        require(block.number != spin.blockn);

         
        if (spin.blockn != 0) {
          _finishSpin(_tkn.sender);
        }

         
        spin.blockn = uint48(block.number);
        spin.tokenValue = uint200(_wagered);

         
        playerSpins[_tkn.sender] = spin;

         
        totalSpins += 1;

         
        totalZTHWagered += _wagered;

        emit TokensWagered(_customerAddress, _wagered);

    }

      
    function finishSpin() public
        gameIsActive
        returns (uint)
    {
      return _finishSpin(msg.sender);
    }

     
    function _finishSpin(address target)
        private returns (uint)
    {
        playerSpin memory spin = playerSpins[target];

        require(spin.tokenValue > 0);  
        require(spin.blockn != block.number);

        uint profit = 0;

         
         
        uint result;
        if (block.number - spin.blockn > 255) {
          result = 9999;  
        } else {

           
           
          result = random(10000, spin.blockn, target);
        }

        if (result > 4489) {
           
          emit Loss(target);
          emit LogResult(target, result, profit, spin.tokenValue, false);
        } else {
            if (result < 29) {
                 
                profit = SafeMath.mul(spin.tokenValue, 25);
                emit Jackpot(target);

            } else {
                if (result < 233) {
                     
                    profit = SafeMath.mul(spin.tokenValue, 8);
                    emit EightXMultiplier(target);
                } else {

                    if (result < 641) {
                         
                        profit = spin.tokenValue;
                        emit ReturnBet(target);
                    } else {
                        if (result < 1865) {
                             
                            profit = SafeMath.div(SafeMath.mul(spin.tokenValue, 25), 10);
                            emit TwoAndAHalfXMultiplier(target);
                        } else {
                             
                            profit = SafeMath.div(SafeMath.mul(spin.tokenValue, 15), 10);
                            emit OneAndAHalfXMultiplier(target);
                        }
                    }
                }
            }
            emit LogResult(target, result, profit, spin.tokenValue, true);
            contractBalance = contractBalance.sub(profit);
            ZTHTKN.transfer(target, profit);
        }
        playerSpins[target] = playerSpin(uint200(0), uint48(0));
        return result;
    }

     
     
     
     
    function jackpotGuard(uint _wager)
        public
        view
        returns (bool)
    {
        uint maxProfit = SafeMath.mul(_wager, 25);
        uint halfContractBalance = SafeMath.div(contractBalance, 2);
        return (maxProfit <= halfContractBalance);
    }

     
     
    function maxRandom(uint blockn, address entropy) public view returns (uint256 randomNumber) {
    return uint256(keccak256(
        abi.encodePacked(
        blockhash(blockn),
        entropy)
      ));
    }

     
    function random(uint256 upper, uint256 blockn, address entropy) internal view returns (uint256 randomNumber) {
    return maxRandom(blockn, entropy) % upper;
    }

     
    function balanceOf() public view returns (uint) {
        return contractBalance;
    }

    function addNewBetAmount(uint _tokenAmount)
        public
        onlyOwner
    {
        validTokenBet[_tokenAmount] = true;
    }

     
    function pauseGame() public onlyOwner {
        gameActive = false;
    }

     
    function resumeGame() public onlyOwner {
        gameActive = true;
    }

     
    function changeOwner(address _newOwner) public onlyOwner {
        owner = _newOwner;
    }

     
    function changeBankroll(address _newBankroll) public onlyOwner {
        bankroll = _newBankroll;
    }

     
    function divertDividendsToBankroll()
        public
        onlyOwner
    {
        bankroll.transfer(address(this).balance);
    }

    function testingSelfDestruct()
        public
        onlyOwner
    {
         
        ZTHTKN.transfer(owner, contractBalance);
        selfdestruct(owner);
    }
    
     
    function _zthToken(address _tokenContract) private view returns (bool) {
       return _tokenContract == ZTHTKNADDR;
    }
}

 

 
library SafeMath {

     
    function mul(uint a, uint b) internal pure returns (uint) {
        if (a == 0) {
            return 0;
        }
        uint c = a * b;
        assert(c / a == b);
        return c;
    }

     
    function div(uint a, uint b) internal pure returns (uint) {
         
        uint c = a / b;
         
        return c;
    }

     
    function sub(uint a, uint b) internal pure returns (uint) {
        assert(b <= a);
        return a - b;
    }

     
    function add(uint a, uint b) internal pure returns (uint) {
        uint c = a + b;
        assert(c >= a);
        return c;
    }
}