pragma solidity ^0.4.23;

library SafeMath {

  
  function mul(uint256 a, uint256 b) internal pure returns (uint256 c) {
    if (a == 0) {
      return 0;
    }
    c = a * b;
    require(c / a == b, "Overflow - Multiplication");
    return c;
  }

  
  function div(uint256 a, uint256 b) internal pure returns (uint256) {
    return a / b;
  }

  
  function sub(uint256 a, uint256 b) internal pure returns (uint256) {
    require(b <= a, "Underflow - Subtraction");
    return a - b;
  }

  
  function add(uint256 a, uint256 b) internal pure returns (uint256 c) {
    c = a + b;
    require(c >= a, "Overflow - Addition");
    return c;
  }
}

library Contract {

  using SafeMath for uint;

  

  
  modifier conditions(function () pure first, function () pure last) {
    first();
    _;
    last();
  }

  bytes32 internal constant EXEC_PERMISSIONS = keccak256('script_exec_permissions');

  
  
  
  
  
  
  
  
  function authorize(address _script_exec) internal view {
    
    initialize();

    
    bytes32 perms = EXEC_PERMISSIONS;
    bool authorized;
    assembly {
      
      mstore(0, _script_exec)
      mstore(0x20, perms)
      
      mstore(0, keccak256(0x0c, 0x34))
      
      mstore(0x20, mload(0x80))
      
      authorized := sload(keccak256(0, 0x40))
    }
    if (!authorized)
      revert("Sender is not authorized as a script exec address");
  }

  
  
  
  
  
  
  
  
  
  function initialize() internal view {
    
    
    require(freeMem() == 0x80, "Memory allocated prior to execution");
    
    assembly {
      mstore(0x80, sload(0))     
      mstore(0xa0, sload(1))     
      mstore(0xc0, 0)            
      mstore(0xe0, 0)            
      mstore(0x100, 0)           
      mstore(0x120, 0)           
      mstore(0x140, 0)           
      mstore(0x160, 0)           

      
      mstore(0x40, 0x180)
    }
    
    assert(execID() != bytes32(0) && sender() != address(0));
  }

  
  
  function checks(function () view _check) conditions(validState, validState) internal view {
    _check();
  }

  
  
  function checks(function () pure _check) conditions(validState, validState) internal pure {
    _check();
  }

  
  
  function commit() conditions(validState, none) internal pure {
    
    bytes32 ptr = buffPtr();
    require(ptr >= 0x180, "Invalid buffer pointer");

    assembly {
      
      let size := mload(add(0x20, ptr))
      mstore(ptr, 0x20) 
      
      revert(ptr, add(0x40, size))
    }
  }

  

  
  function validState() private pure {
    if (freeMem() < 0x180)
      revert('Expected Contract.execute()');

    if (buffPtr() != 0 && buffPtr() < 0x180)
      revert('Invalid buffer pointer');

    assert(execID() != bytes32(0) && sender() != address(0));
  }

  
  function buffPtr() private pure returns (bytes32 ptr) {
    assembly { ptr := mload(0xc0) }
  }

  
  function freeMem() private pure returns (bytes32 ptr) {
    assembly { ptr := mload(0x40) }
  }

  
  function currentAction() private pure returns (bytes4 action) {
    if (buffPtr() == bytes32(0))
      return bytes4(0);

    assembly { action := mload(0xe0) }
  }

  
  function isStoring() private pure {
    if (currentAction() != STORES)
      revert('Invalid current action - expected STORES');
  }

  
  function isEmitting() private pure {
    if (currentAction() != EMITS)
      revert('Invalid current action - expected EMITS');
  }

  
  function isPaying() private pure {
    if (currentAction() != PAYS)
      revert('Invalid current action - expected PAYS');
  }

  
  function startBuffer() private pure {
    assembly {
      
      let ptr := msize()
      mstore(0xc0, ptr)
      
      mstore(ptr, 0)            
      mstore(add(0x20, ptr), 0) 
      
      mstore(0x40, add(0x40, ptr))
      
      mstore(0x100, 1)
    }
  }

  
  function validStoreBuff() private pure {
    
    if (buffPtr() == bytes32(0))
      startBuffer();

    
    
    if (stored() != 0 || currentAction() == STORES)
      revert('Duplicate request - stores');
  }

  
  function validEmitBuff() private pure {
    
    if (buffPtr() == bytes32(0))
      startBuffer();

    
    
    if (emitted() != 0 || currentAction() == EMITS)
      revert('Duplicate request - emits');
  }

  
  function validPayBuff() private pure {
    
    if (buffPtr() == bytes32(0))
      startBuffer();

    
    
    if (paid() != 0 || currentAction() == PAYS)
      revert('Duplicate request - pays');
  }

  
  function none() private pure { }

  

  
  function execID() internal pure returns (bytes32 exec_id) {
    assembly { exec_id := mload(0x80) }
    require(exec_id != bytes32(0), "Execution id overwritten, or not read");
  }

  
  function sender() internal pure returns (address addr) {
    assembly { addr := mload(0xa0) }
    require(addr != address(0), "Sender address overwritten, or not read");
  }

  

  
  
  function read(bytes32 _location) internal view returns (bytes32 data) {
    data = keccak256(_location, execID());
    assembly { data := sload(data) }
  }

  

  bytes4 internal constant EMITS = bytes4(keccak256('Emit((bytes32[],bytes)[])'));
  bytes4 internal constant STORES = bytes4(keccak256('Store(bytes32[])'));
  bytes4 internal constant PAYS = bytes4(keccak256('Pay(bytes32[])'));
  bytes4 internal constant THROWS = bytes4(keccak256('Error(string)'));

  
  enum NextFunction {
    INVALID, NONE, STORE_DEST, VAL_SET, VAL_INC, VAL_DEC, EMIT_LOG, PAY_DEST, PAY_AMT
  }

  
  function validStoreDest() private pure {
    
    if (expected() != NextFunction.STORE_DEST)
      revert('Unexpected function order - expected storage destination to be pushed');

    
    isStoring();
  }

  
  function validStoreVal() private pure {
    
    if (
      expected() != NextFunction.VAL_SET &&
      expected() != NextFunction.VAL_INC &&
      expected() != NextFunction.VAL_DEC
    ) revert('Unexpected function order - expected storage value to be pushed');

    
    isStoring();
  }

  
  function validPayDest() private pure {
    
    if (expected() != NextFunction.PAY_DEST)
      revert('Unexpected function order - expected payment destination to be pushed');

    
    isPaying();
  }

  
  function validPayAmt() private pure {
    
    if (expected() != NextFunction.PAY_AMT)
      revert('Unexpected function order - expected payment amount to be pushed');

    
    isPaying();
  }

  
  function validEvent() private pure {
    
    if (expected() != NextFunction.EMIT_LOG)
      revert('Unexpected function order - expected event to be pushed');

    
    isEmitting();
  }

  
  
  function storing() conditions(validStoreBuff, isStoring) internal pure {
    bytes4 action_req = STORES;
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), action_req)
      
      mstore(add(0x24, add(ptr, mload(ptr))), 0)
      
      mstore(ptr, add(0x24, mload(ptr)))
      
      mstore(0xe0, action_req)
      
      mstore(0x100, 2)
      
      mstore(sub(ptr, 0x20), add(ptr, mload(ptr)))
    }
    
    setFreeMem();
  }

  
  function set(bytes32 _field) conditions(validStoreDest, validStoreVal) internal pure returns (bytes32) {
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), _field)
      
      mstore(ptr, add(0x20, mload(ptr)))
      
      mstore(0x100, 3)
      
      mstore(
        mload(sub(ptr, 0x20)),
        add(1, mload(mload(sub(ptr, 0x20))))
      )
      
      mstore(0x120, add(1, mload(0x120)))
    }
    
    setFreeMem();
    return _field;
  }

  
  function to(bytes32, bytes32 _val) conditions(validStoreVal, validStoreDest) internal pure {
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), _val)
      
      mstore(ptr, add(0x20, mload(ptr)))
      
      mstore(0x100, 2)
    }
    
    setFreeMem();
  }

  
  function to(bytes32 _field, uint _val) internal pure {
    to(_field, bytes32(_val));
  }

  
  function to(bytes32 _field, address _val) internal pure {
    to(_field, bytes32(_val));
  }

  
  function to(bytes32 _field, bool _val) internal pure {
    to(
      _field,
      _val ? bytes32(1) : bytes32(0)
    );
  }

  function increase(bytes32 _field) conditions(validStoreDest, validStoreVal) internal view returns (bytes32 val) {
    
    val = keccak256(_field, execID());
    assembly {
      val := sload(val)
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), _field)
      
      mstore(ptr, add(0x20, mload(ptr)))
      
      mstore(0x100, 4)
      
      mstore(
        mload(sub(ptr, 0x20)),
        add(1, mload(mload(sub(ptr, 0x20))))
      )
      
      mstore(0x120, add(1, mload(0x120)))
    }
    
    setFreeMem();
    return val;
  }

  function decrease(bytes32 _field) conditions(validStoreDest, validStoreVal) internal view returns (bytes32 val) {
    
    val = keccak256(_field, execID());
    assembly {
      val := sload(val)
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), _field)
      
      mstore(ptr, add(0x20, mload(ptr)))
      
      mstore(0x100, 5)
      
      mstore(
        mload(sub(ptr, 0x20)),
        add(1, mload(mload(sub(ptr, 0x20))))
      )
      
      mstore(0x120, add(1, mload(0x120)))
    }
    
    setFreeMem();
    return val;
  }

  function by(bytes32 _val, uint _amt) conditions(validStoreVal, validStoreDest) internal pure {
    
    
    if (expected() == NextFunction.VAL_INC)
      _amt = _amt.add(uint(_val));
    else if (expected() == NextFunction.VAL_DEC)
      _amt = uint(_val).sub(_amt);
    else
      revert('Expected VAL_INC or VAL_DEC');

    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), _amt)
      
      mstore(ptr, add(0x20, mload(ptr)))
      
      mstore(0x100, 2)
    }
    
    setFreeMem();
  }

  
  function byMaximum(bytes32 _val, uint _amt) conditions(validStoreVal, validStoreDest) internal pure {
    
    
    if (expected() == NextFunction.VAL_DEC) {
      if (_amt >= uint(_val))
        _amt = 0;
      else
        _amt = uint(_val).sub(_amt);
    } else {
      revert('Expected VAL_DEC');
    }

    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), _amt)
      
      mstore(ptr, add(0x20, mload(ptr)))
      
      mstore(0x100, 2)
    }
    
    setFreeMem();
  }

  
  
  function emitting() conditions(validEmitBuff, isEmitting) internal pure {
    bytes4 action_req = EMITS;
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), action_req)
      
      mstore(add(0x24, add(ptr, mload(ptr))), 0)
      
      mstore(ptr, add(0x24, mload(ptr)))
      
      mstore(0xe0, action_req)
      
      mstore(0x100, 6)
      
      mstore(sub(ptr, 0x20), add(ptr, mload(ptr)))
    }
    
    setFreeMem();
  }

  function log(bytes32 _data) conditions(validEvent, validEvent) internal pure {
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), 0)
      
      if eq(_data, 0) {
        mstore(add(0x40, add(ptr, mload(ptr))), 0)
        
        mstore(ptr, add(0x40, mload(ptr)))
      }
      
      if iszero(eq(_data, 0)) {
        
        mstore(add(0x40, add(ptr, mload(ptr))), 0x20)
        
        mstore(add(0x60, add(ptr, mload(ptr))), _data)
        
        mstore(ptr, add(0x60, mload(ptr)))
      }
      
      mstore(
        mload(sub(ptr, 0x20)),
        add(1, mload(mload(sub(ptr, 0x20))))
      )
      
      mstore(0x140, add(1, mload(0x140)))
    }
    
    setFreeMem();
  }

  function log(bytes32[1] memory _topics, bytes32 _data) conditions(validEvent, validEvent) internal pure {
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), 1)
      
      mstore(add(0x40, add(ptr, mload(ptr))), mload(_topics))
      
      if eq(_data, 0) {
        mstore(add(0x60, add(ptr, mload(ptr))), 0)
        
        mstore(ptr, add(0x60, mload(ptr)))
      }
      
      if iszero(eq(_data, 0)) {
        
        mstore(add(0x60, add(ptr, mload(ptr))), 0x20)
        
        mstore(add(0x80, add(ptr, mload(ptr))), _data)
        
        mstore(ptr, add(0x80, mload(ptr)))
      }
      
      mstore(
        mload(sub(ptr, 0x20)),
        add(1, mload(mload(sub(ptr, 0x20))))
      )
      
      mstore(0x140, add(1, mload(0x140)))
    }
    
    setFreeMem();
  }

  function log(bytes32[2] memory _topics, bytes32 _data) conditions(validEvent, validEvent) internal pure {
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), 2)
      
      mstore(add(0x40, add(ptr, mload(ptr))), mload(_topics))
      mstore(add(0x60, add(ptr, mload(ptr))), mload(add(0x20, _topics)))
      
      if eq(_data, 0) {
        mstore(add(0x80, add(ptr, mload(ptr))), 0)
        
        mstore(ptr, add(0x80, mload(ptr)))
      }
      
      if iszero(eq(_data, 0)) {
        
        mstore(add(0x80, add(ptr, mload(ptr))), 0x20)
        
        mstore(add(0xa0, add(ptr, mload(ptr))), _data)
        
        mstore(ptr, add(0xa0, mload(ptr)))
      }
      
      mstore(
        mload(sub(ptr, 0x20)),
        add(1, mload(mload(sub(ptr, 0x20))))
      )
      
      mstore(0x140, add(1, mload(0x140)))
    }
    
    setFreeMem();
  }

  function log(bytes32[3] memory _topics, bytes32 _data) conditions(validEvent, validEvent) internal pure {
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), 3)
      
      mstore(add(0x40, add(ptr, mload(ptr))), mload(_topics))
      mstore(add(0x60, add(ptr, mload(ptr))), mload(add(0x20, _topics)))
      mstore(add(0x80, add(ptr, mload(ptr))), mload(add(0x40, _topics)))
      
      if eq(_data, 0) {
        mstore(add(0xa0, add(ptr, mload(ptr))), 0)
        
        mstore(ptr, add(0xa0, mload(ptr)))
      }
      
      if iszero(eq(_data, 0)) {
        
        mstore(add(0xa0, add(ptr, mload(ptr))), 0x20)
        
        mstore(add(0xc0, add(ptr, mload(ptr))), _data)
        
        mstore(ptr, add(0xc0, mload(ptr)))
      }
      
      mstore(
        mload(sub(ptr, 0x20)),
        add(1, mload(mload(sub(ptr, 0x20))))
      )
      
      mstore(0x140, add(1, mload(0x140)))
    }
    
    setFreeMem();
  }

  function log(bytes32[4] memory _topics, bytes32 _data) conditions(validEvent, validEvent) internal pure {
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), 4)
      
      mstore(add(0x40, add(ptr, mload(ptr))), mload(_topics))
      mstore(add(0x60, add(ptr, mload(ptr))), mload(add(0x20, _topics)))
      mstore(add(0x80, add(ptr, mload(ptr))), mload(add(0x40, _topics)))
      mstore(add(0xa0, add(ptr, mload(ptr))), mload(add(0x60, _topics)))
      
      if eq(_data, 0) {
        mstore(add(0xc0, add(ptr, mload(ptr))), 0)
        
        mstore(ptr, add(0xc0, mload(ptr)))
      }
      
      if iszero(eq(_data, 0)) {
        
        mstore(add(0xc0, add(ptr, mload(ptr))), 0x20)
        
        mstore(add(0xe0, add(ptr, mload(ptr))), _data)
        
        mstore(ptr, add(0xe0, mload(ptr)))
      }
      
      mstore(
        mload(sub(ptr, 0x20)),
        add(1, mload(mload(sub(ptr, 0x20))))
      )
      
      mstore(0x140, add(1, mload(0x140)))
    }
    
    setFreeMem();
  }

  
  
  function paying() conditions(validPayBuff, isPaying) internal pure {
    bytes4 action_req = PAYS;
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), action_req)
      
      mstore(add(0x24, add(ptr, mload(ptr))), 0)
      
      mstore(ptr, add(0x24, mload(ptr)))
      
      mstore(0xe0, action_req)
      
      mstore(0x100, 8)
      
      mstore(sub(ptr, 0x20), add(ptr, mload(ptr)))
    }
    
    setFreeMem();
  }

  
  function pay(uint _amount) conditions(validPayAmt, validPayDest) internal pure returns (uint) {
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), _amount)
      
      mstore(ptr, add(0x20, mload(ptr)))
      
      mstore(0x100, 7)
      
      mstore(
        mload(sub(ptr, 0x20)),
        add(1, mload(mload(sub(ptr, 0x20))))
      )
      
      mstore(0x160, add(1, mload(0x160)))
    }
    
    setFreeMem();
    return _amount;
  }

  
  function toAcc(uint, address _dest) conditions(validPayDest, validPayAmt) internal pure {
    assembly {
      
      let ptr := add(0x20, mload(0xc0))
      
      mstore(add(0x20, add(ptr, mload(ptr))), _dest)
      
      mstore(ptr, add(0x20, mload(ptr)))
      
      mstore(0x100, 8)
    }
    
    setFreeMem();
  }

  
  function setFreeMem() private pure {
    assembly { mstore(0x40, msize) }
  }

  
  function expected() private pure returns (NextFunction next) {
    assembly { next := mload(0x100) }
  }

  
  function emitted() internal pure returns (uint num_emitted) {
    if (buffPtr() == bytes32(0))
      return 0;

    
    assembly { num_emitted := mload(0x140) }
  }

  
  function stored() internal pure returns (uint num_stored) {
    if (buffPtr() == bytes32(0))
      return 0;

    
    assembly { num_stored := mload(0x120) }
  }

  
  function paid() internal pure returns (uint num_paid) {
    if (buffPtr() == bytes32(0))
      return 0;

    
    assembly { num_paid := mload(0x160) }
  }
}

