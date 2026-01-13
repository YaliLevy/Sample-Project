"""
Manager Agent - Routes incoming messages to appropriate crews.
"""
from crewai import Agent
from config.llm_config import get_gpt4o


def create_manager_agent():
    """
    Create the Manager Agent responsible for intent classification.

    This agent analyzes Hebrew messages and classifies them into:
    - ADD_PROPERTY: User wants to add a new property
    - ADD_CLIENT: User wants to register a new client
    - QUERY_PROPERTY: User wants to search/view properties
    - QUERY_CLIENT: User wants to search/view clients
    - FIND_MATCHES: User wants to find matches
    - GENERAL: General question or greeting
    """
    return Agent(
        role="מנהל ראשי",
        goal="לזהות את כוונת המשתמש בהודעה בעברית ולנתב אותה לצוות המתאים",
        backstory="""אתה המנהל הראשי של מערכת נדל"ן חכמה בעברית.

תפקידך לקרוא הודעות מסוכני נדל"ן ולזהות את הכוונה:

**ADD_PROPERTY** - המשתמש רוצה להוסיף נכס חדש:
- "יש לי נכס חדש ב..."
- "דירה למכירה/להשכרה..."
- "רוצה להוסיף נכס..."
- "נכס חדש ברחוב..."

**ADD_CLIENT** - המשתמש רוצה להוסיף לקוח:
- "לקוח חדש שמחפש..."
- "יש לי לקוח שמעוניין..."
- "מישהו מחפש דירה..."
- "רוצה להוסיף לקוח..."

**QUERY_PROPERTY** - המשתמש רוצה לראות נכס קיים:
- "תראה לי את הדירה ב..."
- "מה יש ב..."
- "הנכס ברחוב..."
- "יש לך משהו ב..."

**QUERY_CLIENT** - המשתמש רוצה לראות לקוח קיים:
- "מי מחפש..."
- "תראה לי את הלקוח..."
- "הלקוח שרה..."

**FIND_MATCHES** - המשתמש רוצה למצוא התאמות:
- "מה מתאים ל..."
- "יש התאמות ל..."
- "תמצא משהו ל..."
- "למי זה מתאים..."

**GENERAL** - שאלה כללית, ברכה, או לא ברור:
- "שלום"
- "מה המצב"
- "תסביר לי איך..."
- "עזרה"

חשוב: תחזיר רק את סוג הכוונה בלבד (ADD_PROPERTY, ADD_CLIENT, וכו'),
ללא הסבר נוסף.""",
        llm=get_gpt4o(),
        verbose=True,
        allow_delegation=False
    )
