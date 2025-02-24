// config.js
import { getDefaultConfig } from '@rainbow-me/rainbowkit';
import { sonic } from 'wagmi/chains';

export const wagmiConfig = getDefaultConfig({
    appName: 'tairot-bribes',
    projectId: '704283145ec09b6a2e3cd74e02adff41',
    chains: [sonic],
    ssr: true, // If your dApp uses server side rendering (SSR)
});
