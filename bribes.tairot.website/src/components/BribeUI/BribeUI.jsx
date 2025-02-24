import * as React from 'react';
import Pop3D from '../../components/Pop3D/Pop3D';
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Slider from '@mui/material/Slider';
import TokenBalances from '../TokenBalances/TokenBalances';
import { writeContract } from '@wagmi/core'
import { useAccount, useContractRead, useWriteContract } from 'wagmi';
import toast, { Toaster } from 'react-hot-toast';
import { wagmiConfig } from '../../config';
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
    xrlc: '0xf2968631D02330Dc5E420373f083b7B4F8B24E17'
};

export default function BasicSelect() {
    const [coin, setCoin] = React.useState('BEETS');
    const [sliderValue, setSliderValue] = React.useState(0);
    const [isDonating, setIsDonating] = React.useState(false);

    const handleChange = (event) => {
        setCoin(event.target.value);
        setSliderValue(0);
    };

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

    const {
        data: xrlcBalance,
        isError: isErrorXRLC,
        error: errorXRLC,
        isLoading: isLoadingXRLC,
    } = useContractRead({
        address: tokenAddresses.xrlc,
        abi: ERC20_ABI,
        functionName: 'balanceOf',
        args: [address],
        enabled: Boolean(address),
        watch: false,
    });

    // const { writeContract } = useWriteContract();

    const tokenConfig = {
        usdce: {
            name: '$USDC.e',
            address: tokenAddresses.usdce, decimals: 6,
            balance: usdceBalance,
        },
        beets: {
            name: '$BEETS',
            address: tokenAddresses.beets, decimals: 18,
            balance: beetsBalance,
        },
        shadow: {
            name: '$SHADOW',
            address: tokenAddresses.shadow, decimals: 18,
            balance: shadowBalance,
        },
        xrlc: {
            name: '$XRLC',
            address: tokenAddresses.xrlc, decimals: 18,
            balance: xrlcBalance,
        }
    };

    const awaitDonation = async (tokenKey) => {
        toast.promise(handleDonate(tokenKey), {
            loading: 'Sending donation...',
            success: 'Donation sent!',
            error: '',
        }, {
            duration: 4000,
            position: 'top-center',

            // Styling
            style: {},
            className: '',

            // Custom Icon
            icon: '💸',

            // Change colors of success/error/loading icon
            iconTheme: {
                primary: '#000',
                secondary: '#fff',
            },

            // Aria
            ariaProps: {
                role: 'status',
                'aria-live': 'polite',
            },

            // Additional Configuration
            removeDelay: 1000,
        });
    };

    const handleDonate = async (tokenKey) => {
        try {
            setIsDonating(true);
            const token = tokenConfig[tokenKey];
            const amount = ethers.parseUnits('1', token.decimals);
            const recipientAddress = "0x2c4a44a1a45e059b685fe49ee63023d9c7f770cf"; // Replace with actual recipient address

            // Get the current balance first
            const rawBalance = token.balance;
            console.log('rawBalance', rawBalance);
            const floatBalance = Number(ethers.formatUnits(rawBalance, token.decimals));
            const balance = ethers.formatUnits(rawBalance, token.decimals);

            // Check if user has enough balance
            if (rawBalance < amount) {
                toast.error('You don\'t own enough ' + token.name + '');
                throw new Error('Insufficient balance');
            } else {
                console.log('Sufficient balance', floatBalance);
            }
            const result = await writeContract(wagmiConfig, {
                abi: ERC20_ABI,
                address: token.address,
                functionName: 'transfer',
                args: [
                    recipientAddress,
                    amount,
                ]
            })
            console.log('Transaction submitted:', result);
            if (result) {
                // open in etherscan
                const etherscanUrl = `https://sonicscan.org/tx/${result}`;
                toast(
                    <div>
                        ✨ Done! {' '}
                        <a
                            href={etherscanUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ color: 'blue', textDecoration: 'underline' }}
                        >
                            view transaction on SonicScan
                        </a>
                        💸
                    </div>,
                    {
                        duration: 60000, // Toast stays for 1 minute
                        position: 'top-center',
                    }
                );
                // toast.success(`Transaction hash: ${result.hash}`);
            }
        } catch (error) {
            toast.error('Something went wrong... 🔮');
            throw new Error(error);
            console.error('Error donating:', error);
        } finally {
            setIsDonating(false);
        }
    };

    // Optionally, you might want to conditionally render if the wallet isn't connected.
    if (!address) {
        return <div>Please connect your wallet to view token balances.</div>;
    }
    return (
        <>
            <div
                onClick={!isDonating ? () => awaitDonation('beets') : undefined}
                style={{ pointerEvents: isDonating ? 'none' : 'auto', opacity: isDonating ? 0.5 : 1, width: "100%", margin: "0 auto", display: "flex", justifyContent: "center" }}
            >
                <Pop3D className="w-100">Donate 1 $BEETS</Pop3D>
            </div>
            <div
                onClick={!isDonating ? () => awaitDonation('shadow') : undefined}
                style={{ pointerEvents: isDonating ? 'none' : 'auto', opacity: isDonating ? 0.5 : 1, width: "100%", margin: "0 auto", display: "flex", justifyContent: "center" }}
            >
                <Pop3D className="w-100">Donate 1 $SHADOW</Pop3D>
            </div>
            <div
                onClick={!isDonating ? () => awaitDonation('usdce') : undefined}
                style={{ pointerEvents: isDonating ? 'none' : 'auto', opacity: isDonating ? 0.5 : 1, width: "100%", margin: "0 auto", display: "flex", justifyContent: "center" }}
            >
                <Pop3D className="w-100">Donate 1 $USDC.e</Pop3D>
            </div>
            <div
                onClick={!isDonating ? () => awaitDonation('xrlc') : undefined}
                style={{ pointerEvents: isDonating ? 'none' : 'auto', opacity: isDonating ? 0.5 : 1, width: "100%", margin: "0 auto", display: "flex", justifyContent: "center" }}
            >
                <Pop3D className="w-100">Donate 1 $XRLC</Pop3D>
            </div>
        </>
    );
}