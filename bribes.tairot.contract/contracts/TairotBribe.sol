// SPDX-License-Identifier: MIT
// Solidity Version: 0.8.0

// Import the Ownable and IERC20 interfaces from OpenZeppelin's GitHub
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import {IERC20} from "@openzeppelin/contracts/token/ERC20/IERC20.sol";

pragma solidity ^0.8.0;

contract TairotBribe is Ownable {
    // Allow the contract to receive ETH
    receive() external payable {}

    fallback() external payable {}

    constructor() Ownable(msg.sender) {}

    /// @notice Withdraw a specified amount of ETH from the contract.
    /// @param amount The amount of ETH (in wei) to withdraw.
    function withdrawETH(uint256 amount) external onlyOwner {
        require(address(this).balance >= amount, "Insufficient ETH balance");
        (bool sent, ) = msg.sender.call{value: amount}("");
        require(sent, "Failed to send Ether");
    }

    /// @notice Withdraw a specified amount of ERC20 tokens from the contract.
    /// @param tokenAddress The address of the ERC20 token.
    /// @param amount The amount of tokens to withdraw.
    function withdrawERC20(
        address tokenAddress,
        uint256 amount
    ) external onlyOwner {
        IERC20 token = IERC20(tokenAddress);
        require(
            token.balanceOf(address(this)) >= amount,
            "Insufficient token balance"
        );
        bool sent = token.transfer(msg.sender, amount);
        require(sent, "Token transfer failed");
    }
}
