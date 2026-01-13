"""
Property Crew - Manages property-related workflows.

Sequential workflow:
1. Parser Agent: Extract property details from Hebrew text
2. DB Agent: Save property to database
3. Photo Agent: Download and associate photos
4. Matcher Agent (via DB): Find matching clients
5. Response Agent: Generate friendly confirmation
"""
from crewai import Crew, Task, Process
from agents.property.parser_agent import create_property_parser_agent
from agents.property.db_agent import create_property_db_agent
from agents.property.photo_agent import create_property_photo_agent
from agents.property.response_agent import create_property_response_agent
from agents.client.matcher_agent import create_client_matcher_agent
import logging

logger = logging.getLogger(__name__)


class PropertyCrew:
    """Crew for handling property operations."""

    def __init__(self):
        """Initialize all agents."""
        self.parser = create_property_parser_agent()
        self.db_agent = create_property_db_agent()
        self.photo_agent = create_property_photo_agent()
        self.matcher = create_client_matcher_agent()
        self.response_agent = create_property_response_agent()

    def add_property(self, user_message: str, phone_number: str, media_urls: list = None):
        """
        Add a new property workflow.

        Args:
            user_message: Hebrew text describing the property
            phone_number: Phone number of user adding the property
            media_urls: Optional list of Twilio media URLs

        Returns:
            Hebrew response message
        """
        logger.info(f"Starting add_property workflow for: {user_message[:50]}...")

        if media_urls is None:
            media_urls = []

        # Task 1: Parse property details
        parse_task = Task(
            description=f"""נתח את ההודעה הבאה וחלץ פרטי נכס:

הודעה: "{user_message}"

חלץ: property_type, city, street, street_number, rooms, size, floor, price, transaction_type, owner_name, owner_phone, description.

אם חסר מידע קריטי (city או price), ציין מה חסר.

החזר JSON בלבד.""",
            expected_output="JSON object with property fields",
            agent=self.parser
        )

        # Task 2: Save to database
        save_task = Task(
            description=f"""קבל את פרטי הנכס מהמשימה הקודמת ושמור אותם במאגר.

הוסף את מספר הטלפון: {phone_number}

השתמש בכלי PropertySaveTool.

החזר את מספר הנכס שנוצר.""",
            expected_output="Property ID and confirmation message in Hebrew",
            agent=self.db_agent,
            context=[parse_task]
        )

        # Task 3: Download photos (if any)
        has_photos = len(media_urls) > 0
        photo_description = f"""הורד תמונות עבור הנכס שנשמר.

URLs: {media_urls}
מספר טלפון: {phone_number}

קשר את התמונות למספר הנכס שהתקבל מהמשימה הקודמת.

אם אין תמונות (רשימה ריקה), פשוט דווח "לא נשלחו תמונות"."""

        if has_photos:
            photo_description += f"\n\nיש {len(media_urls)} תמונות להוריד."

        photo_task = Task(
            description=photo_description,
            expected_output="Number of photos downloaded or 'no photos'",
            agent=self.photo_agent,
            context=[save_task]
        )

        # Task 4: Find matching clients
        match_task = Task(
            description="""חפש לקוחות שעשויים להתעניין בנכס שנשמר.

קבל את מספר הנכס מהמשימה הקודמת.

השתמש בכלי ClientMatcherTool.

החזר רשימת לקוחות מתאימים (עד 3) או "לא נמצאו התאמות".""",
            expected_output="List of matching clients or 'no matches'",
            agent=self.matcher,
            context=[save_task]
        )

        # Task 5: Generate response
        response_task = Task(
            description="""צור הודעת תשובה ידידותית בעברית.

סכם:
1. את הנכס שנשמר (פרטים מהמשימה הראשונה)
2. מספר הנכס (מהמשימה השנייה)
3. כמה תמונות הורדו (מהמשימה השלישית)
4. לקוחות מתאימים אם יש (מהמשימה הרביעית)

כתוב בסגנון חם וידידותי עם אימוג׳ים (🏠 📍 🛏️ 💰 📸).

מקסימום 1500 תווים.""",
            expected_output="Friendly Hebrew confirmation message (max 1500 chars)",
            agent=self.response_agent,
            context=[parse_task, save_task, photo_task, match_task]
        )

        # Create and execute crew
        crew = Crew(
            agents=[self.parser, self.db_agent, self.photo_agent, self.matcher, self.response_agent],
            tasks=[parse_task, save_task, photo_task, match_task, response_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()

        logger.info("Property crew completed successfully")
        return result.raw if hasattr(result, 'raw') else str(result)

    def query_property(self, query: str):
        """
        Query existing properties.

        Args:
            query: Search query in Hebrew

        Returns:
            Hebrew response with results
        """
        logger.info(f"Starting query_property workflow for: {query}")

        # Task 1: Parse search criteria
        parse_task = Task(
            description=f"""נתח את שאילתת החיפוש וחלץ קריטריונים:

שאילתה: "{query}"

חלץ: street, city, min_rooms, max_rooms, min_price, max_price, transaction_type.

החזר JSON עם הקריטריונים שזוהו.""",
            expected_output="JSON with search criteria",
            agent=self.parser
        )

        # Task 2: Search database
        search_task = Task(
            description="""חפש במאגר נכסים לפי הקריטריונים שהתקבלו.

השתמש בכלי PropertyQueryTool.

החזר רשימת נכסים מתאימים.""",
            expected_output="List of matching properties",
            agent=self.db_agent,
            context=[parse_task]
        )

        # Task 3: Format response
        response_task = Task(
            description="""הצג את תוצאות החיפוש בצורה ברורה וידידותית.

אם נמצאו נכסים, הצג אותם עם כל הפרטים החשובים.

אם לא נמצאו, הצע להרחיב את החיפוש.

מקסימום 1500 תווים.""",
            expected_output="Formatted search results in Hebrew",
            agent=self.response_agent,
            context=[search_task]
        )

        crew = Crew(
            agents=[self.parser, self.db_agent, self.response_agent],
            tasks=[parse_task, search_task, response_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        return result.raw if hasattr(result, 'raw') else str(result)
