# vc-notification-bot

## Requirements

Python 3.10

## Setup

### Discord Developer Portal
- These intents should be enabled from "Settings -> Bot -> Privileged Gateway Intents":
  - Presence intent
  - Server members intent
  - Message content intent

### Python

#### Installing Python 3.10 with pyenv

One way to manage your local Python version is using [pyenv](https://github.com/pyenv/pyenv). Please follow the installation guide for it.

```
# Install Python 3.10.x
pyenv install 3.10.19

# Set Python 3.10 for this project (this creates a .python-version file in the project directory)
pyenv local 3.10.19

# Check Python version
python --version
```

#### Installing dependencies in a virtual environment

It is recommended to use `venv` for creating a virtual environment in the project directory.

```
# Create the virtual env
python -m venv venv

# Activate the virtual env
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Usage
1. Fill the sample config with your bot token and guild id (guild id is an integer remove the quotes)
2. Rename it to config.json
3. run "pip install -r requirements.txt" to install the required packages
3. run "python src/main.py" to run the bot