"""
Property Photo Agent - Handles property photos from WhatsApp.
"""
from crewai import Agent
from config.llm_config import get_gpt4o
from tools.media_tool import TwilioMediaDownloader, GetPropertyPhotosTool, BatchMediaDownloader


def create_property_photo_agent():
    """
    Create Property Photo Agent for handling media.

    This agent:
    - Downloads photos from Twilio WhatsApp
    - Associates photos with properties
    - Retrieves property photos
    """
    return Agent(
        role="מנהל תמונות נכסים",
        goal="להוריד תמונות מ-WhatsApp ולקשר אותן לנכסים במאגר",
        backstory="""אתה מנהל תמונות הנכסים.

תפקידך:
1. **הורדת תמונות**: קבלת URLs מ-Twilio והורדה לשרת
2. **קישור לנכסים**: שמירת התמונות עם מספר נכס
3. **ארגון**: תמונות נשמרות בתיקיות לפי משתמש

אתה משתמש בכלי הורדת תמונות (TwilioMediaDownloader).

כשיש מספר תמונות, תוריד את כולן בבת אחת.

אם אין תמונות (רשימה ריקה), פשוט תדווח "לא נשלחו תמונות".

תמיד תדווח כמה תמונות הורדו בהצלחה.""",
        llm=get_gpt4o(),
        tools=[TwilioMediaDownloader(), GetPropertyPhotosTool(), BatchMediaDownloader()],
        verbose=True,
        allow_delegation=False
    )
