import React, { useEffect } from 'react';
import { useAccount, useContractRead, useWriteContract } from 'wagmi';
import { ethers } from 'ethers';

// Minimal ERC20 ABI
const ERC20_ABI = [
    {
        "constant": true,
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_spender",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "approve",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_from",
                "type": "address"
            },
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transferFrom",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "name": "",
                "type": "uint8"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "name": "balance",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "name": "",
                "type": "string"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": false,
        "inputs": [
            {
                "name": "_to",
                "type": "address"
            },
            {
                "name": "_value",
                "type": "uint256"
            }
        ],
        "name": "transfer",
        "outputs": [
            {
                "name": "",
                "type": "bool"
            }
        ],
        "payable": false,
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "constant": true,
        "inputs": [
            {
                "name": "_owner",
                "type": "address"
            },
            {
                "name": "_spender",
                "type": "address"
            }
        ],
        "name": "allowance",
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
        "payable": false,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "payable": true,
        "stateMutability": "payable",
        "type": "fallback"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "owner",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "spender",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Approval",
        "type": "event"
    },
    {
        "anonymous": false,
        "inputs": [
            {
                "indexed": true,
                "name": "from",
                "type": "address"
            },
            {
                "indexed": true,
                "name": "to",
                "type": "address"
            },
            {
                "indexed": false,
                "name": "value",
                "type": "uint256"
            }
        ],
        "name": "Transfer",
        "type": "event"
    }
]
    ;

const tokenAddresses = {
    usdce: '0x29219dd400f2Bf60E5a23d13Be72B486D4038894',
    beets: '0x2D0E0814E62D80056181F5cd932274405966e4f0',
    shadow: '0x3333b97138d4b086720b5ae8a7844b1345a33333',
};

function TokenBalances() {
    const { address } = useAccount();

    const {
        data: usdceBalance,
        isError: isErrorUSDCE,
        error: errorUSDCE,
        isLoading: isLoadingUSDCE,
    } = useContractRead({
        address: tokenAddresses.usdce,
        abi: ERC20_ABI,
        functionName: 'balanceOf',
        args: [address],
        enabled: Boolean(address),
        watch: false,
    });

    const {
        data: beetsBalance,
        isError: isErrorBeets,
        error: errorBeets,
        isLoading: isLoadingBeets,
    } = useContractRead({
        address: tokenAddresses.beets,
        abi: ERC20_ABI,
        functionName: 'balanceOf',
        args: [address],
        enabled: Boolean(address),
        watch: false,
    });

    const {
        data: shadowBalance,
        isError: isErrorShadow,
        error: errorShadow,
        isLoading: isLoadingShadow,
    } = useContractRead({
        address: tokenAddresses.shadow,
        abi: ERC20_ABI,
        functionName: 'balanceOf',
        args: [address],
        enabled: Boolean(address),
        watch: false,
    });

    // Function to format the balance from the smallest unit to a human-readable string.
    const formatBalance = (balance, decimals = 18) => {
        console.log(balance);
        return balance ? ethers.formatUnits(balance, decimals) : '0';
    };

    // Optionally, you might want to conditionally render if the wallet isn't connected.
    if (!address) {
        return <div>Please connect your wallet to view token balances.</div>;
    }

    return (
        <div>
            <h2>Your Token Balances</h2>
            <p>USDCe: {formatBalance(usdceBalance, 6)}</p>
            <p>Beets: {formatBalance(beetsBalance, 18)}</p>
            <p>Shadow: {formatBalance(shadowBalance, 18)}</p>
        </div>
    );
}

export default TokenBalances;
