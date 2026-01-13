"""
WhatsApp messaging tools via Twilio API.
"""
from crewai.tools import BaseTool
from pydantic import BaseModel
from typing import Type, Optional, List
import logging
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

from tools.schemas import WhatsAppMessageInput
from config import settings

logger = logging.getLogger(__name__)


class WhatsAppMessageSender(BaseTool):
    """Tool for sending WhatsApp messages via Twilio."""
    name: str = "שליחת הודעת WhatsApp"
    description: str = "שולח הודעת טקסט ב-WhatsApp דרך Twilio. מקסימום 1600 תווים."
    args_schema: Type[BaseModel] = WhatsAppMessageInput

    def __init__(self):
        super().__init__()
        # Initialize Twilio client
        self.client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

    def _run(
        self,
        to_number: str,
        message: str,
        media_urls: Optional[List[str]] = None
    ) -> str:
        """
        Send WhatsApp message via Twilio.

        Args:
            to_number: Recipient phone number (format: whatsapp:+972...)
            message: Message text (max 1600 characters)
            media_urls: Optional list of media URLs to send

        Returns:
            Hebrew confirmation message with message SID
        """
        try:
            # Ensure whatsapp: prefix
            if not to_number.startswith('whatsapp:'):
                to_number = f'whatsapp:{to_number}'

            # Truncate message if too long
            if len(message) > 1600:
                logger.warning(f"Message too long ({len(message)} chars), truncating to 1600")
                message = message[:1597] + "..."

            # Send message
            logger.info(f"Sending WhatsApp message to {to_number}")

            message_params = {
                'from_': settings.TWILIO_WHATSAPP_NUMBER,
                'to': to_number,
                'body': message
            }

            # Add media if provided
            if media_urls:
                message_params['media_url'] = media_urls

            twilio_message = self.client.messages.create(**message_params)

            logger.info(f"Message sent successfully. SID: {twilio_message.sid}")

            return f"ההודעה נשלחה בהצלחה! Message ID: {twilio_message.sid}"

        except TwilioRestException as e:
            logger.error(f"Twilio error sending message: {e}", exc_info=True)
            return f"שגיאה בשליחת ההודעה: {e.msg}"
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}", exc_info=True)
            return f"שגיאה בשליחת ההודעה: {str(e)}"


class BulkWhatsAppSender(BaseTool):
    """Tool for sending messages to multiple recipients."""
    name: str = "שליחה לכמה נמענים"
    description: str = "שולח את אותה הודעה למספר נמענים ב-WhatsApp."

    class Input(BaseModel):
        to_numbers: List[str]
        message: str
        media_urls: Optional[List[str]] = None

    args_schema: Type[BaseModel] = Input

    def _run(
        self,
        to_numbers: List[str],
        message: str,
        media_urls: Optional[List[str]] = None
    ) -> str:
        """Send message to multiple recipients."""
        try:
            sender = WhatsAppMessageSender()
            results = []
            success_count = 0

            for number in to_numbers:
                result = sender._run(
                    to_number=number,
                    message=message,
                    media_urls=media_urls
                )

                if "נשלחה בהצלחה" in result:
                    success_count += 1
                    results.append(f"✓ {number}")
                else:
                    results.append(f"✗ {number}: {result}")

            summary = f"נשלחו {success_count} מתוך {len(to_numbers)} הודעות בהצלחה.\n\n"
            summary += "\n".join(results)

            return summary

        except Exception as e:
            logger.error(f"Error in bulk send: {e}", exc_info=True)
            return f"שגיאה בשליחה המרובה: {str(e)}"
