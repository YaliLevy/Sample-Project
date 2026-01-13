"""
Main entry point for WhatsApp Real Estate Assistant Bot.

This script:
1. Initializes the database
2. Starts ngrok tunnel (in development)
3. Starts the Flask webhook server
"""
import os
import sys
import logging
from config import settings

# Fix Windows console encoding for Unicode characters
if sys.platform == 'win32':
    try:
        # Set console output to UTF-8
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # For older Python versions, use environment variable
        os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_database():
    """Initialize database (create tables if they don't exist)."""
    from database.init_db import init_database

    logger.info("Initializing database...")

    try:
        # Create tables (doesn't recreate if they exist)
        # Set seed=True to add Hebrew test data on first run
        init_database(seed=True)
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}", exc_info=True)
        return False


def start_development_server():
    """Start development server with ngrok."""
    from ngrok_setup import start_ngrok
    import subprocess
    import time

    logger.info("Starting development environment...")

    # Start ngrok in background
    print("\n" + "="*70)
    print("🚀 Starting Development Server")
    print("="*70)

    try:
        # Start ngrok and get webhook URL
        webhook_url = start_ngrok(port=5000)

        # Wait a moment
        time.sleep(2)

        # Start Flask server
        print("\n" + "="*70)
        print("🌐 Starting Flask Server...")
        print("="*70)

        # Import and run Flask app
        from bot.twilio_handler import app
        app.run(
            debug=settings.FLASK_DEBUG,
            port=5000,
            host='0.0.0.0',
            use_reloader=False  # Prevent double startup with ngrok
        )

    except KeyboardInterrupt:
        print("\n\nShutting down...")
        from ngrok_setup import stop_ngrok
        stop_ngrok()
        print("Goodbye! 👋")
        sys.exit(0)


def start_production_server():
    """Start production server (without ngrok)."""
    logger.info("Starting production server...")

    print("\n" + "="*70)
    print("🚀 Starting Production Server")
    print("="*70)
    print(f"\n⚠️  Make sure your webhook is configured in Twilio!")
    print(f"Webhook URL: https://your-domain.com/webhook")
    print("="*70 + "\n")

    from bot.twilio_handler import app
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=False
    )


def main():
    """Main entry point."""
    print("""
    ╔══════════════════════════════════════════════════════════════════╗
    ║                                                                  ║
    ║          🏠 WhatsApp Real Estate Assistant Bot 🏠                ║
    ║                                                                  ║
    ║              Built with CrewAI + Twilio + Flask                  ║
    ║                                                                  ║
    ╚══════════════════════════════════════════════════════════════════╝
    """)

    # Step 1: Initialize database
    print("\n[1/3] Initializing database...")
    if not initialize_database():
        logger.error("Failed to initialize database. Exiting.")
        sys.exit(1)

    # Step 2: Validate configuration
    print("\n[2/3] Validating configuration...")
    try:
        settings.validate_config()
        logger.info("Configuration validated successfully")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        print(f"\n❌ Configuration Error: {e}")
        print("\nPlease create a .env file based on .env.example")
        sys.exit(1)

    # Step 3: Start server
    print("\n[3/3] Starting server...")

    if settings.FLASK_ENV == 'development':
        start_development_server()
    else:
        start_production_server()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        print(f"\n❌ Fatal Error: {e}")
        sys.exit(1)
