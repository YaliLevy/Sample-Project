"""
CrewAI Orchestrator - Main routing logic for the WhatsApp bot.

Routes incoming messages to appropriate crews based on intent classification.
"""
from crewai import Crew, Task, Process
from agents.manager.manager_agent import create_manager_agent
from crews.property_crew import PropertyCrew
from crews.client_crew import ClientCrew
import logging

logger = logging.getLogger(__name__)


class CrewAIOrchestrator:
    """
    Main orchestrator that routes messages to specialized crews.

    Intent classification:
    - ADD_PROPERTY → PropertyCrew.add_property()
    - ADD_CLIENT → ClientCrew.add_client()
    - QUERY_PROPERTY → PropertyCrew.query_property()
    - QUERY_CLIENT → ClientCrew.query_client()
    - FIND_MATCHES → ClientCrew.find_matches()
    - GENERAL → Handle directly with manager
    """

    def __init__(self):
        """Initialize orchestrator with all crews and manager agent."""
        logger.info("Initializing CrewAI Orchestrator...")

        self.manager = create_manager_agent()
        self.property_crew = PropertyCrew()
        self.client_crew = ClientCrew()

        logger.info("Orchestrator initialized successfully")

    def classify_intent(self, message: str) -> str:
        """
        Classify the intent of a Hebrew message.

        Args:
            message: Hebrew message from user

        Returns:
            Intent string: ADD_PROPERTY, ADD_CLIENT, QUERY_PROPERTY,
                          QUERY_CLIENT, FIND_MATCHES, or GENERAL
        """
        logger.info(f"Classifying intent for: {message[:50]}...")

        task = Task(
            description=f"""סווג את כוונת ההודעה הבאה:

"{message}"

החזר **רק** אחד מהבאים (ללא הסבר):
- ADD_PROPERTY
- ADD_CLIENT
- QUERY_PROPERTY
- QUERY_CLIENT
- FIND_MATCHES
- GENERAL""",
            expected_output="Single intent keyword (ADD_PROPERTY, ADD_CLIENT, etc.)",
            agent=self.manager
        )

        crew = Crew(
            agents=[self.manager],
            tasks=[task],
            process=Process.sequential,
            verbose=False  # Less verbose for intent classification
        )

        try:
            result = crew.kickoff()
            intent = (result.raw if hasattr(result, 'raw') else str(result)).strip().upper()

            # Validate intent
            valid_intents = ['ADD_PROPERTY', 'ADD_CLIENT', 'QUERY_PROPERTY',
                           'QUERY_CLIENT', 'FIND_MATCHES', 'GENERAL']

            if intent not in valid_intents:
                logger.warning(f"Invalid intent returned: {intent}, defaulting to GENERAL")
                intent = 'GENERAL'

            logger.info(f"Classified intent: {intent}")
            return intent

        except Exception as e:
            logger.error(f"Error classifying intent: {e}", exc_info=True)
            return 'GENERAL'

    def process_message(self, message: str, phone_number: str, media_urls: list = None) -> str:
        """
        Main entry point for processing messages.

        Args:
            message: Hebrew message from user
            phone_number: User's phone number
            media_urls: Optional list of Twilio media URLs

        Returns:
            Hebrew response message
        """
        if media_urls is None:
            media_urls = []

        logger.info(f"Processing message from {phone_number}: {message[:50]}...")
        logger.info(f"Media URLs count: {len(media_urls)}")

        try:
            # Classify intent
            intent = self.classify_intent(message)

            # Route to appropriate crew
            if intent == 'ADD_PROPERTY':
                logger.info("Routing to Property Crew (add_property)")
                return self.property_crew.add_property(
                    user_message=message,
                    phone_number=phone_number,
                    media_urls=media_urls
                )

            elif intent == 'ADD_CLIENT':
                logger.info("Routing to Client Crew (add_client)")
                return self.client_crew.add_client(
                    user_message=message,
                    phone_number=phone_number
                )

            elif intent == 'QUERY_PROPERTY':
                logger.info("Routing to Property Crew (query_property)")
                return self.property_crew.query_property(query=message)

            elif intent == 'QUERY_CLIENT':
                logger.info("Routing to Client Crew (query_client)")
                return self.client_crew.query_client(query=message)

            elif intent == 'FIND_MATCHES':
                logger.info("Routing to Client Crew (find_matches)")
                return self.client_crew.find_matches(query=message)

            elif intent == 'GENERAL':
                logger.info("Handling as general query")
                return self._handle_general(message)

            else:
                logger.warning(f"Unknown intent: {intent}")
                return self._handle_general(message)

        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return self._handle_error(e)

    def _handle_general(self, message: str) -> str:
        """
        Handle general queries, greetings, and help requests.

        Args:
            message: Hebrew message

        Returns:
            Hebrew response
        """
        message_lower = message.strip().lower()

        # Short affirmative/negative responses - need more context
        if message_lower in ['כן', 'לא', 'אוקי', 'ok', 'בסדר', 'טוב', 'יאללה', 'כ', 'נ']:
            return """אשמח לעזור! 😊

כדי שאוכל להמשיך, אנא פרט מה תרצה:

🔍 **לחפש נכס?** כתוב: "תראה לי נכסים ב[עיר/רחוב]"
📋 **לראות פרטי נכס?** כתוב: "תראה לי נכס מספר [X]"
👥 **למצוא לקוחות מתאימים?** כתוב: "מי מתאים לנכס [X]"
📞 **לקבל פרטי קשר?** כתוב: "תן לי את הטלפון של בעל נכס [X]"

מה תרצה לעשות?"""

        # Greetings
        if any(word in message_lower for word in ['שלום', 'היי', 'מה קורה', 'בוקר טוב', 'ערב טוב']):
            return """שלום! 👋 אני עוזר חכם לניהול נדל"ן.

אני יכול לעזור לך:
🏠 להוסיף נכסים חדשים
📝 לרשום לקוחות
🔍 לחפש נכסים או לקוחות
✨ למצוא התאמות מושלמות

איך אוכל לעזור?"""

        # Help
        if any(word in message_lower for word in ['עזרה', 'מה אתה יכול', 'איך', 'הסבר']):
            return """אני עוזר חכם לניהול נדל"ן! 🏠

**איך להוסיף נכס:**
"דירה 3 חדרים בתל אביב רחוב דיזנגוף 102 5000 שקל להשכרה"
אפשר גם לשלוח תמונות! 📸

**איך להוסיף לקוח:**
"לקוח חדש יניב כהן מחפש 2-3 חדרים עד 6000 בתל אביב"

**איך לחפש:**
"תראה לי נכסים בדיזנגוף"
"מי מחפש 3 חדרים"

**איך למצוא התאמות:**
"מה מתאים ליניב"
"תמצא לקוחות לנכס בדיזנגוף 102"

מה תרצה לעשות?"""

        # Thanks
        if any(word in message_lower for word in ['תודה', 'תודה רבה', 'מעולה', 'אחלה']):
            return """בשמחה! 😊

אם תצטרך עוד משהו, אני כאן.

🏠 להוסיף נכס
📝 להוסיף לקוח
🔍 לחפש
✨ למצוא התאמות"""

        # Unknown
        return """לא הבנתי בדיוק מה ביקשת. 🤔

אני יכול לעזור לך:
🏠 להוסיף נכסים
📝 להוסיף לקוחות
🔍 לחפש נכסים או לקוחות
✨ למצוא התאמות

תנסה שוב? או כתוב "עזרה" למידע נוסף."""

    def _handle_error(self, error: Exception) -> str:
        """
        Generate friendly error message.

        Args:
            error: Exception that occurred

        Returns:
            Hebrew error message for user
        """
        error_msg = str(error)

        # Don't expose technical details to user
        return """מצטער, נתקלתי בבעיה טכנית. 😕

ההודעה שלך נשמרה, ואני מנסה לפתור את הבעיה.

תוכל לנסות שוב בעוד כמה רגעים, או ליצור קשר עם התמיכה.

תודה על הסבלנות!"""
