"""
Flask webhook handler for Twilio WhatsApp messages.
Async version - processes messages in background to avoid Twilio timeout.
"""
from flask import Flask, request, jsonify
from twilio.rest import Client
from crews.orchestrator import CrewAIOrchestrator
from bot.conversation_state import ConversationStateManager
from config import settings
import logging
import threading

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY

# Initialize orchestrator and state manager
logger.info("Initializing CrewAI Orchestrator...")
orchestrator = CrewAIOrchestrator()
state_manager = ConversationStateManager()
logger.info("Initialization complete")

# Initialize Twilio client for sending messages directly
twilio_client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)


def send_whatsapp_message(to_number: str, message: str):
    """
    Send WhatsApp message directly via Twilio API.
    Handles message splitting for long messages.
    """
    try:
        # Ensure whatsapp: prefix
        if not to_number.startswith('whatsapp:'):
            to_number = f'whatsapp:{to_number}'

        # Split long messages (WhatsApp limit is 1600 chars)
        if len(message) > 1600:
            chunks = [message[i:i+1600] for i in range(0, len(message), 1600)]
            logger.info(f"Splitting message into {len(chunks)} parts")
        else:
            chunks = [message]

        # Send each chunk
        for chunk in chunks:
            twilio_client.messages.create(
                from_=settings.TWILIO_WHATSAPP_NUMBER,
                to=to_number,
                body=chunk
            )

        logger.info(f"Successfully sent message to {to_number}")
        return True

    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}", exc_info=True)
        return False


def process_message_async(message: str, from_number: str, media_urls: list):
    """
    Process message in background thread and send response via Twilio API.
    """
    try:
        logger.info(f"[ASYNC] Starting processing for {from_number}")

        # Process through CrewAI orchestrator
        response_text = orchestrator.process_message(
            message=message,
            phone_number=from_number,
            media_urls=media_urls
        )

        logger.info(f"[ASYNC] Generated response: {response_text[:100]}...")

        # Save bot response to conversation history
        state_manager.add_message(from_number, 'assistant', response_text)

        # Send response via Twilio API
        success = send_whatsapp_message(from_number, response_text)

        if success:
            logger.info(f"[ASYNC] Successfully sent response to {from_number}")
        else:
            logger.error(f"[ASYNC] Failed to send response to {from_number}")

    except Exception as e:
        logger.error(f"[ASYNC] Error processing message: {e}", exc_info=True)

        # Send error message to user
        error_msg = "מצטער, נתקלתי בבעיה טכנית. נסה שוב בעוד רגע."
        send_whatsapp_message(from_number, error_msg)


@app.route('/webhook', methods=['POST'])
def whatsapp_webhook():
    """
    Main webhook endpoint for Twilio WhatsApp messages.
    Returns immediately and processes in background.
    """
    try:
        # Extract Twilio parameters
        from_number = request.form.get('From', '').replace('whatsapp:', '')
        message_body = request.form.get('Body', '')
        num_media = int(request.form.get('NumMedia', 0))

        # Collect media URLs
        media_urls = []
        for i in range(num_media):
            media_url = request.form.get(f'MediaUrl{i}')
            if media_url:
                media_urls.append(media_url)

        logger.info(f"Received message from {from_number}: {message_body[:50]}...")
        logger.info(f"Media count: {num_media}")

        # Validate message - must have text content
        if not message_body or message_body.strip() == "":
            logger.warning(f"Empty message received (media count: {num_media}), ignoring")
            return "", 200

        # Save incoming message to conversation history
        state_manager.add_message(from_number, 'user', message_body)

        # Start background processing
        thread = threading.Thread(
            target=process_message_async,
            args=(message_body, from_number, media_urls)
        )
        thread.daemon = True
        thread.start()

        logger.info(f"Started background processing for {from_number}")

        # Return empty response immediately (no TwiML needed)
        # The actual response will be sent via Twilio API
        return "", 200

    except Exception as e:
        logger.error(f"Error in webhook: {e}", exc_info=True)
        return "", 200


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'WhatsApp Real Estate Bot',
        'version': '1.0.0'
    }), 200


@app.route('/', methods=['GET'])
def index():
    """Simple info page."""
    return """
    <html>
        <head>
            <title>WhatsApp Real Estate Bot</title>
            <meta charset="utf-8">
        </head>
        <body style="font-family: Arial; max-width: 600px; margin: 50px auto; direction: rtl;">
            <h1>בוט WhatsApp לניהול נדל"ן</h1>
            <p>הבוט פועל!</p>

            <h2>הגדרת Twilio Sandbox:</h2>
            <ol>
                <li>כנס ל: <a href="https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox" target="_blank">Twilio WhatsApp Sandbox</a></li>
                <li>הגדר "When a message comes in" ל-URL:</li>
                <code style="background: #f0f0f0; padding: 10px; display: block; margin: 10px 0;">
                    {WEBHOOK_URL}/webhook
                </code>
                <li>שמור את ההגדרות</li>
                <li>שלח הודעה למספר Sandbox עם קוד ה-join</li>
            </ol>

            <h2>דוגמאות לשימוש:</h2>
            <ul>
                <li>הוספת נכס: "דירה 3 חדרים בתל אביב דיזנגוף 102 5000 שקל להשכרה"</li>
                <li>הוספת לקוח: "לקוח חדש יניב מחפש 2-3 חדרים עד 6000 בת״א"</li>
                <li>חיפוש: "תראה לי נכסים בדיזנגוף"</li>
                <li>התאמות: "מה מתאים ליניב"</li>
            </ul>

            <p><small>Built with CrewAI + Twilio + Flask</small></p>
        </body>
    </html>
    """, 200


if __name__ == '__main__':
    # Development server
    port = 5000
    logger.info(f"Starting Flask development server on port {port}")
    logger.info(f"Environment: {settings.FLASK_ENV}")

    app.run(
        debug=settings.FLASK_DEBUG,
        port=port,
        host='0.0.0.0'
    )
