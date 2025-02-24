import './App.css'
import '@rainbow-me/rainbowkit/styles.css';
import Pop3D from './components/Pop3D/Pop3D';
import BribeUI from './components/BribeUI/BribeUI';
import HowDoesThisWork from './components/HowDoesThisWork/HowDoesThisWork';
import Modal from 'react-modal';
import React, { useState } from 'react';
import toast, { Toaster } from 'react-hot-toast';
import { wagmiConfig } from './config';

Modal.setAppElement('#root');

import {
  ConnectButton,
  getDefaultConfig,
  RainbowKitProvider,
} from '@rainbow-me/rainbowkit';
import { WagmiProvider, useAccount, useContractRead } from 'wagmi';
import {
  sonic,
} from 'wagmi/chains';
import {
  QueryClientProvider,
  QueryClient,
} from "@tanstack/react-query";

// Minimal ERC20 ABI
const ERC20_ABI = [
  'function balanceOf(address owner) view returns (uint256)',
  'function decimals() view returns (uint8)', // optional, if you want to format units
];


const tokenAddresses = {
  usdce: '0x29219dd400f2Bf60E5a23d13Be72B486D4038894',
  beets: '0x2D0E0814E62D80056181F5cd932274405966e4f0',
  shadow: '0x3333b97138D4b086720b5aE8A7844b1345a33333',
  xrlc: '0xf2968631D02330Dc5E420373f083b7B4F8B24E17'
};

const modalCustomStyles = {
  content: {
    top: '50%',
    left: '50%',
    right: 'auto',
    bottom: 'auto',
    marginRight: '-50%',
    transform: 'translate(-50%, -50%)',
    padding: '20px',
    borderRadius: '8px',
    transition: 'opacity 300ms ease-in-out',
  },
  overlay: {
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    transition: 'opacity 300ms ease-in-out',
  },
};

const queryClient = new QueryClient();
const App = () => {
  const [explainerModalIsOpen, setExplainerModalIsOpen] = useState(false);
  const openExplainerModal = () => setExplainerModalIsOpen(true);
  const closeExplainerModal = () => setExplainerModalIsOpen(false);
  return (
    <WagmiProvider config={wagmiConfig}>
      <QueryClientProvider client={queryClient}>
        <RainbowKitProvider>
          <div className="page ml-5 flex flex-col align-middle justify-center" style={{ alignItems: "center" }} id="learn-more">
            <h1 className="ghost-text atkinson-hyperlegible-700 pop3d mb-5 text-center">
              💲tairot.bribes💲
            </h1>
            <Pop3D action='back-to-tairot-agent'>Go back to tarot.agent page</Pop3D>
            <Pop3D action='open-contract'>Bribes Contract Address</Pop3D>
            <HowDoesThisWork action={openExplainerModal}>How does this work?</HowDoesThisWork>

            <div style={{ margin: "0 auto", marginTop: "1em" }}>
              <ConnectButton style={{ margin: "0 auto" }} />
            </div>
            <div style={{
              width: '100%',
              display: 'flex',
              flexDirection: 'column',
              alignContent: 'center',
              justifyContent: 'center',
              alignItems: 'center',
            }}>
              <BribeUI />
            </div>
          </div>


          <Modal
            isOpen={explainerModalIsOpen}
            onRequestClose={closeExplainerModal}
            contentLabel="Example Modal"
            style={modalCustomStyles}
            closeTimeoutMS={300} // Match this with your transition duration
          >
            <h1 className="cool-text atkinson-hyperlegible-700 pop3d mb-5 text-center text-2xl">
              How does this work?
            </h1>
            <div className='atkinson-hyperlegible-700 ml-5'>
              This is tarot.bribes, the bribes page for tairot.agent. 🔮<br />
              You can use this page to bribe the agent influence its readings. <br />
              Ask for a reading on Telegram or view the public readings on X. <br />
              The more bribes you send, the more swayed the reading will be.
            </div>
            <button className="cool-text w-full mt-5" onClick={closeExplainerModal}>Got it!</button>
          </Modal>
          <Toaster />
        </RainbowKitProvider>
      </QueryClientProvider>
    </WagmiProvider >
  );
};

export default App