library Provider {

  using Contract for *;

  
  function appIndex() internal pure returns (bytes32)
    { return keccak256('index'); }

  
  function execPermissions(address _exec) internal pure returns (bytes32)
    { return keccak256(_exec, keccak256('script_exec_permissions')); }

  
  function appSelectors(bytes4 _selector) internal pure returns (bytes32)
    { return keccak256(_selector, 'implementation'); }

  
  function registeredApps() internal pure returns (bytes32)
    { return keccak256(bytes32(Contract.sender()), 'app_list'); }

  
  function appBase(bytes32 _app) internal pure returns (bytes32)
    { return keccak256(_app, keccak256(bytes32(Contract.sender()), 'app_base')); }

  
  function appVersionList(bytes32 _app) internal pure returns (bytes32)
    { return keccak256('versions', appBase(_app)); }

  
  function versionBase(bytes32 _app, bytes32 _version) internal pure returns (bytes32)
    { return keccak256(_version, 'version', appBase(_app)); }

  
  function versionIndex(bytes32 _app, bytes32 _version) internal pure returns (bytes32)
    { return keccak256('index', versionBase(_app, _version)); }

  
  function versionSelectors(bytes32 _app, bytes32 _version) internal pure returns (bytes32)
    { return keccak256('selectors', versionBase(_app, _version)); }

  
  function versionAddresses(bytes32 _app, bytes32 _version) internal pure returns (bytes32)
    { return keccak256('addresses', versionBase(_app, _version)); }

  
  function previousVersion(bytes32 _app, bytes32 _version) internal pure returns (bytes32)
    { return keccak256("previous version", versionBase(_app, _version)); }

  
  function appVersionListAt(bytes32 _app, uint _index) internal pure returns (bytes32)
    { return bytes32((32 * _index) + uint(appVersionList(_app))); }

  
  function registerApp(bytes32 _app, address _index, bytes4[] _selectors, address[] _implementations) external view {
    
    Contract.authorize(msg.sender);

    
    if (Contract.read(appBase(_app)) != bytes32(0))
      revert("app is already registered");

    if (_selectors.length != _implementations.length || _selectors.length == 0)
      revert("invalid input arrays");

    
    Contract.storing();

    
    uint num_registered_apps = uint(Contract.read(registeredApps()));

    Contract.increase(registeredApps()).by(uint(1));

    Contract.set(
      bytes32(32 * (num_registered_apps + 1) + uint(registeredApps()))
    ).to(_app);

    
    Contract.set(appBase(_app)).to(_app);

    
    Contract.set(versionBase(_app, _app)).to(_app);

    
    Contract.set(appVersionList(_app)).to(uint(1));

    Contract.set(
      bytes32(32 + uint(appVersionList(_app)))
    ).to(_app);

    
    Contract.set(versionIndex(_app, _app)).to(_index);

    
    
    Contract.set(versionSelectors(_app, _app)).to(_selectors.length);
    Contract.set(versionAddresses(_app, _app)).to(_implementations.length);
    for (uint i = 0; i < _selectors.length; i++) {
      Contract.set(bytes32(32 * (i + 1) + uint(versionSelectors(_app, _app)))).to(_selectors[i]);
      Contract.set(bytes32(32 * (i + 1) + uint(versionAddresses(_app, _app)))).to(_implementations[i]);
    }

    
    Contract.set(previousVersion(_app, _app)).to(uint(0));

    
    Contract.commit();
  }

  function registerAppVersion(bytes32 _app, bytes32 _version, address _index, bytes4[] _selectors, address[] _implementations) external view {
    
    Contract.authorize(msg.sender);

    
    
    if (Contract.read(appBase(_app)) == bytes32(0))
      revert("App has not been registered");

    if (Contract.read(versionBase(_app, _version)) != bytes32(0))
      revert("Version already exists");

    if (
      _selectors.length != _implementations.length ||
      _selectors.length == 0
    ) revert("Invalid input array lengths");

    
    Contract.storing();

    
    Contract.set(versionBase(_app, _version)).to(_version);

    
    uint num_versions = uint(Contract.read(appVersionList(_app)));
    Contract.set(appVersionListAt(_app, (num_versions + 1))).to(_version);
    Contract.set(appVersionList(_app)).to(num_versions + 1);

    
    Contract.set(versionIndex(_app, _version)).to(_index);

    
    
    Contract.set(versionSelectors(_app, _version)).to(_selectors.length);
    Contract.set(versionAddresses(_app, _version)).to(_implementations.length);
    for (uint i = 0; i < _selectors.length; i++) {
      Contract.set(bytes32(32 * (i + 1) + uint(versionSelectors(_app, _version)))).to(_selectors[i]);
      Contract.set(bytes32(32 * (i + 1) + uint(versionAddresses(_app, _version)))).to(_implementations[i]);
    }

    
    bytes32 prev_version = Contract.read(bytes32(32 * num_versions + uint(appVersionList(_app))));
    Contract.set(previousVersion(_app, _version)).to(prev_version);

    
    Contract.commit();
  }

  
  function updateInstance(bytes32 _app_name, bytes32 _current_version, bytes32 _registry_id) external view {
    
    Contract.authorize(msg.sender);

    
    require(_app_name != 0 && _current_version != 0 && _registry_id != 0, 'invalid input');

    
    bytes4[] memory current_selectors = getVersionSelectors(_app_name, _current_version, _registry_id);
    require(current_selectors.length != 0, 'invalid current version');

    
    bytes32 latest_version = getLatestVersion(_app_name, _registry_id);
    require(latest_version != _current_version, 'current version is already latest');
    require(latest_version != 0, 'invalid latest version');

    
    
    address latest_idx = getVersionIndex(_app_name, latest_version, _registry_id);
    bytes4[] memory latest_selectors = getVersionSelectors(_app_name, latest_version, _registry_id);
    address[] memory latest_impl = getVersionImplementations(_app_name, latest_version, _registry_id);
    require(latest_idx != 0, 'invalid version idx address');
    require(latest_selectors.length != 0 && latest_selectors.length == latest_impl.length, 'invalid implementation specification');

    
    Contract.storing();

    
    for (uint i = 0; i < current_selectors.length; i++)
      Contract.set(appSelectors(current_selectors[i])).to(address(0));

    
    Contract.set(appIndex()).to(latest_idx);

    
    for (i = 0; i < latest_selectors.length; i++) {
      require(latest_selectors[i] != 0 && latest_impl[i] != 0, 'invalid input - expected nonzero implementation');
      Contract.set(appSelectors(latest_selectors[i])).to(latest_impl[i]);
    }

    
    Contract.commit();
  }

  
  function updateExec(address _new_exec_addr) external view {
    
    Contract.authorize(msg.sender);

    
    require(_new_exec_addr != 0, 'invalid replacement');

    
    Contract.storing();

    
    Contract.set(execPermissions(msg.sender)).to(false);

    
    Contract.set(execPermissions(_new_exec_addr)).to(true);

    
    Contract.commit();
  }

  

  function registryRead(bytes32 _location, bytes32 _registry_id) internal view returns (bytes32 value) {
    _location = keccak256(_location, _registry_id);
    assembly { value := sload(_location) }
  }

  

  
  function getLatestVersion(bytes32 _app, bytes32 _registry_id) internal view returns (bytes32) {
    uint length = uint(registryRead(appVersionList(_app), _registry_id));
    
    return registryRead(appVersionListAt(_app, length), _registry_id);
  }

  
  function getVersionIndex(bytes32 _app, bytes32 _version, bytes32 _registry_id) internal view returns (address) {
    return address(registryRead(versionIndex(_app, _version), _registry_id));
  }

  
  function getVersionImplementations(bytes32 _app, bytes32 _version, bytes32 _registry_id) internal view returns (address[] memory impl) {
    
    uint length = uint(registryRead(versionAddresses(_app, _version), _registry_id));
    
    impl = new address[](length);
    
    for (uint i = 0; i < length; i++) {
      bytes32 location = bytes32(32 * (i + 1) + uint(versionAddresses(_app, _version)));
      impl[i] = address(registryRead(location, _registry_id));
    }
  }

  
  function getVersionSelectors(bytes32 _app, bytes32 _version, bytes32 _registry_id) internal view returns (bytes4[] memory sels) {
    
    uint length = uint(registryRead(versionSelectors(_app, _version), _registry_id));
    
    sels = new bytes4[](length);
    
    for (uint i = 0; i < length; i++) {
      bytes32 location = bytes32(32 * (i + 1) + uint(versionSelectors(_app, _version)));
      sels[i] = bytes4(registryRead(location, _registry_id));
    }
  }

}