import yaml
import os
from dotenv import load_dotenv

def load_config(config_path='config.yaml'):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_env():
    load_dotenv()
    return {
        'TELEGRAM_BOT_TOKEN': os.getenv('TELEGRAM_BOT_TOKEN'),
        'TELEGRAM_CHAT_ID': os.getenv('TELEGRAM_CHAT_ID'),
        'DATABASE_URL': os.getenv('DATABASE_URL', 'sqlite:///crypto_signals.db')
    }
