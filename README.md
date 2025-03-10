tAIrot.agent - The Sonic Chain Divination AI

Overview:
tAIrot.agent is an autonomous AI oracle that combines mystical divination with real-time blockchain data from the Sonic chain. Designed for the Build the Future of DeFAI Hackathon, it uniquely blends AI-driven market predictions with a bribe mechanism that lets users influence outcomes by staking tokens.

Key Features:
- Real-Time Data: Continuously monitors the Sonic blockchain and integrates data from sources like Coingecko and DefiLlama.
- AI Divination: Uses ChatGPT to generate market prophecies, which are then turned into symbolic visuals via DALL·E-2.
- Bribe Mechanism: Allows users to stake ERC-20 tokens in a transparent, renounced smart contract to subtly influence divination results.
- Multi-Platform Interaction: Operates on Telegram (using commands like "/tarot"), posts spontaneous updates on X (Twitter), and offers dedicated web interfaces.

Architecture:
- Smart Contracts: Developed in Solidity (using Hardhat) to manage the bribe system.
- Frontend: Two websites—one for the divination experience (built with Svelte) and one for interacting with the bribe system (built with React/Vite).
- Backend: A Node.js API handles user requests and integration with external services, while a Python-based ZerePy agent orchestrates blockchain interactions, social media actions, and AI processes.

Installation & Setup:
1. Clone the repository.
2. Set up and test smart contracts using Hardhat.
3. Install dependencies and run the frontend applications.
4. Start the Node.js API and the Python ZerePy agent.

Usage:
- Send "/tarot" via Telegram to trigger a divination reading.
- Follow tAIrot.agent on X (Twitter) for automatic market updates.
- Use the web interface to participate in the bribe mechanism.

Contact:
Email: info@stomaco.studio
Telegram: https://t.me/+z_Qbj70f-khkYzZk
Xwitter: https://x.com/TAROT_LORD
GitHub: https://github.com/urielromeo/tairot.agent

Join us in redefining the future of DeFAI on Sonic!
