"""
ngrok setup helper for development.
Starts ngrok tunnel and prints webhook URL.
"""
import subprocess
import requests
import time
import sys
import os
from config import settings


def start_ngrok(port=5000):
    """
    Start ngrok tunnel on specified port.

    Args:
        port: Local port to tunnel (default: 5000)

    Returns:
        Public webhook URL
    """
    print(f"Starting ngrok tunnel on port {port}...")

    # Check if ngrok is installed
    try:
        subprocess.run(['ngrok', 'version'], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ ngrok is not installed!")
        print("\nInstall ngrok:")
        print("  Windows: choco install ngrok")
        print("  Mac: brew install ngrok")
        print("  Or download from: https://ngrok.com/download")
        sys.exit(1)

    # Set auth token if available
    if settings.NGROK_AUTH_TOKEN:
        print("Setting ngrok auth token...")
        subprocess.run(
            ['ngrok', 'config', 'add-authtoken', settings.NGROK_AUTH_TOKEN],
            capture_output=True
        )

    # Kill existing ngrok processes
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'ngrok.exe'], capture_output=True)
        else:  # Unix/Mac
            subprocess.run(['pkill', 'ngrok'], capture_output=True)
        time.sleep(1)
    except Exception:
        pass

    # Start ngrok
    print("Starting ngrok process...")
    ngrok_process = subprocess.Popen(
        ['ngrok', 'http', str(port)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    # Wait for ngrok to start
    print("Waiting for ngrok to initialize...")
    time.sleep(3)

    # Get public URL from ngrok API
    try:
        response = requests.get('http://localhost:4040/api/tunnels', timeout=5)
        response.raise_for_status()

        tunnels = response.json()['tunnels']

        if not tunnels:
            raise Exception("No tunnels found")

        # Get HTTPS URL
        public_url = None
        for tunnel in tunnels:
            if tunnel['proto'] == 'https':
                public_url = tunnel['public_url']
                break

        if not public_url:
            public_url = tunnels[0]['public_url']

        webhook_url = f"{public_url}/webhook"

        print("\n" + "="*70)
        print("✅ ngrok tunnel started successfully!")
        print("="*70)
        print(f"\n📍 Public URL: {public_url}")
        print(f"📍 Webhook URL: {webhook_url}")
        print(f"📍 ngrok Dashboard: http://localhost:4040")

        print("\n" + "="*70)
        print("🔧 Twilio Configuration:")
        print("="*70)
        print("\n1. Go to: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox")
        print("\n2. Set 'When a message comes in' to:")
        print(f"   {webhook_url}")
        print("\n3. Click 'Save'")
        print("\n4. Send your join code to the sandbox number")

        print("\n" + "="*70)
        print("📱 Testing:")
        print("="*70)
        print("\nSend these messages to test:")
        print('  • "שלום" - Greeting')
        print('  • "דירה 3 חדרים בתל אביב 5000 שקל להשכרה" - Add property')
        print('  • "לקוח חדש יניב מחפש 2 חדרים עד 6000" - Add client')

        print("\n" + "="*70)
        print("⚠️  Keep this terminal open while testing!")
        print("="*70)

        return public_url

    except requests.exceptions.RequestException as e:
        print(f"❌ Error getting ngrok URL: {e}")
        print("\nMake sure ngrok started successfully.")
        print("Check the ngrok dashboard at: http://localhost:4040")
        sys.exit(1)


def stop_ngrok():
    """Stop ngrok tunnel."""
    print("Stopping ngrok...")
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'ngrok.exe'])
        else:  # Unix/Mac
            subprocess.run(['pkill', 'ngrok'])
        print("✅ ngrok stopped")
    except Exception as e:
        print(f"Error stopping ngrok: {e}")


if __name__ == '__main__':
    try:
        start_ngrok()
        print("\nPress Ctrl+C to stop ngrok...")
        # Keep running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping ngrok...")
        stop_ngrok()
        print("Goodbye! 👋")
