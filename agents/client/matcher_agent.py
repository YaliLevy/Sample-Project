"""
Client Matcher Agent - Finds property-client matches.
"""
from crewai import Agent
from config.llm_config import get_gpt4o
from tools.matching_tool import PropertyMatcherTool, ClientMatcherTool


def create_client_matcher_agent():
    """
    Create Client Matcher Agent for finding matches.

    This agent uses matching algorithms to:
    - Find properties that match a client's requirements
    - Find clients interested in a specific property
    """
    return Agent(
        role="מומחה התאמות",
        goal="למצוא את ההתאמות הטובות ביותר בין לקוחות לנכסים",
        backstory="""אתה מומחה להתאמת נכסים ללקוחות.

תפקידך למצוא את ההתאמות הטובות ביותר על סמך:
1. **סוג עסקה**: חובה התאמה (rent ↔ rent, sale ↔ buy)
2. **מיקום**: עיר מדויקת או אותו אזור (גוש דן, ירושלים, חיפה)
3. **מספר חדרים**: בתוך הטווח המבוקש
4. **מחיר**: בתקציב או עד 10% מעל
5. **גודל**: מעל המינימום אם צוין

אתה משתמש בכלי ההתאמה (PropertyMatcherTool, ClientMatcherTool).

**אלגוריתם הציונים:**
- 100-85 נקודות: התאמה מצוינת ✨
- 84-75 נקודות: התאמה טובה מאוד
- 74-65 נקודות: התאמה סבירה
- מתחת ל-65: לא מציג

תמיד תסביר למה ההתאמה טובה:
- "עיר מדויקת, בתקציב, מספר חדרים מתאים"
- "אזור קרוב, מעט מעל תקציב (5%)"

תמיד תחזיר את הלקוחות/נכסים הכי מתאימים קודם.""",
        llm=get_gpt4o(),
        tools=[PropertyMatcherTool(), ClientMatcherTool()],
        verbose=True,
        allow_delegation=False
    )
