"""
Client Crew - Manages client-related workflows.

Sequential workflow:
1. Parser Agent: Extract client requirements from Hebrew text
2. DB Agent: Save client to database
3. Matcher Agent: Find matching properties
4. Response Agent: Generate friendly confirmation with matches
"""
from crewai import Crew, Task, Process
from agents.client.parser_agent import create_client_parser_agent
from agents.client.db_agent import create_client_db_agent
from agents.client.matcher_agent import create_client_matcher_agent
from agents.client.response_agent import create_client_response_agent
import logging

logger = logging.getLogger(__name__)


class ClientCrew:
    """Crew for handling client operations."""

    def __init__(self):
        """Initialize all agents."""
        self.parser = create_client_parser_agent()
        self.db_agent = create_client_db_agent()
        self.matcher = create_client_matcher_agent()
        self.response_agent = create_client_response_agent()

    def add_client(self, user_message: str, phone_number: str):
        """
        Add a new client workflow.

        Args:
            user_message: Hebrew text describing the client and their requirements
            phone_number: Phone number of user adding the client

        Returns:
            Hebrew response message
        """
        logger.info(f"Starting add_client workflow for: {user_message[:50]}...")

        # Task 1: Parse client requirements
        parse_task = Task(
            description=f"""נתח את ההודעה הבאה וחלץ פרטי לקוח:

הודעה: "{user_message}"

חלץ: name, phone, looking_for, property_type, city, min_rooms, max_rooms, min_price, max_price, min_size, preferred_areas, notes.

אם אין שם לקוח, כתוב "לקוח חדש".

החזר JSON בלבד.""",
            expected_output="JSON object with client fields",
            agent=self.parser
        )

        # Task 2: Save to database
        save_task = Task(
            description=f"""קבל את פרטי הלקוח מהמשימה הקודמת ושמור אותם במאגר.

הוסף את מספר הטלפון: {phone_number}

השתמש בכלי ClientSaveTool.

החזר את מספר הלקוח שנוצר.""",
            expected_output="Client ID and confirmation message in Hebrew",
            agent=self.db_agent,
            context=[parse_task]
        )

        # Task 3: Find matching properties
        match_task = Task(
            description="""חפש נכסים המתאימים לדרישות הלקוח.

קבל את מספר הלקוח מהמשימה הקודמת.

השתמש בכלי PropertyMatcherTool.

החזר את 3-5 ההתאמות הטובות ביותר עם הסברים.""",
            expected_output="List of matching properties with scores and explanations",
            agent=self.matcher,
            context=[save_task]
        )

        # Task 4: Generate response
        response_task = Task(
            description="""צור הודעת תשובה ידידותית בעברית.

סכם:
1. את הלקוח שנשמר (שם ודרישות)
2. מספר הלקוח
3. נכסים מתאימים שנמצאו עם פרטים והסבר ההתאמה

דגש את ההתאמות הטובות! זה מה שמעניין.

כתוב בסגנון חם עם אימוג׳ים (📝 🔍 ✨ 🏠).

מקסימום 1500 תווים.""",
            expected_output="Friendly Hebrew confirmation with matches (max 1500 chars)",
            agent=self.response_agent,
            context=[parse_task, save_task, match_task]
        )

        # Create and execute crew
        crew = Crew(
            agents=[self.parser, self.db_agent, self.matcher, self.response_agent],
            tasks=[parse_task, save_task, match_task, response_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()

        logger.info("Client crew completed successfully")
        return result.raw if hasattr(result, 'raw') else str(result)

    def query_client(self, query: str):
        """
        Query existing clients.

        Args:
            query: Search query in Hebrew

        Returns:
            Hebrew response with results
        """
        logger.info(f"Starting query_client workflow for: {query}")

        # Task 1: Parse search criteria
        parse_task = Task(
            description=f"""נתח את שאילתת החיפוש וחלץ קריטריונים:

שאילתה: "{query}"

חלץ: name, looking_for, city, status.

החזר JSON עם הקריטריונים.""",
            expected_output="JSON with search criteria",
            agent=self.parser
        )

        # Task 2: Search database
        search_task = Task(
            description="""חפש במאגר לקוחות לפי הקריטריונים.

השתמש בכלי ClientQueryTool.

החזר רשימת לקוחות מתאימים.""",
            expected_output="List of matching clients",
            agent=self.db_agent,
            context=[parse_task]
        )

        # Task 3: Format response
        response_task = Task(
            description="""הצג את תוצאות החיפוש בצורה ברורה.

עבור כל לקוח, הצג: שם, טלפון, דרישות, תאריך רישום.

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

    def find_matches(self, query: str):
        """
        Find matches for a specific client or property.

        Args:
            query: Hebrew query specifying what to match

        Returns:
            Hebrew response with matches
        """
        logger.info(f"Starting find_matches workflow for: {query}")

        # Task 1: Parse query to understand what to match
        parse_task = Task(
            description=f"""נתח את הבקשה להתאמות:

שאילתה: "{query}"

זהה: האם מדובר בחיפוש עבור לקוח ספציפי (שם) או סתם בקשה כללית.

חלץ את השם או הקריטריונים הרלוונטיים.""",
            expected_output="JSON with matching request details",
            agent=self.parser
        )

        # Task 2: Find the client/property
        find_task = Task(
            description="""מצא את הלקוח או הנכס הרלוונטי במאגר.

השתמש בכלי ClientQueryTool או PropertyQueryTool.

החזר את המזהה שנמצא.""",
            expected_output="Client or property ID",
            agent=self.db_agent,
            context=[parse_task]
        )

        # Task 3: Find matches
        match_task = Task(
            description="""מצא את ההתאמות הטובות ביותר.

השתמש בכלי PropertyMatcherTool או ClientMatcherTool בהתאם.

החזר את 5 ההתאמות הטובות ביותר עם הסברים.""",
            expected_output="Top 5 matches with scores and explanations",
            agent=self.matcher,
            context=[find_task]
        )

        # Task 4: Format response
        response_task = Task(
            description="""הצג את ההתאמות בצורה ברורה ומעניינת.

דגש את ההתאמות המצוינות.

הסבר למה כל התאמה טובה.

מקסימום 1500 תווים.""",
            expected_output="Formatted matches in Hebrew",
            agent=self.response_agent,
            context=[parse_task, match_task]
        )

        crew = Crew(
            agents=[self.parser, self.db_agent, self.matcher, self.response_agent],
            tasks=[parse_task, find_task, match_task, response_task],
            process=Process.sequential,
            verbose=True
        )

        result = crew.kickoff()
        return result.raw if hasattr(result, 'raw') else str(result)
