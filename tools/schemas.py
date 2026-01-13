"""
Pydantic schemas for tool input/output validation.
"""
from pydantic import BaseModel, Field
from typing import Optional, List


# Property Tool Schemas

class PropertySaveInput(BaseModel):
    """Input schema for saving a property."""
    property_type: str = Field(..., description="סוג נכס: דירה, בית, מגרש, וכו'")
    city: str = Field(..., description="עיר")
    street: Optional[str] = Field(None, description="שם רחוב")
    street_number: Optional[str] = Field(None, description="מספר בית")
    rooms: Optional[float] = Field(None, description="מספר חדרים (יכול להיות 2.5, 3.5)")
    size: Optional[int] = Field(None, description="גודל במטרים רבועים")
    floor: Optional[int] = Field(None, description="קומה")
    price: int = Field(..., description="מחיר בשקלים")
    transaction_type: str = Field(..., description="סוג עסקה: rent או sale")
    owner_name: Optional[str] = Field(None, description="שם בעל הנכס")
    owner_phone: Optional[str] = Field(None, description="טלפון בעל הנכס")
    description: Optional[str] = Field(None, description="תיאור נוסף")
    phone_number: str = Field(..., description="מספר טלפון של מי שמוסיף את הנכס")


class PropertyGetByIdInput(BaseModel):
    """Input schema for getting a specific property by ID."""
    property_id: int = Field(..., description="מזהה הנכס")


class PropertyQueryInput(BaseModel):
    """Input schema for querying properties."""
    property_id: Optional[int] = Field(None, description="מזהה נכס ספציפי - אם מוגדר, יחזיר רק את הנכס הזה")
    street: Optional[str] = Field(None, description="שם רחוב (חיפוש חלקי)")
    city: Optional[str] = Field(None, description="עיר")
    min_rooms: Optional[float] = Field(None, description="מינימום חדרים")
    max_rooms: Optional[float] = Field(None, description="מקסימום חדרים")
    min_price: Optional[int] = Field(None, description="מחיר מינימלי")
    max_price: Optional[int] = Field(None, description="מחיר מקסימלי")
    transaction_type: Optional[str] = Field(None, description="rent או sale")
    status: Optional[str] = Field("available", description="סטטוס הנכס")
    limit: int = Field(10, description="מספר מקסימלי של תוצאות")


class PropertyUpdateInput(BaseModel):
    """Input schema for updating a property."""
    property_id: int = Field(..., description="מזהה הנכס")
    status: Optional[str] = Field(None, description="סטטוס חדש: available, rented, sold, pending")
    price: Optional[int] = Field(None, description="מחיר חדש")
    description: Optional[str] = Field(None, description="תיאור חדש")


# Client Tool Schemas

class ClientSaveInput(BaseModel):
    """Input schema for saving a client."""
    name: str = Field(..., description="שם הלקוח")
    phone: Optional[str] = Field(None, description="טלפון הלקוח")
    looking_for: str = Field(..., description="מה הלקוח מחפש: rent או buy")
    property_type: Optional[str] = Field(None, description="סוג נכס: דירה, בית, וכו'")
    city: Optional[str] = Field(None, description="עיר מועדפת")
    min_rooms: Optional[float] = Field(None, description="מינימום חדרים")
    max_rooms: Optional[float] = Field(None, description="מקסימום חדרים")
    min_price: Optional[int] = Field(None, description="מחיר מינימלי")
    max_price: Optional[int] = Field(None, description="מחיר מקסימלי")
    min_size: Optional[int] = Field(None, description="גודל מינימלי במטרים")
    preferred_areas: Optional[List[str]] = Field(None, description="רשימת אזורים מועדפים")
    notes: Optional[str] = Field(None, description="הערות נוספות")
    phone_number: str = Field(..., description="מספר טלפון של מי שמוסיף את הלקוח")


class ClientQueryInput(BaseModel):
    """Input schema for querying clients."""
    name: Optional[str] = Field(None, description="שם לקוח (חיפוש חלקי)")
    looking_for: Optional[str] = Field(None, description="rent או buy")
    city: Optional[str] = Field(None, description="עיר")
    status: Optional[str] = Field("active", description="סטטוס הלקוח")
    limit: int = Field(10, description="מספר מקסימלי של תוצאות")


class ClientUpdateInput(BaseModel):
    """Input schema for updating a client."""
    client_id: int = Field(..., description="מזהה הלקוח")
    status: Optional[str] = Field(None, description="סטטוס חדש: active, closed, pending")
    notes: Optional[str] = Field(None, description="הערות עדכניות")


# Media Tool Schemas

class MediaDownloadInput(BaseModel):
    """Input schema for downloading media from Twilio."""
    media_url: str = Field(..., description="Twilio media URL")
    property_id: Optional[int] = Field(None, description="Property ID to associate with")
    user_phone: str = Field(..., description="User's phone number for organizing files")
    content_type: Optional[str] = Field("image/jpeg", description="Media content type")


# Matching Tool Schemas

class PropertyMatchInput(BaseModel):
    """Input schema for finding matches for a client."""
    client_id: int = Field(..., description="מזהה לקוח")
    limit: int = Field(5, description="מספר מקסימלי של התאמות")


class ClientMatchInput(BaseModel):
    """Input schema for finding clients for a property."""
    property_id: int = Field(..., description="מזהה נכס")
    limit: int = Field(5, description="מספר מקסימלי של לקוחות")


# WhatsApp Tool Schemas

class WhatsAppMessageInput(BaseModel):
    """Input schema for sending WhatsApp messages."""
    to_number: str = Field(..., description="Recipient phone number (with whatsapp: prefix)")
    message: str = Field(..., description="Message text (max 1600 characters)")
    media_urls: Optional[List[str]] = Field(None, description="Optional list of media URLs to send")


# Search Tool Schemas

class HebrewSearchInput(BaseModel):
    """Input schema for Hebrew text search."""
    query: str = Field(..., description="Hebrew search query")
    search_in: str = Field(..., description="Where to search: properties or clients")
    limit: int = Field(10, description="Maximum results")
