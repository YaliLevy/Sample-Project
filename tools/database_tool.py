"""
Database CRUD tools for CrewAI agents.
"""
from crewai_tools import BaseTool

from pydantic import BaseModel
from typing import Type, Optional, List
import logging
import json

from database.models import Property, Client, Photo, Match
from database.connection import get_session
from tools.schemas import (
    PropertySaveInput, PropertyQueryInput, PropertyUpdateInput, PropertyGetByIdInput,
    ClientSaveInput, ClientQueryInput, ClientUpdateInput
)

logger = logging.getLogger(__name__)


class PropertySaveTool(BaseTool):
    """Tool for saving a new property to the database."""
    name: str = "שמירת נכס במאגר"
    description: str = "שומר נכס חדש במאגר הנתונים. מקבל פרטי נכס מלאים ומחזיר מספר נכס."
    args_schema: Type[BaseModel] = PropertySaveInput

    def _run(
        self,
        property_type: str,
        city: str,
        price: int,
        transaction_type: str,
        phone_number: str,
        street: Optional[str] = None,
        street_number: Optional[str] = None,
        rooms: Optional[float] = None,
        size: Optional[int] = None,
        floor: Optional[int] = None,
        owner_name: Optional[str] = None,
        owner_phone: Optional[str] = None,
        description: Optional[str] = None
    ) -> str:
        """Save a property and return confirmation in Hebrew."""
        try:
            with get_session() as session:
                # Build full address
                address_parts = []
                if street:
                    address_parts.append(street)
                if street_number:
                    address_parts.append(street_number)
                address_parts.append(city)
                address = ", ".join(address_parts)

                # Create property
                property_obj = Property(
                    property_type=property_type,
                    city=city,
                    street=street,
                    street_number=street_number,
                    address=address,
                    rooms=rooms,
                    size=size,
                    floor=floor,
                    price=price,
                    transaction_type=transaction_type,
                    owner_name=owner_name,
                    owner_phone=owner_phone,
                    description=description,
                    status='available',
                    phone_number=phone_number
                )

                session.add(property_obj)
                session.flush()  # Get the ID

                property_id = property_obj.id

                logger.info(f"Saved property {property_id}: {address}")

                return f"הנכס נשמר בהצלחה! מספר נכס: {property_id}"

        except Exception as e:
            logger.error(f"Error saving property: {e}", exc_info=True)
            return f"שגיאה בשמירת הנכס: {str(e)}"


class PropertyGetByIdTool(BaseTool):
    """Tool for getting a specific property by ID with full details."""
    name: str = "שליפת נכס לפי מספר"
    description: str = "מחזיר את כל הפרטים של נכס ספציפי לפי מספר הנכס (ID). כולל: כתובת, חדרים, גודל, קומה, מחיר, בעלים, תיאור, תמונות."
    args_schema: Type[BaseModel] = PropertyGetByIdInput

    def _run(self, property_id: int) -> str:
        """Get a specific property by ID with all details."""
        try:
            with get_session() as session:
                prop = session.query(Property).filter_by(id=property_id).first()

                if not prop:
                    return f"נכס מספר {property_id} לא נמצא במאגר."

                photo_count = len(prop.photos)
                transaction = "להשכרה" if prop.transaction_type == "rent" else "למכירה"

                # Build full details response
                lines = [
                    f"פרטי נכס #{prop.id}:",
                    f"",
                    f"סוג: {prop.property_type}",
                    f"כתובת: {prop.address}",
                    f"עיר: {prop.city}",
                ]

                if prop.street:
                    lines.append(f"רחוב: {prop.street} {prop.street_number or ''}")

                if prop.rooms:
                    lines.append(f"חדרים: {prop.rooms}")

                if prop.size:
                    lines.append(f"גודל: {prop.size} מ\"ר")

                if prop.floor is not None:
                    lines.append(f"קומה: {prop.floor}")

                lines.append(f"מחיר: {prop.price:,}₪ {transaction}")
                lines.append(f"סטטוס: {prop.status}")

                if prop.owner_name:
                    lines.append(f"בעלים: {prop.owner_name}")

                if prop.owner_phone:
                    lines.append(f"טלפון בעלים: {prop.owner_phone}")

                if prop.description:
                    lines.append(f"תיאור: {prop.description}")

                lines.append(f"תמונות: {photo_count}")

                if prop.created_at:
                    lines.append(f"נוסף בתאריך: {prop.created_at.strftime('%d/%m/%Y')}")

                return "\n".join(lines)

        except Exception as e:
            logger.error(f"Error getting property by ID: {e}", exc_info=True)
            return f"שגיאה בשליפת נכס: {str(e)}"


