"""
Property-client matching algorithm with weighted scoring.
"""
from crewai.tools import BaseTool
from pydantic import BaseModel
from typing import Type, List, Dict, Tuple, ClassVar
import logging
import json

from database.models import Property, Client, Match
from database.connection import get_session
from tools.schemas import PropertyMatchInput, ClientMatchInput

logger = logging.getLogger(__name__)


class PropertyMatcherTool(BaseTool):
    """Tool for finding matching properties for a client."""
    name: str = "מציאת נכסים תואמים ללקוח"
    description: str = "מחפש נכסים המתאימים לדרישות הלקוח ומחזיר רשימה עם ציוני התאמה."
    args_schema: Type[BaseModel] = PropertyMatchInput

    # Region mappings for location matching
    REGIONS: ClassVar[Dict[str, List[str]]] = {
        'גוש_דן': ['תל אביב', 'רמת גן', 'גבעתיים', 'בני ברק', 'חולון', 'בת ים'],
        'ירושלים': ['ירושלים', 'בית שמש', 'מודיעין'],
        'חיפה': ['חיפה', 'קריות', 'קריית ביאליק', 'קריית אתא', 'קריית מוצקין'],
        'מרכז': ['רעננה', 'כפר סבא', 'הרצליה', 'רמת השרון', 'הוד השרון'],
        'דרום': ['באר שבע', 'אשדוד', 'אשקלון'],
        'צפון': ['נצרת', 'כרמיאל', 'צפת', 'טבריה'],
    }

    def _run(self, client_id: int, limit: int = 5) -> str:
        """Find matching properties for a client."""
        try:
            with get_session() as session:
                # Get client
                client = session.query(Client).filter_by(id=client_id).first()
                if not client:
                    return f"לקוח מספר {client_id} לא נמצא במאגר."

                # Get all available properties with matching transaction type
                looking_for_mapping = {'rent': 'rent', 'buy': 'sale'}
                transaction_type = looking_for_mapping.get(client.looking_for)

                properties = session.query(Property).filter(
                    Property.status == 'available',
                    Property.transaction_type == transaction_type
                ).all()

                if not properties:
                    return f"לא נמצאו נכסים זמינים מסוג '{transaction_type}'."

                # Calculate match scores
                matches = []
                for prop in properties:
                    score = self._calculate_score(prop, client)
                    if score >= 65:  # Threshold for good match
                        matches.append({
                            'property': prop,
                            'score': score,
                            'explanation': self._explain_score(prop, client, score)
                        })

                # Sort by score
                matches.sort(key=lambda x: x['score'], reverse=True)
                top_matches = matches[:limit]

                if not top_matches:
                    return f"לא נמצאו נכסים מתאימים ללקוח {client.name}. אולי כדאי להרחיב את הקריטריונים."

                # Save matches to database
                for match in top_matches:
                    existing_match = session.query(Match).filter_by(
                        property_id=match['property'].id,
                        client_id=client_id
                    ).first()

                    if not existing_match:
                        db_match = Match(
                            property_id=match['property'].id,
                            client_id=client_id,
                            score=match['score'],
                            status='suggested'
                        )
                        session.add(db_match)

                # Format results
                result_lines = [
                    f"נמצאו {len(top_matches)} נכסים מתאימים ל{client.name}:\n"
                ]

                for i, match in enumerate(top_matches, 1):
                    prop = match['property']
                    score = match['score']
                    explanation = match['explanation']

                    result_lines.append(
                        f"{i}. נכס #{prop.id} - {prop.address} "
                        f"(ציון התאמה: {score:.0f}%)"
                    )
                    result_lines.append(f"   {prop.property_type} | {prop.rooms} חדרים | {prop.price:,}₪")
                    result_lines.append(f"   {explanation}\n")

                return "\n".join(result_lines)

        except Exception as e:
            logger.error(f"Error matching properties: {e}", exc_info=True)
            return f"שגיאה בחיפוש התאמות: {str(e)}"

    def _calculate_score(self, prop: Property, client: Client) -> float:
        """
        Calculate match score based on weighted criteria.

        Scoring breakdown:
        - Transaction type: Must match (0 if not)
        - Location: 25 points (exact city) or 15 (same region)
        - Rooms: 20 points (exact) or scaled by difference
        - Price: 15 points (within budget) or scaled by percentage over
        - Size: 10 points (meets minimum) or scaled by difference
        """
        score = 0.0

        # Transaction type must match (already filtered)
        score += 30

        # Location matching (25 points max)
        if client.city:
            if prop.city == client.city:
                score += 25
            elif self._same_region(prop.city, client.city):
                score += 15
            else:
                score -= 5

        # Room count matching (20 points max)
        if client.min_rooms and client.max_rooms:
            if client.min_rooms <= prop.rooms <= client.max_rooms:
                score += 20
            else:
                room_diff = min(
                    abs(prop.rooms - client.min_rooms),
                    abs(prop.rooms - client.max_rooms)
                )
                score += max(0, 20 - room_diff * 5)

        # Price matching (15 points max)
        if client.max_price:
            if prop.price <= client.max_price:
                score += 15
            else:
                over_budget_pct = (prop.price - client.max_price) / client.max_price
                if over_budget_pct <= 0.1:  # Up to 10% over budget
                    score += 10
                else:
                    score -= 15  # Significant penalty for over budget

        # Size matching (10 points max)
        if client.min_size and prop.size:
            if prop.size >= client.min_size:
                score += 10
            else:
                size_diff_pct = (client.min_size - prop.size) / client.min_size
                score += max(0, 10 - size_diff_pct * 50)

        return min(100, max(0, score))  # Clamp between 0-100

    def _same_region(self, city1: str, city2: str) -> bool:
        """Check if two cities are in the same region."""
        for region, cities in self.REGIONS.items():
            if city1 in cities and city2 in cities:
                return True
        return False

    def _explain_score(self, prop: Property, client: Client, score: float) -> str:
        """Generate explanation for the match score."""
        reasons = []

        # Location
        if client.city:
            if prop.city == client.city:
                reasons.append("✓ עיר מדויקת")
            elif self._same_region(prop.city, client.city):
                reasons.append("✓ אזור קרוב")
            else:
                reasons.append("⚠ אזור שונה")

        # Price
        if client.max_price:
            if prop.price <= client.max_price:
                reasons.append("✓ בתקציב")
            else:
                over_pct = ((prop.price - client.max_price) / client.max_price) * 100
                if over_pct <= 10:
                    reasons.append(f"⚠ מעל תקציב ב-{over_pct:.0f}%")
                else:
                    reasons.append(f"✗ מעל תקציב ב-{over_pct:.0f}%")

        # Rooms
        if client.min_rooms and client.max_rooms:
            if client.min_rooms <= prop.rooms <= client.max_rooms:
                reasons.append("✓ מספר חדרים מתאים")
            else:
                reasons.append("⚠ מספר חדרים שונה")

        # Size
        if client.min_size and prop.size:
            if prop.size >= client.min_size:
                reasons.append("✓ גודל מתאים")
            else:
                reasons.append("⚠ קטן מהרצוי")

        return " | ".join(reasons) if reasons else "התאמה בסיסית"


