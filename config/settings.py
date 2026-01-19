"""
Configuration settings loaded from environment variables.
"""
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

# OpenAI Configuration
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = 'gpt-4o'  # Using GPT-4o for best Hebrew support

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///storage/database.db')

# Supabase Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')
SUPABASE_STORAGE_BUCKET = os.getenv('SUPABASE_STORAGE_BUCKET', 'property-photos')

# Flask Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# ngrok Configuration
NGROK_AUTH_TOKEN = os.getenv('NGROK_AUTH_TOKEN')

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Project Paths
PROJECT_ROOT = Path(__file__).parent.parent
STORAGE_PATH = PROJECT_ROOT / 'storage'
PHOTOS_PATH = STORAGE_PATH / 'photos'

# Ensure storage directories exist
STORAGE_PATH.mkdir(exist_ok=True)
PHOTOS_PATH.mkdir(exist_ok=True)

# Validate critical configuration
def validate_config():
    """Validate that critical configuration is set."""
    missing = []

    if not TWILIO_ACCOUNT_SID:
        missing.append('TWILIO_ACCOUNT_SID')
    if not TWILIO_AUTH_TOKEN:
        missing.append('TWILIO_AUTH_TOKEN')
    if not OPENAI_API_KEY:
        missing.append('OPENAI_API_KEY')

    # Supabase is optional - warn if missing but don't fail
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Warning: Supabase credentials not set. Photos will be stored locally.")

    if missing:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing)}\n"
            f"Please create a .env file based on .env.example"
        )

# Run validation when module is imported (can be disabled for testing)
if os.getenv('SKIP_CONFIG_VALIDATION') != 'true':
    try:
        validate_config()
    except ValueError as e:
        print(f"Warning: {e}")
