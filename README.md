# vc-notification-bot

## Requirements

Python 3.10

## Setup

### Discord Developer Portal
- These intents should be enabled from "Settings -> Bot -> Privileged Gateway Intents":
  - Presence intent
  - Server members intent
  - Message content intent

## Usage
1. Fill the sample config with your bot token and guild id (guild id is an integer remove the quotes)
2. Rename it to config.json
3. run "pip install -r requirements.txt" to install the required packages
3. run "python src/main.py" to run the bot