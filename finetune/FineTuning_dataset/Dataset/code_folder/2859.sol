 

pragma solidity ^0.4.18;

 

contract Ownable {

	address public owner;
	address public pendingOwner;
	address public operator;

	event OwnershipTransferred(
		address indexed previousOwner,
		address indexed newOwner
	);

	 
	constructor() public {
		owner = msg.sender;
	}

	 
	modifier onlyOwner() {
		require(msg.sender == owner);
		_;
	}

	 
	modifier onlyPendingOwner() {
		require(msg.sender == pendingOwner);
		_;
	}

	modifier ownerOrOperator {
		require(msg.sender == owner || msg.sender == operator);
		_;
	}

	 
	function transferOwnership(address newOwner) onlyOwner public {
		pendingOwner = newOwner;
	}

	 
	function claimOwnership() onlyPendingOwner public {
		emit OwnershipTransferred(owner, pendingOwner);
		owner = pendingOwner;
		pendingOwner = address(0);
	}

	function setOperator(address _operator) onlyOwner public {
		operator = _operator;
	}

}

 

contract LikeCoinInterface {
	function balanceOf(address _owner) public constant returns (uint256 balance);
	function transfer(address _to, uint256 _value) public returns (bool success);
	function transferFrom(address _from, address _to, uint256 _value) public returns (bool success);
	function approve(address _spender, uint256 _value) public returns (bool success);
}

 

contract ArtMuseumBase is Ownable {

	struct Artwork {
		uint8 artworkType;
		uint32 sequenceNumber;
		uint128 value;
		address player;
	}
	LikeCoinInterface public like;

	 
	uint32[] public ids;
	 
	uint32 public lastId;
	 
	uint32 public oldest;
	 
	mapping(uint32 => Artwork) artworks;
	 
	mapping(address=>mapping(uint8 => uint32)) userArtworkSequenceNumber;
	 
	uint128[] public costs;
	 
	uint128[] public values;
	 
	uint8 public fee;

	 
	uint32 public numArtworks;
	 
	uint16 public maxArtworks;
	 
	uint32[] numArtworksXType;

	 
	function init(address _likeAddr) public onlyOwner {
		require(like==address(0));
		like = LikeCoinInterface(_likeAddr);
		costs = [800 ether, 2000 ether, 5000 ether, 12000 ether, 25000 ether];
		setFee(5);
		maxArtworks = 1000;
		lastId = 1;
		oldest = 0;
	}

	function deposit() payable public {

	}

	function withdrawBalance() public onlyOwner returns(bool res) {
		owner.transfer(address(this).balance);
		return true;
	}

	 
	function collectFees(uint128 amount) public onlyOwner {
		uint collectedFees = getFees();
		if (amount <= collectedFees) {
			like.transfer(owner,amount);
		}
	}

	function getArtwork(uint32 artworkId) public constant returns(uint8 artworkType, uint32 sequenceNumber, uint128 value, address player) {
		return (artworks[artworkId].artworkType, artworks[artworkId].sequenceNumber, artworks[artworkId].value, artworks[artworkId].player);
	}

	function getAllArtworks() public constant returns(uint32[] artworkIds,uint8[] types,uint32[] sequenceNumbers, uint128[] artworkValues) {
		uint32 id;
		artworkIds = new uint32[](numArtworks);
		types = new uint8[](numArtworks);
		sequenceNumbers = new uint32[](numArtworks);
		artworkValues = new uint128[](numArtworks);
		for (uint16 i = 0; i < numArtworks; i++) {
			id = ids[i];
			artworkIds[i] = id;
			types[i] = artworks[id].artworkType;
			sequenceNumbers[i] = artworks[id].sequenceNumber;
			artworkValues[i] = artworks[id].value;
		}
	}

	function getAllArtworksByOwner() public constant returns(uint32[] artworkIds,uint8[] types,uint32[] sequenceNumbers, uint128[] artworkValues) {
		uint32 id;
		uint16 j = 0;
		uint16 howmany = 0;
		address player = address(msg.sender);
		for (uint16 k = 0; k < numArtworks; k++) {
			if (artworks[ids[k]].player == player)
				howmany++;
		}
		artworkIds = new uint32[](howmany);
		types = new uint8[](howmany);
		sequenceNumbers = new uint32[](howmany);
		artworkValues = new uint128[](howmany);
		for (uint16 i = 0; i < numArtworks; i++) {
			if (artworks[ids[i]].player == player) {
				id = ids[i];
				artworkIds[j] = id;
				types[j] = artworks[id].artworkType;
				sequenceNumbers[j] = artworks[id].sequenceNumber;
				artworkValues[j] = artworks[id].value;
				j++;
			}
		}
	}

	function setCosts(uint128[] _costs) public onlyOwner {
		require(_costs.length >= costs.length);
		costs = _costs;
		setFee(fee);
	}
	
	function setFee(uint8 _fee) public onlyOwner {
		fee = _fee;
		for (uint8 i = 0; i < costs.length; i++) {
			if (i < values.length)
				values[i] = costs[i] - costs[i] / 100 * fee;
			else {
				values.push(costs[i] - costs[i] / 100 * fee);
				numArtworksXType.push(0);
			}
		}
	}

	function getFees() public constant returns(uint) {
		uint reserved = 0;
		for (uint16 j = 0; j < numArtworks; j++)
			reserved += artworks[ids[j]].value;
		return like.balanceOf(this) - reserved;
	}

	function getNumArtworksXType() public constant returns(uint32[] _numArtworksXType) {
		_numArtworksXType = numArtworksXType;
	}


}

 

 

