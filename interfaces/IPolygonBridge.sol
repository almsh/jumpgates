//SPDX-License-Identifier: Unlicense
pragma solidity ^0.8.0;

interface IPolygonBridge {
    function typeToPredicate(bytes32 tokenType) external returns (address);
    function tokenToType(address token) external returns (bytes32);

    function depositFor(
        address user,
        address rootToken,
        bytes calldata depositData
    ) external;
}