class PropertyQueryTool(BaseTool):
    """Tool for querying properties from the database."""
    name: str = "חיפוש נכסים במאגר"
    description: str = "מחפש נכסים לפי קריטריונים שונים: מספר נכס, עיר, רחוב, מספר חדרים, מחיר, סוג עסקה. אם מחפשים נכס ספציפי לפי מספר, יחזיר את כל הפרטים."
    args_schema: Type[BaseModel] = PropertyQueryInput

    def _run(
        self,
        property_id: Optional[int] = None,
        street: Optional[str] = None,
        city: Optional[str] = None,
        min_rooms: Optional[float] = None,
        max_rooms: Optional[float] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        transaction_type: Optional[str] = None,
        status: Optional[str] = "available",
        limit: int = 10
    ) -> str:
        """Query properties and return formatted results in Hebrew."""
        try:
            with get_session() as session:
                # If specific property_id is provided, return full details
                if property_id:
                    prop = session.query(Property).filter_by(id=property_id).first()

                    if not prop:
                        return f"נכס מספר {property_id} לא נמצא במאגר."

                    return self._format_full_property(prop)

                # Otherwise, search with filters
                query = session.query(Property)

                if street:
                    query = query.filter(Property.street.ilike(f'%{street}%'))
                if city:
                    query = query.filter(Property.city.ilike(f'%{city}%'))
                if min_rooms:
                    query = query.filter(Property.rooms >= min_rooms)
                if max_rooms:
                    query = query.filter(Property.rooms <= max_rooms)
                if min_price:
                    query = query.filter(Property.price >= min_price)
                if max_price:
                    query = query.filter(Property.price <= max_price)
                if transaction_type:
                    query = query.filter(Property.transaction_type == transaction_type)
                if status:
                    query = query.filter(Property.status == status)

                properties = query.limit(limit).all()

                if not properties:
                    return "לא נמצאו נכסים התואמים את הקריטריונים."

                # Format results with full details
                result_lines = [f"נמצאו {len(properties)} נכסים:\n"]
                for prop in properties:
                    result_lines.append(self._format_full_property(prop))
                    result_lines.append("-" * 30)

                return "\n".join(result_lines)

        except Exception as e:
            logger.error(f"Error querying properties: {e}", exc_info=True)
            return f"שגיאה בחיפוש נכסים: {str(e)}"

    def _format_full_property(self, prop: Property) -> str:
        """Format a property with all its details."""
        photo_count = len(prop.photos)
        transaction = "להשכרה" if prop.transaction_type == "rent" else "למכירה"

        lines = [f"נכס #{prop.id}: {prop.property_type} ב{prop.address}"]

        details = []
        if prop.rooms:
            details.append(f"{prop.rooms} חדרים")
        if prop.size:
            details.append(f"{prop.size} מ\"ר")
        if prop.floor is not None:
            details.append(f"קומה {prop.floor}")

        if details:
            lines.append("  " + " | ".join(details))

        lines.append(f"  מחיר: {prop.price:,}₪ {transaction}")

        if prop.owner_name or prop.owner_phone:
            owner_info = []
            if prop.owner_name:
                owner_info.append(prop.owner_name)
            if prop.owner_phone:
                owner_info.append(prop.owner_phone)
            lines.append(f"  בעלים: {' - '.join(owner_info)}")

        if prop.description:
            lines.append(f"  תיאור: {prop.description}")

        if photo_count > 0:
            lines.append(f"  תמונות: {photo_count}")

        lines.append(f"  סטטוס: {prop.status}")

        return "\n".join(lines)


class PropertyUpdateTool(BaseTool):
    """Tool for updating property details."""
    name: str = "עדכון נכס במאגר"
    description: str = "מעדכן פרטי נכס קיים: סטטוס, מחיר, תיאור."
    args_schema: Type[BaseModel] = PropertyUpdateInput

    def _run(
        self,
        property_id: int,
        status: Optional[str] = None,
        price: Optional[int] = None,
        description: Optional[str] = None
    ) -> str:
        """Update property and return confirmation."""
        try:
            with get_session() as session:
                property_obj = session.query(Property).filter_by(id=property_id).first()

                if not property_obj:
                    return f"נכס מספר {property_id} לא נמצא במאגר."

                # Update fields
                if status:
                    property_obj.status = status
                if price:
                    property_obj.price = price
                if description:
                    property_obj.description = description

                logger.info(f"Updated property {property_id}")

                return f"נכס #{property_id} עודכן בהצלחה!"

        except Exception as e:
            logger.error(f"Error updating property: {e}", exc_info=True)
            return f"שגיאה בעדכון נכס: {str(e)}"


