"""
Client Database Agent - Handles client database operations.
"""
from crewai import Agent
from config.llm_config import get_gpt4o
from tools.database_tool import ClientSaveTool, ClientQueryTool, ClientUpdateTool


def create_client_db_agent():
    """
    Create Client Database Agent for CRUD operations.

    This agent uses database tools to:
    - Save new clients
    - Query existing clients
    - Update client status/details
    """
    return Agent(
        role="מנהל מאגר לקוחות",
        goal="לשמור ולחפש לקוחות במאגר הנתונים בצורה מדויקת",
        backstory="""אתה מנהל מאגר הלקוחות.

תפקידך:
1. **שמירת לקוחות**: קבלת פרטי לקוח JSON ושמירה במאגר
2. **חיפוש לקוחות**: חיפוש לפי שם, סוג חיפוש (rent/buy), עיר, סטטוס
3. **עדכון לקוחות**: עדכון סטטוס (active → closed), הערות

אתה משתמש בכלי מאגר הנתונים (ClientSaveTool, ClientQueryTool, ClientUpdateTool).

כשאתה שומר לקוח חדש, תמיד תחזיר את **מספר הלקוח** שנוצר.

כשאתה מחפש לקוחות, תחזיר רשימה ברורה עם הדרישות של כל לקוח.

תמיד תבצע את הפעולה המתבקשת ותדווח על התוצאה בעברית.""",
        llm=get_gpt4o(),
        tools=[ClientSaveTool(), ClientQueryTool(), ClientUpdateTool()],
        verbose=True,
        allow_delegation=False
    )
