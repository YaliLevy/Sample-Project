"""
Conversation state management.
Tracks message history for each user.
"""
from database.models import Conversation
from database.connection import get_session
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ConversationStateManager:
    """Manages conversation history in database."""

    def add_message(self, phone_number: str, role: str, content: str):
        """
        Store a message in conversation history.

        Args:
            phone_number: User's phone number
            role: 'user' or 'assistant'
            content: Message content
        """
        try:
            with get_session() as session:
                conversation = Conversation(
                    phone_number=phone_number,
                    role=role,
                    content=content,
                    timestamp=datetime.utcnow()
                )
                session.add(conversation)

            logger.info(f"Saved message from {phone_number} (role: {role})")

        except Exception as e:
            logger.error(f"Error saving conversation: {e}", exc_info=True)

    def get_recent_history(self, phone_number: str, limit: int = 10):
        """
        Retrieve recent conversation history for a user.

        Args:
            phone_number: User's phone number
            limit: Maximum number of messages to retrieve

        Returns:
            List of Conversation objects (oldest first)
        """
        try:
            with get_session() as session:
                messages = session.query(Conversation)\
                    .filter_by(phone_number=phone_number)\
                    .order_by(Conversation.timestamp.desc())\
                    .limit(limit)\
                    .all()

                # Reverse to get oldest first
                return list(reversed(messages))

        except Exception as e:
            logger.error(f"Error retrieving history: {e}", exc_info=True)
            return []

    def clear_history(self, phone_number: str):
        """
        Clear conversation history for a user.

        Args:
            phone_number: User's phone number
        """
        try:
            with get_session() as session:
                session.query(Conversation)\
                    .filter_by(phone_number=phone_number)\
                    .delete()

            logger.info(f"Cleared history for {phone_number}")

        except Exception as e:
            logger.error(f"Error clearing history: {e}", exc_info=True)

    def get_conversation_count(self, phone_number: str) -> int:
        """
        Get total number of messages for a user.

        Args:
            phone_number: User's phone number

        Returns:
            Message count
        """
        try:
            with get_session() as session:
                count = session.query(Conversation)\
                    .filter_by(phone_number=phone_number)\
                    .count()
                return count

        except Exception as e:
            logger.error(f"Error counting messages: {e}", exc_info=True)
            return 0
