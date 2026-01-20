"""
Media handling tools for Twilio WhatsApp photos.
Downloads media from Twilio with authentication and stores in Supabase Storage.
"""
from crewai_tools import BaseTool

from pydantic import BaseModel
from typing import Type, Optional
import logging
import requests
from requests.auth import HTTPBasicAuth
import os
from uuid import uuid4
from datetime import datetime
from supabase import create_client, Client

from database.models import Photo
from database.connection import get_session
from tools.schemas import MediaDownloadInput
from config import settings

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


class TwilioMediaDownloader(BaseTool):
    """Tool for downloading media from Twilio WhatsApp and uploading to Supabase."""
    name: str = "הורדת תמונות מ-WhatsApp"
    description: str = "מוריד תמונות שנשלחו ב-WhatsApp דרך Twilio ומעלה אותן ל-Supabase Storage."
    args_schema: Type[BaseModel] = MediaDownloadInput

    def _run(
        self,
        media_url: str,
        user_phone: str,
        property_id: Optional[int] = None,
        content_type: Optional[str] = "image/jpeg"
    ) -> str:
        """
        Download media from Twilio and upload to Supabase Storage.

        Args:
            media_url: Twilio media URL
            user_phone: User's phone number for organizing files
            property_id: Optional property ID to associate with
            content_type: Media content type

        Returns:
            Hebrew confirmation message with file URL
        """
        try:
            # Authenticate with Twilio
            auth = HTTPBasicAuth(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )

            # Download media from Twilio
            logger.info(f"Downloading media from: {media_url}")
            response = requests.get(media_url, auth=auth, timeout=30)
            response.raise_for_status()

            # Determine file extension
            extension = self._get_extension(content_type, media_url)

            # Generate unique filename with user organization
            file_id = str(uuid4())
            timestamp = int(datetime.now().timestamp())
            user_clean = user_phone.replace('+', '').replace('whatsapp:', '').replace(':', '')

            # Supabase storage path: user_[phone]/property_[id]/[uuid]_[timestamp].jpg
            if property_id:
                storage_path = f"user_{user_clean}/property_{property_id}/{file_id}_{timestamp}{extension}"
            else:
                storage_path = f"user_{user_clean}/temp/{file_id}_{timestamp}{extension}"

            # Upload to Supabase Storage
            logger.info(f"Uploading to Supabase Storage: {storage_path}")

            upload_response = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).upload(
                path=storage_path,
                file=response.content,
                file_options={"content-type": content_type}
            )

            # Get public URL
            public_url = supabase.storage.from_(settings.SUPABASE_STORAGE_BUCKET).get_public_url(storage_path)

            logger.info(f"Photo uploaded successfully: {public_url}")

            # Save to database if property_id provided
            if property_id:
                with get_session() as session:
                    photo = Photo(
                        property_id=property_id,
                        file_path=public_url,  # Store Supabase URL
                        twilio_media_url=media_url,
                        media_content_type=content_type
                    )
                    session.add(photo)
                    logger.info(f"Associated photo with property {property_id}")

                return f"התמונה הועלתה ל-Supabase ונקשרה לנכס #{property_id}. ✅"
            else:
                return f"התמונה הועלתה ל-Supabase בהצלחה. ✅"

        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading media from Twilio: {e}", exc_info=True)
            return f"שגיאה בהורדת התמונה מ-Twilio: {str(e)}"
        except Exception as e:
            logger.error(f"Error uploading to Supabase: {e}", exc_info=True)
            return f"שגיאה בהעלאת התמונה ל-Supabase: {str(e)}"

    def _get_extension(self, content_type: str, url: str) -> str:
        """Determine file extension from content type or URL."""
        # Map content types to extensions
        type_map = {
            'image/jpeg': '.jpg',
            'image/jpg': '.jpg',
            'image/png': '.png',
            'image/gif': '.gif',
            'image/webp': '.webp',
            'video/mp4': '.mp4',
            'video/quicktime': '.mov',
        }

        # Try content type first
        if content_type and content_type in type_map:
            return type_map[content_type]

        # Try URL extension
        if '.' in url:
            url_ext = '.' + url.split('.')[-1].split('?')[0].lower()
            if url_ext in type_map.values():
                return url_ext

        # Default to jpg
        return '.jpg'


class GetPropertyPhotosTool(BaseTool):
    """Tool for retrieving photos associated with a property."""
    name: str = "קבלת תמונות נכס"
    description: str = "מחזיר רשימת תמונות של נכס מסוים מהמאגר."

    class Input(BaseModel):
        property_id: int

    args_schema: Type[BaseModel] = Input

    def _run(self, property_id: int) -> str:
        """Get photos for a property."""
        try:
            with get_session() as session:
                photos = session.query(Photo).filter_by(property_id=property_id).all()

                if not photos:
                    return f"לא נמצאו תמונות לנכס #{property_id}."

                # Format results - showing Supabase URLs
                result_lines = [f"נמצאו {len(photos)} תמונות לנכס #{property_id}:\n"]
                for i, photo in enumerate(photos, 1):
                    result_lines.append(f"{i}. {photo.file_path}")

                return "\n".join(result_lines)

        except Exception as e:
            logger.error(f"Error retrieving photos: {e}", exc_info=True)
            return f"שגיאה בקבלת התמונות: {str(e)}"


class BatchMediaDownloader(BaseTool):
    """Tool for downloading multiple media files at once."""
    name: str = "הורדת מספר תמונות"
    description: str = "מוריד מספר תמונות מ-WhatsApp בבת אחת."

    class Input(BaseModel):
        media_urls: list
        user_phone: str
        property_id: Optional[int] = None

    args_schema: Type[BaseModel] = Input

    def _run(
        self,
        media_urls: list,
        user_phone: str,
        property_id: Optional[int] = None
    ) -> str:
        """Download multiple media files."""
        try:
            downloader = TwilioMediaDownloader()
            results = []
            success_count = 0

            for i, media_url in enumerate(media_urls, 1):
                logger.info(f"Downloading media {i}/{len(media_urls)}")
                result = downloader._run(
                    media_url=media_url,
                    user_phone=user_phone,
                    property_id=property_id
                )

                if "נשמרה" in result:
                    success_count += 1

                results.append(f"{i}. {result}")

            summary = f"הורדו {success_count} מתוך {len(media_urls)} תמונות בהצלחה."
            if property_id:
                summary += f" נקשרו לנכס #{property_id}."

            return summary + "\n\n" + "\n".join(results)

        except Exception as e:
            logger.error(f"Error in batch download: {e}", exc_info=True)
            return f"שגיאה בהורדת התמונות: {str(e)}"