class ClientSaveTool(BaseTool):
    """Tool for saving a new client to the database."""
    name: str = "שמירת לקוח במאגר"
    description: str = "שומר לקוח חדש במאגר הנתונים. מקבל פרטי לקוח ודרישות חיפוש."
    args_schema: Type[BaseModel] = ClientSaveInput

    def _run(
        self,
        name: str,
        looking_for: str,
        phone_number: str,
        phone: Optional[str] = None,
        property_type: Optional[str] = None,
        city: Optional[str] = None,
        min_rooms: Optional[float] = None,
        max_rooms: Optional[float] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_size: Optional[int] = None,
        preferred_areas: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> str:
        """Save a client and return confirmation in Hebrew."""
        try:
            with get_session() as session:
                # Convert preferred_areas to JSON string
                preferred_areas_json = None
                if preferred_areas:
                    preferred_areas_json = json.dumps(preferred_areas, ensure_ascii=False)

                # Create client
                client_obj = Client(
                    name=name,
                    phone=phone,
                    looking_for=looking_for,
                    property_type=property_type,
                    city=city,
                    min_rooms=min_rooms,
                    max_rooms=max_rooms,
                    min_price=min_price,
                    max_price=max_price,
                    min_size=min_size,
                    preferred_areas=preferred_areas_json,
                    notes=notes,
                    status='active',
                    phone_number=phone_number
                )

                session.add(client_obj)
                session.flush()

                client_id = client_obj.id

                logger.info(f"Saved client {client_id}: {name}")

                return f"הלקוח {name} נשמר בהצלחה! מספר לקוח: {client_id}"

        except Exception as e:
            logger.error(f"Error saving client: {e}", exc_info=True)
            return f"שגיאה בשמירת הלקוח: {str(e)}"


class ClientQueryTool(BaseTool):
    """Tool for querying clients from the database."""
    name: str = "חיפוש לקוחות במאגר"
    description: str = "מחפש לקוחות לפי שם, סוג חיפוש (rent/buy), עיר, סטטוס."
    args_schema: Type[BaseModel] = ClientQueryInput

    def _run(
        self,
        name: Optional[str] = None,
        looking_for: Optional[str] = None,
        city: Optional[str] = None,
        status: Optional[str] = "active",
        limit: int = 10
    ) -> str:
        """Query clients and return formatted results in Hebrew."""
        try:
            with get_session() as session:
                query = session.query(Client)

                # Apply filters
                if name:
                    query = query.filter(Client.name.ilike(f'%{name}%'))
                if looking_for:
                    query = query.filter(Client.looking_for == looking_for)
                if city:
                    query = query.filter(Client.city == city)
                if status:
                    query = query.filter(Client.status == status)

                # Execute query
                clients = query.limit(limit).all()

                if not clients:
                    return "לא נמצאו לקוחות התואמים את הקריטריונים."

                # Format results
                result_lines = [f"נמצאו {len(clients)} לקוחות:\n"]
                for client in clients:
                    looking_type = "להשכרה" if client.looking_for == "rent" else "לקנייה"

                    # Build client info line with None handling
                    client_line = f"לקוח #{client.id}: {client.name} - מחפש {looking_type}"

                    # Add rooms info if available
                    if client.min_rooms is not None or client.max_rooms is not None:
                        min_r = client.min_rooms if client.min_rooms is not None else "?"
                        max_r = client.max_rooms if client.max_rooms is not None else "?"
                        client_line += f", {min_r}-{max_r} חדרים"

                    # Add budget info if available
                    if client.min_price is not None or client.max_price is not None:
                        min_p = f"{client.min_price:,}" if client.min_price is not None else "?"
                        max_p = f"{client.max_price:,}" if client.max_price is not None else "?"
                        client_line += f", תקציב: {min_p}-{max_p}₪"

                    result_lines.append(client_line)
                    if client.city:
                        result_lines.append(f"  עיר מועדפת: {client.city}")

                return "\n".join(result_lines)

        except Exception as e:
            logger.error(f"Error querying clients: {e}", exc_info=True)
            return f"שגיאה בחיפוש לקוחות: {str(e)}"


class ClientUpdateTool(BaseTool):
    """Tool for updating client details."""
    name: str = "עדכון לקוח במאגר"
    description: str = "מעדכן פרטי לקוח קיים: סטטוס, הערות."
    args_schema: Type[BaseModel] = ClientUpdateInput

    def _run(
        self,
        client_id: int,
        status: Optional[str] = None,
        notes: Optional[str] = None
    ) -> str:
        """Update client and return confirmation."""
        try:
            with get_session() as session:
                client_obj = session.query(Client).filter_by(id=client_id).first()

                if not client_obj:
                    return f"לקוח מספר {client_id} לא נמצא במאגר."

                # Update fields
                if status:
                    client_obj.status = status
                if notes:
                    client_obj.notes = notes

                logger.info(f"Updated client {client_id}")

                return f"לקוח #{client_id} ({client_obj.name}) עודכן בהצלחה!"

        except Exception as e:
            logger.error(f"Error updating client: {e}", exc_info=True)
            return f"שגיאה בעדכון לקוח: {str(e)}"
