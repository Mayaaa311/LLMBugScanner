// Copyright (C) 2019  Argent Labs Ltd. <https://argent.xyz>

// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

pragma solidity ^0.5.4;
import "./MakerV2Base.sol";
import "../../infrastructure/MakerRegistry.sol";

interface IUniswapFactory {
    function getExchange(address _token) external view returns(IUniswapExchange);
}

interface IUniswapExchange {
    function getEthToTokenOutputPrice(uint256 _tokensBought) external view returns (uint256);
    function getEthToTokenInputPrice(uint256 _ethSold) external view returns (uint256);
    function getTokenToEthOutputPrice(uint256 _ethBought) external view returns (uint256);
    function getTokenToEthInputPrice(uint256 _tokensSold) external view returns (uint256);
}

/**
 * @title MakerV2Loan
 * @dev Module to migrate old CDPs and open and manage new vaults. The vaults managed by
 * this module are directly owned by the module. This is to prevent a compromised wallet owner
 * from being able to use `TransferManager.callContract()` to transfer ownership of a vault
 * (a type of asset NOT protected by a wallet's daily limit) to another account.
 * @author Olivier VDB - <olivier@argent.xyz>
 */
contract MakerV2Loan is MakerV2Base {

    // The address of the MKR token
    GemLike internal mkrToken;
    // The address of the WETH token
    GemLike internal wethToken;
    // The address of the WETH Adapter
    JoinLike internal wethJoin;
    // The address of the Jug
    JugLike internal jug;
    // The address of the Vault Manager (referred to as 'CdpManager' to match Maker's naming)
    ManagerLike internal cdpManager;
    // The address of the SCD Tub
    SaiTubLike internal tub;
    // The Maker Registry in which all supported collateral tokens and their adapters are stored
    MakerRegistry internal makerRegistry;
    // The Uniswap Exchange contract for DAI
    IUniswapExchange internal daiUniswap;
    // The Uniswap Exchange contract for MKR
    IUniswapExchange internal mkrUniswap;
    // Mapping [wallet][ilk] -> loanId, that keeps track of cdp owners
    // while also enforcing a maximum of one loan per token (ilk) and per wallet
    // (which will make future upgrades of the module easier)
    mapping(address => mapping(bytes32 => bytes32)) public loanIds;
    // Lock used by nonReentrant()
    bool private _notEntered = true;

    // Mock token address for ETH
    address constant internal ETH_TOKEN_ADDRESS = 0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE;

    // ****************** Events *************************** //

    // Emitted when an SCD CDP is converted into an MCD vault
    event CdpMigrated(address indexed _wallet, bytes32 _oldCdpId, bytes32 _newVaultId);
    // Vault management events
    event LoanOpened(
        address indexed _wallet,
        bytes32 indexed _loanId,
        address _collateral,
        uint256 _collateralAmount,
        address _debtToken,
        uint256 _debtAmount
    );
    event LoanClosed(address indexed _wallet, bytes32 indexed _loanId);
    event CollateralAdded(address indexed _wallet, bytes32 indexed _loanId, address _collateral, uint256 _collateralAmount);
    event CollateralRemoved(address indexed _wallet, bytes32 indexed _loanId, address _collateral, uint256 _collateralAmount);
    event DebtAdded(address indexed _wallet, bytes32 indexed _loanId, address _debtToken, uint256 _debtAmount);
    event DebtRemoved(address indexed _wallet, bytes32 indexed _loanId, address _debtToken, uint256 _debtAmount);


    // *************** Modifiers *************************** //

    /**
     * @dev Throws if the sender is not an authorised module.
     */
    modifier onlyModule(BaseWallet _wallet) {
        require(_wallet.authorised(msg.sender), "MV2: sender unauthorized");
        _;
    }

    /**
     * @dev Prevents call reentrancy
     */
    modifier nonReentrant() {
        require(_notEntered, "MV2: reentrant call");
        _notEntered = false;
        _;
        _notEntered = true;
    }

    // *************** Constructor ********************** //

    constructor(
        JugLike _jug,
        MakerRegistry _makerRegistry,
        IUniswapFactory _uniswapFactory
    )
        public
    {
        cdpManager = ScdMcdMigrationLike(scdMcdMigration).cdpManager();
        tub = ScdMcdMigrationLike(scdMcdMigration).tub();
        wethJoin = ScdMcdMigrationLike(scdMcdMigration).wethJoin();
        wethToken = wethJoin.gem();
        mkrToken = tub.gov();
        jug = _jug;
        makerRegistry = _makerRegistry;
        daiUniswap = _uniswapFactory.getExchange(address(daiToken));
        mkrUniswap = _uniswapFactory.getExchange(address(mkrToken));
        // Authorize daiJoin to exit DAI from the module's internal balance in the vat
        vat.hope(address(daiJoin));
    }

    // *************** External/Public Functions ********************* //

    /* ********************************** Implementation of Loan ************************************* */

   /**
     * @dev Opens a collateralized loan.
     * @param _wallet The target wallet.
     * @param _collateral The token used as a collateral.
     * @param _collateralAmount The amount of collateral token provided.
     * @param _debtToken The token borrowed (must be the address of the DAI contract).
     * @param _debtAmount The amount of tokens borrowed.
     * @return The ID of the created vault.
     */
    function openLoan(
        BaseWallet _wallet,
        address _collateral,
        uint256 _collateralAmount,
        address _debtToken,
        uint256 _debtAmount
    )
        external
        onlyWalletOwner(_wallet)
        onlyWhenUnlocked(_wallet)
        returns (bytes32 _loanId)
    {
        verifySupportedCollateral(_collateral);
        require(_debtToken == address(daiToken), "MV2: debt token not DAI");
        _loanId = bytes32(openVault(_wallet, _collateral, _collateralAmount, _debtAmount));
        emit LoanOpened(address(_wallet), _loanId, _collateral, _collateralAmount, _debtToken, _debtAmount);
    }

    /**
     * @dev Adds collateral to a loan identified by its ID.
     * @param _wallet The target wallet.
     * @param _loanId The ID of the target vault.
     * @param _collateral The token used as a collateral.
     * @param _collateralAmount The amount of collateral to add.
     */
    function addCollateral(
        BaseWallet _wallet,
        bytes32 _loanId,
        address _collateral,
        uint256 _collateralAmount
    )
        external
        onlyWalletOwner(_wallet)
        onlyWhenUnlocked(_wallet)
    {
        verifyLoanOwner(_wallet, _loanId);
        addCollateral(_wallet, uint256(_loanId), _collateralAmount);
        emit CollateralAdded(address(_wallet), _loanId, _collateral, _collateralAmount);
    }

    /**
     * @dev Removes collateral from a loan identified by its ID.
     * @param _wallet The target wallet.
     * @param _loanId The ID of the target vault.
     * @param _collateral The token used as a collateral.
     * @param _collateralAmount The amount of collateral to remove.
     */
    function removeCollateral(
        BaseWallet _wallet,
        bytes32 _loanId,
        address _collateral,
        uint256 _collateralAmount
    )
        external
        onlyWalletOwner(_wallet)
        onlyWhenUnlocked(_wallet)
    {
        verifyLoanOwner(_wallet, _loanId);
        removeCollateral(_wallet, uint256(_loanId), _collateralAmount);
        emit CollateralRemoved(address(_wallet), _loanId, _collateral, _collateralAmount);
    }

    /**
     * @dev Increases the debt by borrowing more token from a loan identified by its ID.
     * @param _wallet The target wallet.
     * @param _loanId The ID of the target vault.
     * @param _debtToken The token borrowed (must be the address of the DAI contract).
     * @param _debtAmount The amount of token to borrow.
     */
    function addDebt(
        BaseWallet _wallet,
        bytes32 _loanId,
        address _debtToken,
        uint256 _debtAmount
    )
        external
        onlyWalletOwner(_wallet)
        onlyWhenUnlocked(_wallet)
    {
        verifyLoanOwner(_wallet, _loanId);
        addDebt(_wallet, uint256(_loanId), _debtAmount);
        emit DebtAdded(address(_wallet), _loanId, _debtToken, _debtAmount);
    }

    /**
     * @dev Decreases the debt by repaying some token from a loan identified by its ID.
     * @param _wallet The target wallet.
     * @param _loanId The ID of the target vault.
     * @param _debtToken The token to repay (must be the address of the DAI contract).
     * @param _debtAmount The amount of token to repay.
     */
    function removeDebt(
        BaseWallet _wallet,
        bytes32 _loanId,
        address _debtToken,
        uint256 _debtAmount
    )
        external
        onlyWalletOwner(_wallet)
        onlyWhenUnlocked(_wallet)
    {
        verifyLoanOwner(_wallet, _loanId);
        updateStabilityFee(uint256(_loanId));
        removeDebt(_wallet, uint256(_loanId), _debtAmount);
        emit DebtRemoved(address(_wallet), _loanId, _debtToken, _debtAmount);
    }

    /**
     * @dev Closes a collateralized loan by repaying all debts (plus interest) and redeeming all collateral.
     * @param _wallet The target wallet.
     * @param _loanId The ID of the target vault.
     */
    function closeLoan(
        BaseWallet _wallet,
        bytes32 _loanId
    )
        external
        onlyWalletOwner(_wallet)
        onlyWhenUnlocked(_wallet)
    {
        verifyLoanOwner(_wallet, _loanId);
        updateStabilityFee(uint256(_loanId));
        closeVault(_wallet, uint256(_loanId));
        emit LoanClosed(address(_wallet), _loanId);
    }

    /* *************************************** Other vault methods ***************************************** */

    /**
     * @dev Lets a vault owner transfer their vault from their wallet to the present module so the vault
     * can be managed by the module.
     * @param _wallet The target wallet.
     * @param _loanId The ID of the target vault.
     */
    function acquireLoan(
        BaseWallet _wallet,
        bytes32 _loanId
    )
        external
        nonReentrant
        onlyWalletOwner(_wallet)
        onlyWhenUnlocked(_wallet)
    {
        require(cdpManager.owns(uint256(_loanId)) == address(_wallet), "MV2: wrong vault owner");
        // Transfer the vault from the wallet to the module
        invokeWallet(
            address(_wallet),
            address(cdpManager),
            0,
            abi.encodeWithSignature("give(uint256,address)", uint256(_loanId), address(this))
        );
        require(cdpManager.owns(uint256(_loanId)) == address(this), "MV2: failed give");
        // Mark the incoming vault as belonging to the wallet (or merge it into the existing vault if there is one)
        assignLoanToWallet(_wallet, _loanId);
    }

    /**
     * @dev Lets a SCD CDP owner migrate their CDP to use the new MCD engine.
     * Requires MKR or ETH to pay the SCD governance fee
     * @param _wallet The target wallet.
     * @param _cup id of the old SCD CDP to migrate
     */
    function migrateCdp(
        BaseWallet _wallet,
        bytes32 _cup
    )
        external
        onlyWalletOwner(_wallet)
        onlyWhenUnlocked(_wallet)
        returns (bytes32 _loanId)
    {
        (uint daiPerMkr, bool ok) = tub.pep().peek();
        if (ok && daiPerMkr != 0) {
            // get governance fee in MKR
            uint mkrFee = tub.rap(_cup).wdiv(daiPerMkr);
            // Convert some ETH into MKR with Uniswap if necessary
            buyTokens(_wallet, mkrToken, mkrFee, mkrUniswap);
            // Transfer the MKR to the Migration contract
            invokeWallet(address(_wallet), address(mkrToken), 0, abi.encodeWithSignature("transfer(address,uint256)", address(scdMcdMigration), mkrFee));
        }
        // Transfer ownership of the SCD CDP to the migration contract
        invokeWallet(address(_wallet), address(tub), 0, abi.encodeWithSignature("give(bytes32,address)", _cup, address(scdMcdMigration)));
        // Update stability fee rate
        jug.drip(wethJoin.ilk());
        // Execute the CDP migration
        _loanId = bytes32(ScdMcdMigrationLike(scdMcdMigration).migrate(_cup));
        // Mark the new vault as belonging to the wallet (or merge it into the existing vault if there is one)
        _loanId = assignLoanToWallet(_wallet, _loanId);

        emit CdpMigrated(address(_wallet), _cup, _loanId);
    }

    /**
     * @dev Lets a future upgrade of this module transfer a vault to itself
     * @param _wallet The target wallet.
     * @param _loanId The ID of the target vault.
     */
    function giveVault(
        BaseWallet _wallet,
        bytes32 _loanId
    )
        external
        onlyModule(_wallet)
        onlyWhenUnlocked(_wallet)
    {
        verifyLoanOwner(_wallet, _loanId);
        cdpManager.give(uint256(_loanId), msg.sender);
        clearLoanOwner(_wallet, _loanId);
    }

    /* ************************************** Internal Functions ************************************** */

    function toInt(uint256 _x) internal pure returns (int _y) {
        _y = int(_x);
        require(_y >= 0, "MV2: int overflow");
    }

    function assignLoanToWallet(BaseWallet _wallet, bytes32 _loanId) internal returns (bytes32 _assignedLoanId) {
        bytes32 ilk = cdpManager.ilks(uint256(_loanId));
        // Check if the user already holds a vault in the MakerV2Manager
        bytes32 existingLoanId = loanIds[address(_wallet)][ilk];
        if (existingLoanId > 0) {
            // Merge the new loan into the existing loan
            cdpManager.shift(uint256(_loanId), uint256(existingLoanId));
            return existingLoanId;
        }
        // Record the new vault as belonging to the wallet
        loanIds[address(_wallet)][ilk] = _loanId;
        return _loanId;
    }

    function clearLoanOwner(BaseWallet _wallet, bytes32 _loanId) internal {
        delete loanIds[address(_wallet)][cdpManager.ilks(uint256(_loanId))];
    }

    function verifyLoanOwner(BaseWallet _wallet, bytes32 _loanId) internal view {
        require(loanIds[address(_wallet)][cdpManager.ilks(uint256(_loanId))] == _loanId, "MV2: unauthorized loanId");
    }

    function verifySupportedCollateral(address _collateral) internal view {
        if (_collateral != ETH_TOKEN_ADDRESS) {
            (bool collateralSupported,,,) = makerRegistry.collaterals(_collateral);
            require(collateralSupported, "MV2: unsupported collateral");
        }
    }

    function buyTokens(
        BaseWallet _wallet,
        GemLike _token,
        uint256 _tokenAmountRequired,
        IUniswapExchange _uniswapExchange
    )
        internal
    {
        // get token balance
        uint256 tokenBalance = _token.balanceOf(address(_wallet));
        if (tokenBalance < _tokenAmountRequired) {
            // Not enough tokens => Convert some ETH into tokens with Uniswap
            uint256 etherValueOfTokens = _uniswapExchange.getEthToTokenOutputPrice(_tokenAmountRequired - tokenBalance);
            // solium-disable-next-line security/no-block-members
            invokeWallet(address(_wallet), address(_uniswapExchange), etherValueOfTokens, abi.encodeWithSignature("ethToTokenSwapOutput(uint256,uint256)", _tokenAmountRequired - tokenBalance, now));
        }
    }

    function joinCollateral(
        BaseWallet _wallet,
        uint256 _cdpId,
        uint256 _collateralAmount,
        bytes32 _ilk
    )
        internal
    {
        // Get the adapter and collateral token for the vault
        (JoinLike gemJoin, GemLike collateral) = makerRegistry.getCollateral(_ilk);
        // Convert ETH to WETH if needed
        if (gemJoin == wethJoin) {
            invokeWallet(address(_wallet), address(wethToken), _collateralAmount, abi.encodeWithSignature("deposit()"));
        }
        // Send the collateral to the module
        invokeWallet(
            address(_wallet),
            address(collateral),
            0,
            abi.encodeWithSignature("transfer(address,uint256)", address(this), _collateralAmount)
        );
        // Approve the adapter to pull the collateral from the module
        collateral.approve(address(gemJoin), _collateralAmount);
        // Join collateral to the adapter. The first argument to `join` is the address that *technically* owns the vault
        gemJoin.join(cdpManager.urns(_cdpId), _collateralAmount);
    }

    function joinDebt(
        BaseWallet _wallet,
        uint256 _cdpId,
        uint256 _debtAmount //  art.mul(rate).div(RAY) === [wad]*[ray]/[ray]=[wad]
    )
        internal
    {
        // Send the DAI to the module
        invokeWallet(address(_wallet), address(daiToken), 0, abi.encodeWithSignature("transfer(address,uint256)", address(this), _debtAmount));
        // Approve the DAI adapter to burn DAI from the module
        daiToken.approve(address(daiJoin), _debtAmount);
        // Join DAI to the adapter. The first argument to `join` is the address that *technically* owns the vault
        // To avoid rounding issues, we substract one wei to the amount joined
        daiJoin.join(cdpManager.urns(_cdpId), _debtAmount.sub(1));
    }

    function drawAndExitDebt(
        BaseWallet _wallet,
        uint256 _cdpId,
        uint256 _debtAmount,
        uint256 _collateralAmount,
        bytes32 _ilk
    )
        internal
    {
        // Get the accumulated rate for the collateral type
        (, uint rate,,,) = vat.ilks(_ilk);
        // Express the debt in the RAD units used internally by the vat
        uint daiDebtInRad = _debtAmount.mul(RAY);
        // Lock the collateral and draw the debt. To avoid rounding issues we add an extra wei of debt
        cdpManager.frob(_cdpId, toInt(_collateralAmount), toInt(daiDebtInRad.div(rate) + 1));
        // Transfer the (internal) DAI debt from the cdp's urn to the module.
        cdpManager.move(_cdpId, address(this), daiDebtInRad);
        // Mint the DAI token and exit it to the user's wallet
        daiJoin.exit(address(_wallet), _debtAmount);
    }

    function updateStabilityFee(
        uint256 _cdpId
    )
        internal
    {
        jug.drip(cdpManager.ilks(_cdpId));
    }

    function debt(
        uint256 _cdpId
    )
        internal
        view
        returns (uint256 _fullRepayment, uint256 _maxNonFullRepayment)
    {
        bytes32 ilk = cdpManager.ilks(_cdpId);
        (, uint256 art) = vat.urns(ilk, cdpManager.urns(_cdpId));
        if (art > 0) {
            (, uint rate,,, uint dust) = vat.ilks(ilk);
            _maxNonFullRepayment = art.mul(rate).sub(dust).div(RAY);
            _fullRepayment = art.mul(rate).div(RAY)
                .add(1) // the amount approved is 1 wei more than the amount repaid, to avoid rounding issues
                .add(art-art.mul(rate).div(RAY).mul(RAY).div(rate)); // adding 1 extra wei if further rounding issues are expected
        }
    }

    function collateral(
        uint256 _cdpId
    )
        internal
        view
        returns (uint256 _collateralAmount)
    {
        (_collateralAmount,) = vat.urns(cdpManager.ilks(_cdpId), cdpManager.urns(_cdpId));
    }

    function verifyValidRepayment(
        uint256 _cdpId,
        uint256 _debtAmount
    )
        internal
        view
    {
        (uint256 fullRepayment, uint256 maxRepayment) = debt(_cdpId);
        require(_debtAmount <= maxRepayment || _debtAmount == fullRepayment, "MV2: repay less or full");
    }

     /**
     * @dev Lets the owner of a wallet open a new vault. The owner must have enough collateral
     * in their wallet.
     * @param _wallet The target wallet
     * @param _collateral The token to use as collateral in the vault.
     * @param _collateralAmount The amount of collateral to lock in the vault.
     * @param _debtAmount The amount of DAI to draw from the vault
     * @return The id of the created vault.
     */
    // solium-disable-next-line security/no-assign-params
    function openVault(
        BaseWallet _wallet,
        address _collateral,
        uint256 _collateralAmount,
        uint256 _debtAmount
    )
        internal
        returns (uint256 _cdpId)
    {
        // Continue with WETH as collateral instead of ETH if needed
        if (_collateral == ETH_TOKEN_ADDRESS) {
            _collateral = address(wethToken);
        }
        // Get the ilk for the collateral
        bytes32 ilk = makerRegistry.getIlk(_collateral);
        // Open a vault if there isn't already one for the collateral type (the vault owner will effectively be the module)
        _cdpId = uint256(loanIds[address(_wallet)][ilk]);
        if (_cdpId == 0) {
            _cdpId = cdpManager.open(ilk, address(this));
            // Mark the vault as belonging to the wallet
            loanIds[address(_wallet)][ilk] = bytes32(_cdpId);
        }
        // Move the collateral from the wallet to the vat
        joinCollateral(_wallet, _cdpId, _collateralAmount, ilk);
        // Draw the debt and exit it to the wallet
        if (_debtAmount > 0) {
            drawAndExitDebt(_wallet, _cdpId, _debtAmount, _collateralAmount, ilk);
        }
    }

    /**
     * @dev Lets the owner of a vault add more collateral to their vault. The owner must have enough of the
     * collateral token in their wallet.
     * @param _wallet The target wallet
     * @param _cdpId The id of the vault.
     * @param _collateralAmount The amount of collateral to add to the vault.
     */
    function addCollateral(
        BaseWallet _wallet,
        uint256 _cdpId,
        uint256 _collateralAmount
    )
        internal
    {
        // Move the collateral from the wallet to the vat
        joinCollateral(_wallet, _cdpId, _collateralAmount, cdpManager.ilks(_cdpId));
        // Lock the collateral
        cdpManager.frob(_cdpId, toInt(_collateralAmount), 0);
    }

    /**
     * @dev Lets the owner of a vault remove some collateral from their vault
     * @param _wallet The target wallet
     * @param _cdpId The id of the vault.
     * @param _collateralAmount The amount of collateral to remove from the vault.
     */
    function removeCollateral(
        BaseWallet _wallet,
        uint256 _cdpId,
        uint256 _collateralAmount
    )
        internal
    {
        // Unlock the collateral
        cdpManager.frob(_cdpId, -toInt(_collateralAmount), 0);
        // Transfer the (internal) collateral from the cdp's urn to the module.
        cdpManager.flux(_cdpId, address(this), _collateralAmount);
        // Get the adapter for the collateral
        (JoinLike gemJoin,) = makerRegistry.getCollateral(cdpManager.ilks(_cdpId));
        // Exit the collateral from the adapter.
        gemJoin.exit(address(_wallet), _collateralAmount);
        // Convert WETH to ETH if needed
        if (gemJoin == wethJoin) {
            invokeWallet(address(_wallet), address(wethToken), 0, abi.encodeWithSignature("withdraw(uint256)", _collateralAmount));
        }
    }

    /**
     * @dev Lets the owner of a vault draw more DAI from their vault.
     * @param _wallet The target wallet
     * @param _cdpId The id of the vault.
     * @param _amount The amount of additional DAI to draw from the vault.
     */
    function addDebt(
        BaseWallet _wallet,
        uint256 _cdpId,
        uint256 _amount
    )
        internal
    {
        // Draw and exit the debt to the wallet
        drawAndExitDebt(_wallet, _cdpId, _amount, 0, cdpManager.ilks(_cdpId));
    }

    /**
     * @dev Lets the owner of a vault partially repay their debt. The repayment is made up of
     * the outstanding DAI debt plus the DAI stability fee.
     * The method will use the user's DAI tokens in priority and will, if needed, convert the required
     * amount of ETH to cover for any missing DAI tokens.
     * @param _wallet The target wallet
     * @param _cdpId The id of the vault.
     * @param _amount The amount of DAI debt to repay.
     */
    function removeDebt(
        BaseWallet _wallet,
        uint256 _cdpId,
        uint256 _amount
    )
        internal
    {
        verifyValidRepayment(_cdpId, _amount);
        // Convert some ETH into DAI with Uniswap if necessary
        buyTokens(_wallet, daiToken, _amount, daiUniswap);
        // Move the DAI from the wallet to the vat.
        joinDebt(_wallet, _cdpId, _amount);
        // Get the accumulated rate for the collateral type
        (, uint rate,,,) = vat.ilks(cdpManager.ilks(_cdpId));
        // Repay the debt. To avoid rounding issues we reduce the repayment by one wei
        cdpManager.frob(_cdpId, 0, -toInt(_amount.sub(1).mul(RAY).div(rate)));
    }

    /**
     * @dev Lets the owner of a vault close their vault. The method will:
     * 1) repay all debt and fee
     * 2) free all collateral
     * @param _wallet The target wallet
     * @param _cdpId The id of the CDP.
     */
    function closeVault(
        BaseWallet _wallet,
        uint256 _cdpId
    )
        internal
    {
        (uint256 fullRepayment,) = debt(_cdpId);
        // Repay the debt
        if (fullRepayment > 0) {
            removeDebt(_wallet, _cdpId, fullRepayment);
        }
        // Remove the collateral
        uint256 ink = collateral(_cdpId);
        if (ink > 0) {
            removeCollateral(_wallet, _cdpId, ink);
        }
    }

}