pragma solidity ^0.4.20; 

contract OraclizeI {
	address public cbAddress;
	function query(uint _timestamp, string _datasource, string _arg) external payable returns (bytes32 _id);
	function query_withGasLimit(uint _timestamp, string _datasource, string _arg, uint _gaslimit) external payable returns (bytes32 _id);
	function query2(uint _timestamp, string _datasource, string _arg1, string _arg2) public payable returns (bytes32 _id);
	function query2_withGasLimit(uint _timestamp, string _datasource, string _arg1, string _arg2, uint _gaslimit) external payable returns (bytes32 _id);
	function queryN(uint _timestamp, string _datasource, bytes _argN) public payable returns (bytes32 _id);
	function queryN_withGasLimit(uint _timestamp, string _datasource, bytes _argN, uint _gaslimit) external payable returns (bytes32 _id);
	function getPrice(string _datasource) public returns (uint _dsprice);
	function getPrice(string _datasource, uint gaslimit) public returns (uint _dsprice);
	function setProofType(byte _proofType) external;
	function setCustomGasPrice(uint _gasPrice) external;
	function randomDS_getSessionPubKeyHash() external constant returns(bytes32);
}

contract OraclizeAddrResolverI {
	function getAddress() public returns (address _addr);
}

contract usingOraclize {  
	uint constant day = 60*60*24;
	uint constant week = 60*60*24*7;
	uint constant month = 60*60*24*30;
	byte constant proofType_NONE = 0x00;
	byte constant proofType_TLSNotary = 0x10;
	byte constant proofType_Android = 0x20;
	byte constant proofType_Ledger = 0x30;
	byte constant proofType_Native = 0xF0;
	byte constant proofStorage_IPFS = 0x01;
	uint8 constant networkID_auto = 0;
	uint8 constant networkID_mainnet = 1;
	uint8 constant networkID_testnet = 2;
	uint8 constant networkID_morden = 2;
	uint8 constant networkID_consensys = 161;
	string oraclize_network_name;
	OraclizeAddrResolverI OAR;
	OraclizeI oraclize;
	modifier oraclizeAPI {
		if((address(OAR)==0)||(getCodeSize(address(OAR))==0))
			oraclize_setNetwork(networkID_auto);

		if(address(oraclize) != OAR.getAddress())
			oraclize = OraclizeI(OAR.getAddress());

		_;
	}
	function oraclize_setNetwork(uint8 networkID) internal returns(bool){
	  return oraclize_setNetwork();
	  networkID;  
	}
	function oraclize_setNetwork() internal returns(bool){
		if (getCodeSize(0x1d3B2638a7cC9f2CB3D298A3DA7a90B67E5506ed)>0){  
			OAR = OraclizeAddrResolverI(0x1d3B2638a7cC9f2CB3D298A3DA7a90B67E5506ed);
			oraclize_setNetworkName("eth_mainnet");
			return true;
		}
		if (getCodeSize(0xc03A2615D5efaf5F49F60B7BB6583eaec212fdf1)>0){  
			OAR = OraclizeAddrResolverI(0xc03A2615D5efaf5F49F60B7BB6583eaec212fdf1);
			oraclize_setNetworkName("eth_ropsten3");
			return true;
		}
		if (getCodeSize(0xB7A07BcF2Ba2f2703b24C0691b5278999C59AC7e)>0){  
			OAR = OraclizeAddrResolverI(0xB7A07BcF2Ba2f2703b24C0691b5278999C59AC7e);
			oraclize_setNetworkName("eth_kovan");
			return true;
		}
		if (getCodeSize(0x146500cfd35B22E4A392Fe0aDc06De1a1368Ed48)>0){  
			OAR = OraclizeAddrResolverI(0x146500cfd35B22E4A392Fe0aDc06De1a1368Ed48);
			oraclize_setNetworkName("eth_rinkeby");
			return true;
		}
		if (getCodeSize(0x6f485C8BF6fc43eA212E93BBF8ce046C7f1cb475)>0){  
			OAR = OraclizeAddrResolverI(0x6f485C8BF6fc43eA212E93BBF8ce046C7f1cb475);
			return true;
		}
		if (getCodeSize(0x20e12A1F859B3FeaE5Fb2A0A32C18F5a65555bBF)>0){  
			OAR = OraclizeAddrResolverI(0x20e12A1F859B3FeaE5Fb2A0A32C18F5a65555bBF);
			return true;
		}
		if (getCodeSize(0x51efaF4c8B3C9AfBD5aB9F4bbC82784Ab6ef8fAA)>0){  
			OAR = OraclizeAddrResolverI(0x51efaF4c8B3C9AfBD5aB9F4bbC82784Ab6ef8fAA);
			return true;
		}
		return false;
	}
	function oraclize_getPrice(string datasource) oraclizeAPI internal returns (uint){
		return oraclize.getPrice(datasource);
	}
	function oraclize_getPrice(string datasource, uint gaslimit) oraclizeAPI internal returns (uint){
		return oraclize.getPrice(datasource, gaslimit);
	}
	function oraclize_query(string datasource, string arg) oraclizeAPI internal returns (bytes32 id){
		uint price = oraclize.getPrice(datasource);
		if (price > 1 ether + tx.gasprice*200000) return 0;  
		return oraclize.query.value(price)(0, datasource, arg);
	}
	function oraclize_query(uint timestamp, string datasource, string arg) oraclizeAPI internal returns (bytes32 id){
		uint price = oraclize.getPrice(datasource);
		if (price > 1 ether + tx.gasprice*200000) return 0;  
		return oraclize.query.value(price)(timestamp, datasource, arg);
	}
	function oraclize_query(uint timestamp, string datasource, string arg, uint gaslimit) oraclizeAPI internal returns (bytes32 id){
		uint price = oraclize.getPrice(datasource, gaslimit);
		if (price > 1 ether + tx.gasprice*gaslimit) return 0;  
		return oraclize.query_withGasLimit.value(price)(timestamp, datasource, arg, gaslimit);
	}
	function oraclize_query(string datasource, string arg, uint gaslimit) oraclizeAPI internal returns (bytes32 id){
		uint price = oraclize.getPrice(datasource, gaslimit);
		if (price > 1 ether + tx.gasprice*gaslimit) return 0;  
		return oraclize.query_withGasLimit.value(price)(0, datasource, arg, gaslimit);
	}
	function oraclize_query(string datasource, string arg1, string arg2) oraclizeAPI internal returns (bytes32 id){
		uint price = oraclize.getPrice(datasource);
		if (price > 1 ether + tx.gasprice*200000) return 0;  
		return oraclize.query2.value(price)(0, datasource, arg1, arg2);
	}
	function oraclize_query(uint timestamp, string datasource, string arg1, string arg2) oraclizeAPI internal returns (bytes32 id){
		uint price = oraclize.getPrice(datasource);
		if (price > 1 ether + tx.gasprice*200000) return 0;  
		return oraclize.query2.value(price)(timestamp, datasource, arg1, arg2);
	}
	function oraclize_query(uint timestamp, string datasource, string arg1, string arg2, uint gaslimit) oraclizeAPI internal returns (bytes32 id){
		uint price = oraclize.getPrice(datasource, gaslimit);
		if (price > 1 ether + tx.gasprice*gaslimit) return 0;  
		return oraclize.query2_withGasLimit.value(price)(timestamp, datasource, arg1, arg2, gaslimit);
	}
	function oraclize_query(string datasource, string arg1, string arg2, uint gaslimit) oraclizeAPI internal returns (bytes32 id){
		uint price = oraclize.getPrice(datasource, gaslimit);
		if (price > 1 ether + tx.gasprice*gaslimit) return 0;  
		return oraclize.query2_withGasLimit.value(price)(0, datasource, arg1, arg2, gaslimit);
	}

	function oraclize_cbAddress() oraclizeAPI internal returns (address){
		return oraclize.cbAddress();
	}
	function oraclize_setCustomGasPrice(uint gasPrice) oraclizeAPI internal {
		return oraclize.setCustomGasPrice(gasPrice);
	}
	function getCodeSize(address _addr) constant internal returns(uint _size) {
		assembly {
			_size := extcodesize(_addr)
		}
	}
	 
	function parseInt(string _a) internal pure returns (uint) {
		return parseInt(_a, 0);
	}
	 
	function parseInt(string _a, uint _b) internal pure returns (uint) {
		bytes memory bresult = bytes(_a);
		uint mint = 0;
		bool decimals = false;
		for (uint i=0; i<bresult.length; i++){
			if ((bresult[i] >= 48)&&(bresult[i] <= 57)){
				if (decimals){
				   if (_b == 0) break;
					else _b--;
				}
				mint *= 10;
				mint += uint(bresult[i]) - 48;
			} else if (bresult[i] == 46) decimals = true;
		}
		if (_b > 0) mint *= 10**_b;
		return mint;
	}
	function oraclize_setNetworkName(string _network_name) internal {
		oraclize_network_name = _network_name;
	}
	function oraclize_getNetworkName() internal view returns (string) {
		return oraclize_network_name;
	}
}

 

