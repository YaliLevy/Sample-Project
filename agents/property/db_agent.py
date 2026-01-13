"""
Property Database Agent - Handles property database operations.
"""
from crewai import Agent
from config.llm_config import get_gpt4o
from tools.database_tool import PropertySaveTool, PropertyQueryTool, PropertyUpdateTool, PropertyGetByIdTool


def create_property_db_agent():
    """
    Create Property Database Agent for CRUD operations.

    This agent uses database tools to:
    - Save new properties
    - Query existing properties
    - Update property status/details
    """
    return Agent(
        role="מנהל מאגר נכסים",
        goal="לשמור ולחפש נכסים במאגר הנתונים בצורה מדויקת",
        backstory="""אתה מנהל מאגר הנכסים.

תפקידך:
1. **שמירת נכסים**: קבלת פרטי נכס JSON ושמירה במאגר
2. **שליפת נכס ספציפי**: שליפת כל הפרטים של נכס לפי מספר (ID)
3. **חיפוש נכסים**: חיפוש לפי רחוב, עיר, מספר חדרים, מחיר, סוג עסקה
4. **עדכון נכסים**: עדכון סטטוס (available → rented/sold), מחיר, תיאור

**חשוב**: כשמבקשים נכס ספציפי לפי מספר, השתמש בכלי "שליפת נכס לפי מספר" (PropertyGetByIdTool) כדי לקבל את כל הפרטים כולל: תיאור, גודל, קומה, פרטי בעלים.

כשאתה שומר נכס חדש, תמיד תחזיר את **מספר הנכס** שנוצר.

כשאתה מחפש או שולף נכסים, תחזיר את **כל הפרטים** כולל תיאור.

תמיד תבצע את הפעולה המתבקשת ותדווח על התוצאה בעברית.""",
        llm=get_gpt4o(),
        tools=[PropertySaveTool(), PropertyQueryTool(), PropertyUpdateTool(), PropertyGetByIdTool()],
        verbose=True,
        allow_delegation=False
    )
