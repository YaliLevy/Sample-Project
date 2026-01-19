"""
Hebrew text search tools with fuzzy matching.
"""
# Try new import first, fallback to old
try:
    from langchain_core.tools import BaseTool
except ImportError:
    try:
        from crewai.tools import BaseTool
    except ImportError:
        from crewai.tool import BaseTool

from pydantic import BaseModel
from typing import Type, Optional
import logging

from database.models import Property, Client
from database.connection import get_session
from tools.schemas import HebrewSearchInput

logger = logging.getLogger(__name__)


class HebrewSearchTool(BaseTool):
    """Tool for searching properties and clients with Hebrew text."""
    name: str = "חיפוש טקסט בעברית"
    description: str = "מחפש נכסים או לקוחות לפי טקסט חופשי בעברית."
    args_schema: Type[BaseModel] = HebrewSearchInput

    # Hebrew abbreviation mappings
    ABBREVIATIONS = {
        'חד': 'חדרים',
        'חדר': 'חדרים',
        "חד'": 'חדרים',
        'מ"ר': 'מטר',
        'מר': 'מטר',
        'ת"א': 'תל אביב',
        'תא': 'תל אביב',
        'י-ם': 'ירושלים',
        'ירוש': 'ירושלים',
        'ק"ג': 'קומה גבוהה',
        'ש"ח': 'שקלים',
        'מיל': 'מיליון',
        "מיל'": 'מיליון',
    }

    def _run(
        self,
        query: str,
        search_in: str = 'properties',
        limit: int = 10
    ) -> str:
        """
        Search for properties or clients using Hebrew text.

        Args:
            query: Hebrew search query
            search_in: 'properties' or 'clients'
            limit: Maximum number of results

        Returns:
            Formatted search results in Hebrew
        """
        try:
            # Normalize query
            normalized_query = self._normalize_hebrew(query)

            if search_in == 'properties':
                return self._search_properties(normalized_query, limit)
            elif search_in == 'clients':
                return self._search_clients(normalized_query, limit)
            else:
                return f"סוג חיפוש לא נתמך: {search_in}. השתמש ב-'properties' או 'clients'."

        except Exception as e:
            logger.error(f"Error in Hebrew search: {e}", exc_info=True)
            return f"שגיאה בחיפוש: {str(e)}"

    def _normalize_hebrew(self, text: str) -> str:
        """Normalize Hebrew text by expanding abbreviations."""
        normalized = text

        # Replace abbreviations
        for abbr, full in self.ABBREVIATIONS.items():
            normalized = normalized.replace(abbr, full)

        return normalized.strip()

    def _search_properties(self, query: str, limit: int) -> str:
        """Search in properties table."""
        try:
            with get_session() as session:
                # Build search conditions
                search_filter = (
                    Property.address.ilike(f'%{query}%') |
                    Property.street.ilike(f'%{query}%') |
                    Property.city.ilike(f'%{query}%') |
                    Property.description.ilike(f'%{query}%') |
                    Property.property_type.ilike(f'%{query}%')
                )

                properties = session.query(Property).filter(search_filter).limit(limit).all()

                if not properties:
                    return f'לא נמצאו נכסים המתאימים לחיפוש "{query}".'

                # Format results
                result_lines = [f'נמצאו {len(properties)} נכסים:\n']
                for prop in properties:
                    result_lines.append(
                        f"נכס #{prop.id}: {prop.property_type} ב{prop.address}, "
                        f"{prop.rooms} חדרים, {prop.price:,}₪"
                    )
                    if prop.description:
                        desc_preview = prop.description[:50] + "..." if len(prop.description) > 50 else prop.description
                        result_lines.append(f"  {desc_preview}")

                return "\n".join(result_lines)

        except Exception as e:
            logger.error(f"Error searching properties: {e}", exc_info=True)
            return f"שגיאה בחיפוש נכסים: {str(e)}"

    def _search_clients(self, query: str, limit: int) -> str:
        """Search in clients table."""
        try:
            with get_session() as session:
                # Build search conditions
                search_filter = (
                    Client.name.ilike(f'%{query}%') |
                    Client.city.ilike(f'%{query}%') |
                    Client.property_type.ilike(f'%{query}%') |
                    Client.notes.ilike(f'%{query}%')
                )

                clients = session.query(Client).filter(search_filter).limit(limit).all()

                if not clients:
                    return f'לא נמצאו לקוחות המתאימים לחיפוש "{query}".'

                # Format results
                result_lines = [f'נמצאו {len(clients)} לקוחות:\n']
                for client in clients:
                    looking_type = "להשכרה" if client.looking_for == "rent" else "לקנייה"
                    result_lines.append(
                        f"לקוח #{client.id}: {client.name} - מחפש {looking_type}, "
                        f"{client.min_rooms}-{client.max_rooms} חדרים"
                    )
                    if client.city:
                        result_lines.append(f"  עיר: {client.city}")
                    if client.notes:
                        notes_preview = client.notes[:50] + "..." if len(client.notes) > 50 else client.notes
                        result_lines.append(f"  הערות: {notes_preview}")

                return "\n".join(result_lines)

        except Exception as e:
            logger.error(f"Error searching clients: {e}", exc_info=True)
            return f"שגיאה בחיפוש לקוחות: {str(e)}"