library strings {
	struct slice {
		uint _len;
		uint _ptr;
	}

	function memcpy(uint dest, uint src, uint len) private pure {
		 
		for(; len >= 32; len -= 32) {
			assembly {
				mstore(dest, mload(src))
			}
			dest += 32;
			src += 32;
		}

		 
		uint mask = 256 ** (32 - len) - 1;
		assembly {
			let srcpart := and(mload(src), not(mask))
			let destpart := and(mload(dest), mask)
			mstore(dest, or(destpart, srcpart))
		}
	}

	 
	function toSlice(string self) internal pure returns (slice) {
		uint ptr;
		assembly {
			ptr := add(self, 0x20)
		}
		return slice(bytes(self).length, ptr);
	}

	 
	function toString(slice self) internal pure returns (string) {
		string memory ret = new string(self._len);
		uint retptr;
		assembly { retptr := add(ret, 32) }

		memcpy(retptr, self._ptr, self._len);
		return ret;
	}

	 
	 
	function findPtr(uint selflen, uint selfptr, uint needlelen, uint needleptr) private pure returns (uint) {
		uint ptr = selfptr;
		uint idx;

		if (needlelen <= selflen) {
			if (needlelen <= 32) {
				bytes32 mask = bytes32(~(2 ** (8 * (32 - needlelen)) - 1));

				bytes32 needledata;
				assembly { needledata := and(mload(needleptr), mask) }

				uint end = selfptr + selflen - needlelen;
				bytes32 ptrdata;
				assembly { ptrdata := and(mload(ptr), mask) }

				while (ptrdata != needledata) {
					if (ptr >= end)
						return selfptr + selflen;
					ptr++;
					assembly { ptrdata := and(mload(ptr), mask) }
				}
				return ptr;
			} else {
				 
				bytes32 hash;
				assembly { hash := sha3(needleptr, needlelen) }

				for (idx = 0; idx <= selflen - needlelen; idx++) {
					bytes32 testHash;
					assembly { testHash := sha3(ptr, needlelen) }
					if (hash == testHash)
						return ptr;
					ptr += 1;
				}
			}
		}
		return selfptr + selflen;
	}


	 
	function split(slice self, slice needle, slice token) internal pure returns (slice) {
		uint ptr = findPtr(self._len, self._ptr, needle._len, needle._ptr);
		token._ptr = self._ptr;
		token._len = ptr - self._ptr;
		if (ptr == self._ptr + self._len) {
			 
			self._len = 0;
		} else {
			self._len -= token._len + needle._len;
			self._ptr = ptr + needle._len;
		}
		return token;
	}

	 
	function split(slice self, slice needle) internal pure returns (slice token) {
		split(self, needle, token);
	}

	 
	function count(slice self, slice needle) internal pure returns (uint cnt) {
		uint ptr = findPtr(self._len, self._ptr, needle._len, needle._ptr) + needle._len;
		while (ptr <= self._ptr + self._len) {
			cnt++;
			ptr = findPtr(self._len - (ptr - self._ptr), ptr, needle._len, needle._ptr) + needle._len;
		}
	}

}

 

