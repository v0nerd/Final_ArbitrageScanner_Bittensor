<div align="center">

# **Bittensor Arbitrage Scanner**
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 

</div>

## Introduction
Arbitrage is a trading strategy that capitalizes on price discrepancies between similar financial instruments across different markets. As decentralized financial markets become increasingly complex, they not only offer abundant arbitrage opportunities but also present significant challenges due to high volatility, fluctuating transaction fees, and the necessity for real-time data processing. This subnet tackles these challenges by offering a decentralized arbitrage scanner that autonomously identifies profitable opportunities, complemented by AI-powered wallet analysis and search capabilities.

The primary goal of the subnet is to maximize these arbitrage opportunities for traders, enabling them to achieve substantial real-world profits, guaranteed by its realistically simulated environment and a robust incentive mechanism. Initially focusing on cryptocurrencies, the subnet plans to extend into traditional financial markets, including forex, options, and commodities, to broaden its utility and reach.

![alt text]([diagram-export-8-30-2024-10_32_16-AM.png](https://github.com/v0nerd/Final_ArbitrageScanner_Bittensor/blob/main/Assets/diagram-export-8-30-2024-10_32_16-AM.png))

## Key Features
### Offering Best Arbitrage Opportunities
The arbitrage subnet is a highly competitive arena where a realistic arbitrage environment is simulated. Here, only those who consistently secure substantial profits from high-return arbitrage opportunities will survive. These top performers contribute the best arbitrage opportunities and strategies, translating the subnet's value into real-world profits. Users can access top arbitrage opportunities directly from the subnet dashboard, where insights into how the best performers are capitalizing on these opportunities are showcased. This allows them to apply these successful strategies to their own trading activities as they see it.


### Wallet Search/Analysis
Miners of our subnet use AI to search and analyze wallets based on dozens to hundreds of criteria. This allows traders to benefit by understanding how professional traders operate and what sets them apart. By tracking all transactions and actions of these top traders, our users gain valuable insights into effective trading strategies.

### Providing Latest News as soon as possible
Staying ahead with the latest news is critical in the cryptocurrency realm. Our platform ensures that traders receive timely updates, giving them a strategic advantage by allowing them to act on information quicker than others. This feature supports dynamic decision-making in the fast-paced crypto market, helping traders leverage news for prompt and informed trading actions.


## Base Implementation
### Validator's Role
Validators are required to evaluate miners' performance by simulating their inputs for arbitrage opportunities and reward them based on the profits they made. Currently, only arbitrage opportunities from 100+ whitelisted exchanges are accepted; any opportunities from other sources are discarded.

- **Real-Time Simulation**: Using real-time data such as prices, fees, and transaction times to simulate the feasibility and profitability of the arbitrage opportunity.
- **Data Accumulation**: Recording and accumulating performance data such as timestamp, profit margins, and execution times for validated trades.
- **Reward Calculation**: Validators assess miner performance based on the profits gained from the arbitrage opportunities.

![alt text]([diagram-export-8-30-2024-12_41_56-PM-1-1.png](https://github.com/v0nerd/Final_ArbitrageScanner_Bittensor/blob/main/Assets/diagram-export-8-30-2024-12_41_56-PM-1-1.png))

### Miner's Role
Miners are responsible for finding the most profitable arbitrage opportunities and sending them to validators to earn higher incentives. To maximize their potential, miners are encouraged to continually enhance their strategies to identify and exploit the best opportunities effectively.

- **Data Collection**: Continuously scanning the market for price discrepancies between exchanges.
- **Opportunity Identification**: Detecting arbitrage opportunities by analyzing price differences while accounting for transaction costs and slippage.
- **Submission of Opportunities**: Sending arbitrage opportunities to validators for further real-time simulation and confirmation.


### Incentive Mechanism
Validators evaluate miners based on the profits generated from arbitrage opportunities submitted to them. Here is an overview of how it works in detail:
- Each day, miners' cash reserves are reset to a default value, and validators score their performance based on the profits earned by the end of that day. The subnet prioritizes top-performing miners, adjusting the incentive mechanism to be more exponential to reward these top performers more significantly.
- Miners' scores are calculated based on their performance over the last seven days. The impact of daily profits on the score diminishes exponentially over time, with more recent profits having a greater effect on the overall score.

## Execute

### Register Wallet

```
btcli s register --wallet.name <YOUR_WALLET> --subtensor.network test --netuid <YOUR_NET> --wallet.hotkey <YOUR_HOTKEY>
btcli st add --wallet.name george --subtensor.network test
btcli w new_coldkey --wallet.name <test_miner> --no_password
btcli w new_hotkey --wallet.name <test_miner> --wallet.hotkey <test_miner_hotkey>
```

### Run Miner or Validator
```
pip install -e .

sudo ufw allow 8092
sudo ufw allow 8091

pm2 start <YOUR_PATH>/Bittensor_Arbitrage/neurons/validator.py --interpreter <YOUR_PATH>/Bittensor_Arbitrage/subnet/bin/python3 --name test_validator -- --subtensor.network test --wallet.name <YOUR_WALLET> --wallet.hotkey <YOUR_WALLET> --netuid <YOUR_NET> --logging.debug --axon.port 8091

pm2 start <YOUR_PATH>/Bittensor_Arbitrage/neurons/miner.py --interpreter <YOUR_PATH>/Bittensor_Arbitrage/subnet/bin/python3 --name test_miner -- --subtensor.network test --wallet.name <test_miner> --wallet.hotkey <test_miner> --netuid <YOUR_NET> --logging.debug --axon.port 8092
```

## Roadmap
### Phase 1: Foundation
- Launch on testnet
- Make simulation environment more realistic
- Improve incentive mechanism
- Develop miner dashboard
- Launch on mainnet

### Phase 2: Expansion
- Develop a basic AI model to detect peak arbitrage times
- Introduce wallet searching and analysis features
- Build initial AI models for wallet search/analysis
- Integrate forex, options and other financial assets
- Implement Telegram and Reddit scanners
- Refine incentive mechanism

### Phase 3: Mass Adoption and Accessibility
- Improve models for arbitrage and wallet analysis
- Develop API for accessing prime arbitrage opportunities and wallet analytics
- Monetize API access to top miner insights
- Expand and integrate all arbitrage services


