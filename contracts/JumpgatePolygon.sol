// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.8.13;

import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/token/ERC20/ERC20.sol";
import "OpenZeppelin/openzeppelin-contracts@4.5.0/contracts/token/ERC20/utils/SafeERC20.sol";

import "./AssetRecoverer.sol";
import "./NormalizedAmounts.sol";
import "../interfaces/IPolygonBridge.sol";

/// @title Jumpgate
/// @author mymphe
/// @notice Transfer an ERC20 token using a Wormhole token bridge with pre-determined parameters
/// @dev `IWormholeTokenBridge` and the logic in `_callBridgeTransfer` are specific to Wormhole Token Bridge
contract JumpgatePolygon is AssetRecoverer {
    using NormalizedAmounts for uint256;
    using SafeERC20 for IERC20;

    event JumpgateCreated(
        address indexed _jumpgate,
        address indexed _token,
        address indexed _bridge,
        address _recipient
    );

    event TokensBridged(
        address indexed _token,
        address indexed _bridge,
        address _recipient,
        uint256 _amount
    );

    /// ERC20 token to be bridged
    IERC20 public immutable token;

    /// Wormhole token bridge
    IPolygonBridge public immutable bridge;

    /// recipient address on the target chain
    address public immutable recipient;

    constructor(
        address _owner,
        address _token,
        address _bridge,
        address _recipient
    ) {
        transferOwnership(_owner);

        token = IERC20(_token);
        bridge = IPolygonBridge(_bridge);
        recipient = _recipient;

        emit JumpgateCreated(
            address(this),
            _token,
            _bridge,
            _recipient
        );
    }

    /// @notice transfer all of the tokens on this contract's balance to the cross-chain recipient
    /// @dev transfer amount is normalized due to bridging decimal shift which sometimes truncates decimals
    function bridgeTokens() external {
        uint256 amount = token.balanceOf(address(this));
        uint8 decimals = getDecimals();
        uint256 normalizedAmount = amount.normalize(decimals);
        require(normalizedAmount > 0, "Amount too small for bridging!");
        uint256 denormalizedAmount = normalizedAmount.denormalize(decimals);

        bytes32 tokenType = bridge.tokenToType(address(token));
        address tokenPredicate = bridge.typeToPredicate(tokenType);
        token.safeApprove(tokenPredicate, denormalizedAmount);
        _callBridgeTransfer(denormalizedAmount);

        emit TokensBridged(
            address(token),
            address(bridge),
            recipient,
            denormalizedAmount
        );
    }

    /// @notice calls the transfer method on the bridge
    /// @dev implements the actual logic of the bridge transfer
    /// @param _amount amount of tokens to transfer
    function _callBridgeTransfer(uint256 _amount)
    private
    {
        bridge.depositFor(
            recipient,
            address(token),
            abi.encode(_amount)
        );
    }

    /// @notice get number of token decimals for normalization
    /// @dev using low-level `staticcall` because OpenZeppelin IERC20 doesn't include `decimals()`
    /// @return decimals number of token decimals
    function getDecimals() internal view returns (uint8 decimals) {
        (, bytes memory queriedDecimals) = address(token).staticcall(
            abi.encodeWithSignature("decimals()")
        );
        decimals = abi.decode(queriedDecimals, (uint8));
    }
}