contract ArtMuseumV1 is ArtMuseumBase, usingOraclize {

	 
	using strings for *;

	 
	uint32 public lastcombo;
	 
	uint public lastStealBlockNumber;
	 
	uint8[] public oldestExtraStealProbability;

	 
	string randomQuery;
	 
	string queryType;
	 
	uint public nextStealTimestamp;
	 
	uint32 public oraclizeGas;
	 
	uint32 public oraclizeGasExtraArtwork;
	 
	uint32 public etherExchangeLikeCoin;
	 
	bytes32 nextStealId;
	 
	uint8 public numOfTimesSteal;
	 
	uint public oraclizeFee;

	 
	event newPurchase(address player, uint32 startId, uint8[] artworkTypes, uint32[] startSequenceNumbers);
	 
	event newSteal(uint timestamp,uint32[] stolenArtworks,uint8[] artworkTypes,uint32[] sequenceNumbers, uint256[] values,address[] players);
	 
	event newStealRewards(uint128 total,uint128[] values);
	 
	event newSell(uint32[] artworkId, address player, uint256 value);
	 
	event newTriggerOraclize(bytes32 nextStealId, uint waittime, uint gasAmount, uint price, uint balancebefore, uint balance);
	 
	event newOraclizeCallback(bytes32 nextStealId, string result, uint32 killed, uint128 killedValue, uint128 distValue,uint oraclizeFee,uint gaslimit,uint exchange);

	function initOraclize() public onlyOwner {
		if((address(OAR)==0)||(getCodeSize(address(OAR))==0))
			oraclize_setNetwork();
	}

	function init1() public onlyOwner {
		randomQuery = "10 random numbers between 1 and 100000";
		queryType = "WolframAlpha";
		oraclizeGas = 150000;
		oraclizeGasExtraArtwork = 14000;
		etherExchangeLikeCoin = 50000;
		oldestExtraStealProbability = [3,5,10,15,30,50];
		numOfTimesSteal = 1;
	}

	 
	function giveArtworks(uint8[] artworkTypes, address receiver, uint256 _value) internal {
		uint32 len = uint32(artworkTypes.length);
		require(numArtworks + len < maxArtworks);
		uint256 amount = 0;
		for (uint16 i = 0; i < len; i++) {
			require(artworkTypes[i] < costs.length);
			amount += costs[artworkTypes[i]];
		}
		require(_value >= amount);
		uint8 artworkType;
		uint32[] memory seqnolist = new uint32[](len);
		for (uint16 j = 0; j < len; j++) {
			if (numArtworks < ids.length)
				ids[numArtworks] = lastId;
			else
				ids.push(lastId);
			artworkType = artworkTypes[j];
			userArtworkSequenceNumber[receiver][artworkType]++;
			seqnolist[j] = userArtworkSequenceNumber[receiver][artworkType];
			artworks[lastId] = Artwork(artworkTypes[j], userArtworkSequenceNumber[receiver][artworkType], values[artworkType], receiver);
			numArtworks++;
			lastId++;
			numArtworksXType[artworkType]++;
		}
		 
		emit newPurchase(receiver, lastId - len, artworkTypes, seqnolist);
	}

	 
	function replaceArtwork(uint16 index) internal {
		uint32 artworkId = ids[index];
		numArtworksXType[artworks[artworkId].artworkType]--;
		numArtworks--;
		if (artworkId == oldest) oldest = 0;
		delete artworks[artworkId];
		if (numArtworks>0)
			ids[index] = ids[numArtworks];
		delete ids[numArtworks];
		ids.length = numArtworks;
	}


	 
	function getOldest() public constant returns(uint32 artworkId,uint8 artworkType, uint32 sequenceNumber, uint128 value, address player) {
		if (numArtworks==0) artworkId = 0;
		else {
			artworkId = oldest;
			if (artworkId==0) {
				artworkId = ids[0];
				for (uint16 i = 1; i < numArtworks; i++) {
					if (ids[i] < artworkId)  
						artworkId = ids[i];
				}
			}
			artworkType = artworks[artworkId].artworkType;
			sequenceNumber = artworks[artworkId].sequenceNumber;
			value = artworks[artworkId].value;
			player = artworks[artworkId].player;
		}
	}

	 
	function setOldest() internal returns(uint32 artworkId,uint16 index) {
		if (numArtworks==0) artworkId = 0;
		else {
			if (oldest==0) {
				oldest = ids[0];
				index = 0;
				for (uint16 i = 1; i < numArtworks; i++) {
					if (ids[i] < oldest) {  
						oldest = ids[i];
						index = i;
					}
				}
			} else {
				for (uint16 j = 0; j < numArtworks; j++) {
					if (ids[j] == oldest) {
						index = j;
						break;
					}
				}				
			}
			artworkId = oldest;
		}
	}

	 
	function sellArtwork(uint32 artworkId) public {
		require(msg.sender == artworks[artworkId].player);
		uint256 val = uint256(artworks[artworkId].value); 
		uint16 artworkIndex;
		bool found = false;
		for (uint16 i = 0; i < numArtworks; i++) {
			if (ids[i] == artworkId) {
				artworkIndex = i;
				found = true;
				break;
			}
		}
		require(found == true);
		replaceArtwork(artworkIndex);
		if (val>0)
			like.transfer(msg.sender,val);
		uint32[] memory artworkIds = new uint32[](1);
		artworkIds[0] = artworkId;
		 
		 
		emit newSell(artworkIds, msg.sender, val);
	}
	
	 
	function triggerStealManually(uint32 inseconds) public payable ownerOrOperator {
		require((nextStealTimestamp) < now);  
		triggerSteal(inseconds, (oraclizeGas + oraclizeGasExtraArtwork * numArtworks));
	}

	 
	function triggerStealManually2(string result) public payable ownerOrOperator {
		uint gaslimit = gasleft();
		oraclizeFee = (gaslimit) * tx.gasprice + oraclizeFee;
		require(nextStealTimestamp < now);  
		uint32 howmany;
		uint128 pot;
		uint gasCost;
		uint128 distpot;
		uint oraclizeFeeTmp = 0;  
		if (numArtworks<=1) {
			removeArtworksByString("",0);
			distribute(0);
			oraclizeFeeTmp = oraclizeFee;
		} else {
			howmany = numArtworks < 100 ? (numArtworks < 10 ? (numArtworks < 2 ? 0 : 1) : numArtworks / 10) : 10;  
			pot = removeArtworksByString(result,howmany);
			gasCost = ((oraclizeFee * etherExchangeLikeCoin) / 1 ether) * 1 ether;
			if (pot > gasCost)
				distpot = uint128(pot - gasCost);
			distribute(distpot);  
			oraclizeFeeTmp = oraclizeFee;
			oraclizeFee = 0;
		}
		emit newOraclizeCallback(0x0,result,howmany,pot,distpot,oraclizeFeeTmp,gaslimit,etherExchangeLikeCoin);
	}

	 
	function triggerStealManually3(string result,uint gaslimit) public payable ownerOrOperator {
		oraclizeFee = (gaslimit) * tx.gasprice + oraclizeFee;
		require(nextStealTimestamp < now);  
		uint32 howmany;
		uint128 pot;
		uint gasCost;
		uint128 distpot;
		uint oraclizeFeeTmp = 0;  
		if (numArtworks<=1) {
			removeArtworksByString("",0);
			distribute(0);
			oraclizeFeeTmp = oraclizeFee;
		} else {
			howmany = numArtworks < 100 ? (numArtworks < 10 ? (numArtworks < 2 ? 0 : 1) : numArtworks / 10) : 10;  
			pot = removeArtworksByString(result,howmany);
			gasCost = ((oraclizeFee * etherExchangeLikeCoin) / 1 ether) * 1 ether;
			if (pot > gasCost)
				distpot = uint128(pot - gasCost);
			distribute(distpot);  
			oraclizeFeeTmp = oraclizeFee;
			oraclizeFee = 0;
		}
		emit newOraclizeCallback(0x0,result,howmany,pot,distpot,oraclizeFeeTmp,gaslimit,etherExchangeLikeCoin);
	}


	 
	function timeTillNextSteal() constant internal returns(uint32) {
		return (86400 / (1 + numArtworks / 100)) / ( numOfTimesSteal );
	}

	 
	function triggerSteal(uint32 inseconds, uint gasAmount) internal {
		 
		uint gaslimit = gasleft();
		uint price = oraclize_getPrice(queryType, gasAmount);
		uint balancebefore = address(this).balance;
		require(price <= address(this).balance);
		if (numArtworks<=1) {
			removeArtworksByString("",0);
			distribute(0);
			nextStealId = 0x0;
			price = 0;
		} else {
			nextStealId = oraclize_query(nextStealTimestamp, queryType, randomQuery, gasAmount);
		}
		emit newTriggerOraclize(nextStealId, inseconds, gasAmount, price, balancebefore, address(this).balance);
		oraclizeFee = price + (gaslimit-gasleft() + 200000  ) * tx.gasprice;
	}

	 
	function findIndexFromRandomNumber(uint32 randomNumbers) internal returns (uint32 artworkId, uint16 index) {
		uint16 indexOldest;
		uint maxNumber;
		uint8 extraProbability;
		if (oldest==0)
			lastcombo = 0;
		(artworkId,indexOldest) = setOldest();
		if (lastcombo>oldestExtraStealProbability.length-1)
			extraProbability = oldestExtraStealProbability[oldestExtraStealProbability.length-1];
		else
			extraProbability = oldestExtraStealProbability[lastcombo];
		maxNumber = 100000 - extraProbability*1000;
		if (extraProbability>0 && randomNumbers>maxNumber) {
			index = indexOldest;
			artworkId = oldest;
		} else {
			index = mapToNewRange(randomNumbers, numArtworks, maxNumber);
			artworkId = ids[index];
		}
	}

	 
	function removeArtworksByString(string result,uint32 howmany) internal returns (uint128 pot) {
		uint32[] memory stolenArtworks = new uint32[](howmany);
		uint8[] memory artworkTypes = new uint8[](howmany);
		uint32[] memory sequenceNumbers = new uint32[](howmany);
		uint256[] memory artworkValues = new uint256[](howmany);
		address[] memory players = new address[](howmany);
		if (howmany>0) {
			uint32[] memory randomNumbers = getNumbersFromString(result, ",", howmany);
			uint16 index;
			uint32 artworkId;
			Artwork memory artworkData;
			pot = 0;
			if (oldest!=0)
				lastcombo++;
			for (uint32 i = 0; i < howmany; i++) {
				(artworkId,index) = findIndexFromRandomNumber(randomNumbers[i]);
				artworkData = artworks[artworkId];
				pot += artworkData.value;
				stolenArtworks[i] = artworkId;
				artworkTypes[i] = artworkData.artworkType;
				sequenceNumbers[i] = artworkData.sequenceNumber;
				artworkValues[i] = artworkData.value;
				players[i] = artworkData.player;
				replaceArtwork(index);
			}
		} else {
			pot = 0;
		}
		emit newSteal(now,stolenArtworks,artworkTypes,sequenceNumbers,artworkValues,players);
	}

	 
	function __callback(bytes32 myid, string result) public {
		uint gaslimit = gasleft();
		uint32 howmany;
		uint128 pot;
		uint gasCost;
		uint128 distpot;
		uint oraclizeFeeTmp = 0;  
		if (msg.sender == oraclize_cbAddress() && myid == nextStealId) {
			howmany = numArtworks < 100 ? (numArtworks < 10 ? (numArtworks < 2 ? 0 : 1) : numArtworks / 10) : 10;  
			pot = removeArtworksByString(result,howmany);
			gasCost = ((oraclizeFee * etherExchangeLikeCoin) / 1 ether) * 1 ether + 1 ether ;
			if (pot > gasCost)
				distpot = uint128(pot - gasCost);
			distribute(distpot);  
			oraclizeFeeTmp = oraclizeFee;
			oraclizeFee = 0;
		}
		emit newOraclizeCallback(myid,result,howmany,pot,distpot,oraclizeFeeTmp,gaslimit,etherExchangeLikeCoin);
	}

	 
	function updateNextStealTime(uint32 inseconds) internal {
		nextStealTimestamp = now + inseconds;
	}

	 
	function distribute(uint128 totalAmount) internal {
		uint32 artworkId;
		uint128 amount = ( totalAmount * 60 ) / 100;
		uint128 valueSum = 0;
		uint128 totalAmountRemain = totalAmount;
		uint128[] memory shares = new uint128[](values.length+1);
		if (totalAmount>0) {
			 
			for (uint8 v = 0; v < values.length; v++) {
				if (numArtworksXType[v] > 0) valueSum += values[v];
			}
			for (uint8 m = 0; m < values.length; m++) {
				if (numArtworksXType[m] > 0)
					shares[m] = ((amount * (values[m] * 1000 / valueSum) / numArtworksXType[m]) / (1000 ether)) * (1 ether);
			}
			for (uint16 i = 0; i < numArtworks; i++) {
				artworkId = ids[i];
				amount = shares[artworks[artworkId].artworkType];
				artworks[artworkId].value += amount;
				totalAmountRemain -= amount;
			}
			setOldest();
			artworks[oldest].value += totalAmountRemain;
			shares[shares.length-1] = totalAmountRemain;			
		}
		lastStealBlockNumber = block.number;
		updateNextStealTime(timeTillNextSteal());
		emit newStealRewards(totalAmount,shares);
	}


	
	 

	function get30Artworks(uint16 startIndex) public constant returns(uint32[] artworkIds,uint8[] types,uint32[] sequenceNumbers, uint128[] artworkValues,address[] players) {
		uint32 endIndex = startIndex + 30 > numArtworks ? numArtworks : startIndex + 30;
		uint32 id;
		uint32 num = endIndex - startIndex;
		artworkIds = new uint32[](num);
		types = new uint8[](num);
		sequenceNumbers = new uint32[](num);
		artworkValues = new uint128[](num);
		players = new address[](num);
		uint16 j = 0;		
		for (uint16 i = startIndex; i < endIndex; i++) {
			id = ids[i];
			artworkIds[j] = id;
			types[j] = artworks[id].artworkType;
			sequenceNumbers[j] = artworks[id].sequenceNumber;
			artworkValues[j] = artworks[id].value;
			players[j] = artworks[id].player;
			j++;
		}
	}

	function getRemainTime() public constant returns(uint remainTime) {
		if (nextStealTimestamp>now) remainTime = nextStealTimestamp - now;
	}

	 

	function setCustomGasPrice(uint gasPrice) public ownerOrOperator {
		oraclize_setCustomGasPrice(gasPrice);
	}

	function setOraclizeGas(uint32 newGas) public ownerOrOperator {
		oraclizeGas = newGas;
	}

	function setOraclizeGasExtraArtwork(uint32 newGas) public ownerOrOperator {
		oraclizeGasExtraArtwork = newGas;
	}

	function setEtherExchangeLikeCoin(uint32 newValue) public ownerOrOperator {
		etherExchangeLikeCoin = newValue;
	}

	function setMaxArtworks(uint16 number) public ownerOrOperator {
		maxArtworks = number;
	}
	
	function setNumOfTimesSteal(uint8 adjust) public ownerOrOperator {
		numOfTimesSteal = adjust;
	}

	function updateNextStealTimeByOperator(uint32 inseconds) public ownerOrOperator {
		nextStealTimestamp = now + inseconds;
	}


	 

	 
	function mapToNewRange(uint number, uint range, uint max) pure internal returns(uint16 randomNumber) {
		return uint16(number * range / max);
	}

	 
	function getNumbersFromString(string s, string delimiter, uint32 howmany) public pure returns(uint32[] numbers) {
		var s2 = s.toSlice();
		var delim = delimiter.toSlice();
		string[] memory parts = new string[](s2.count(delim) + 1);
		for(uint8 i = 0; i < parts.length; i++) {
			parts[i] = s2.split(delim).toString();
		}
		numbers = new uint32[](howmany);
		if (howmany>parts.length) howmany = uint32(parts.length);
		for (uint8 j = 0; j < howmany; j++) {
			numbers[j] = uint32(parseInt(parts[j]));
		}
		return numbers;
	}

	 
	function tokenCallback(address _from, uint256 _value, bytes _data) public {
		require(msg.sender == address(like));
		uint[] memory result;
		uint len;
		assembly {
			len := mload(_data)
			let c := 0
			result := mload(0x40)
			for { let i := 0 } lt(i, len) { i := add(i, 0x20) }
			{
				mstore(add(result, add(i, 0x20)), mload(add(_data, add(i, 0x20))))
				c := add(c, 1)
			}
			mstore(result, c)
			mstore(0x40, add(result , add(0x20, mul(c, 0x20))))
		}
		uint8[] memory result2 = new uint8[](result.length);
		for (uint16 j=0;j<result.length; j++) {
			result2[j] = uint8(result[j]);
		}
		giveArtworks(result2, _from, _value);
	}

}