class ClientMatcherTool(BaseTool):
    """Tool for finding clients interested in a property."""
    name: str = "מציאת לקוחות מתאימים לנכס"
    description: str = "מחפש לקוחות שעשויים להתעניין בנכס מסוים."
    args_schema: Type[BaseModel] = ClientMatchInput

    def _run(self, property_id: int, limit: int = 5) -> str:
        """Find matching clients for a property."""
        try:
            with get_session() as session:
                # Get property
                prop = session.query(Property).filter_by(id=property_id).first()
                if not prop:
                    return f"נכס מספר {property_id} לא נמצא במאגר."

                # Get active clients with matching transaction type
                looking_for_mapping = {'rent': 'rent', 'sale': 'buy'}
                looking_for = looking_for_mapping.get(prop.transaction_type)

                clients = session.query(Client).filter(
                    Client.status == 'active',
                    Client.looking_for == looking_for
                ).all()

                if not clients:
                    return f"לא נמצאו לקוחות פעילים המחפשים נכסים ל{looking_for}."

                # Use PropertyMatcherTool logic in reverse
                matcher = PropertyMatcherTool()
                matches = []

                for client in clients:
                    score = matcher._calculate_score(prop, client)
                    if score >= 65:
                        matches.append({
                            'client': client,
                            'score': score,
                            'explanation': matcher._explain_score(prop, client, score)
                        })

                # Sort by score
                matches.sort(key=lambda x: x['score'], reverse=True)
                top_matches = matches[:limit]

                if not top_matches:
                    return f"לא נמצאו לקוחות מתאימים לנכס #{property_id}."

                # Save matches to database
                for match in top_matches:
                    existing_match = session.query(Match).filter_by(
                        property_id=property_id,
                        client_id=match['client'].id
                    ).first()

                    if not existing_match:
                        db_match = Match(
                            property_id=property_id,
                            client_id=match['client'].id,
                            score=match['score'],
                            status='suggested'
                        )
                        session.add(db_match)

                # Format results
                result_lines = [
                    f"נמצאו {len(top_matches)} לקוחות מתאימים לנכס ב{prop.address}:\n"
                ]

                for i, match in enumerate(top_matches, 1):
                    client = match['client']
                    score = match['score']
                    explanation = match['explanation']

                    result_lines.append(
                        f"{i}. {client.name} (ציון התאמה: {score:.0f}%)"
                    )
                    result_lines.append(
                        f"   מחפש: {client.min_rooms}-{client.max_rooms} חדרים | "
                        f"תקציב: {client.min_price:,}-{client.max_price:,}₪"
                    )
                    if client.phone:
                        result_lines.append(f"   טלפון: {client.phone}")
                    result_lines.append(f"   {explanation}\n")

                return "\n".join(result_lines)

        except Exception as e:
            logger.error(f"Error matching clients: {e}", exc_info=True)
            return f"שגיאה בחיפוש לקוחות: {str(e)}"
