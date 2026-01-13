"""
🔍 בדיקות שיטתיות לאיתור בעיות בבוט
הרץ כל פונקציה בנפרד לזהות איפה הבעיה
"""
import logging

# הגדר לוגים מפורטים
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_1_database_connection():
    """
    📊 בדיקה 1: חיבור למסד נתונים
    """
    print("\n" + "="*60)
    print("📊 בדיקה 1: חיבור למסד נתונים")
    print("="*60)

    try:
        from database.connection import get_session
        from database.models import Property, Client

        with get_session() as session:
            properties_count = session.query(Property).count()
            clients_count = session.query(Client).count()

        print(f"✅ חיבור למסד נתונים תקין!")
        print(f"   נכסים: {properties_count}")
        print(f"   לקוחות: {clients_count}")
        return True

    except Exception as e:
        print(f"❌ שגיאה בחיבור למסד נתונים: {e}")
        return False


def test_2_openai_connection():
    """
    🤖 בדיקה 2: חיבור ל-OpenAI
    """
    print("\n" + "="*60)
    print("🤖 בדיקה 2: חיבור ל-OpenAI")
    print("="*60)

    try:
        from config import settings
        import openai

        client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

        # בדיקה פשוטה
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "אמור 'בדיקה תקינה' בעברית"}],
            max_tokens=20
        )

        result = response.choices[0].message.content
        print(f"✅ חיבור ל-OpenAI תקין!")
        print(f"   תשובה: {result}")
        return True

    except Exception as e:
        print(f"❌ שגיאה בחיבור ל-OpenAI: {e}")
        return False


def test_3_manager_agent():
    """
    🎯 בדיקה 3: Manager Agent - סיווג כוונות
    """
    print("\n" + "="*60)
    print("🎯 בדיקה 3: Manager Agent - סיווג כוונות")
    print("="*60)

    try:
        from crews.orchestrator import CrewAIOrchestrator

        orchestrator = CrewAIOrchestrator()

        test_messages = [
            ("דירה 3 חדרים בתל אביב 5000 שקל", "ADD_PROPERTY"),
            ("לקוח חדש יניב מחפש דירה", "ADD_CLIENT"),
            ("שלום", "GENERAL"),
        ]

        for message, expected in test_messages:
            print(f"\n   בודק: '{message[:30]}...'")
            intent = orchestrator.classify_intent(message)
            status = "✅" if intent == expected else "⚠️"
            print(f"   {status} כוונה: {intent} (צפוי: {expected})")

        print("\n✅ Manager Agent עובד!")
        return True

    except Exception as e:
        print(f"❌ שגיאה ב-Manager Agent: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_4_property_crew_response():
    """
    🏠 בדיקה 4: Property Crew - האם מחזיר תשובה?
    """
    print("\n" + "="*60)
    print("🏠 בדיקה 4: Property Crew - האם מחזיר תשובה?")
    print("="*60)

    try:
        from crews.property_crew import PropertyCrew

        crew = PropertyCrew()

        test_message = "דירה 3 חדרים בתל אביב רחוב דיזנגוף 102 קומה 5 80 מטר 6000 שקל להשכרה בעלים יוסי 0501234567"

        print(f"   שולח: '{test_message[:50]}...'")
        print("   מעבד... (זה יכול לקחת 15-30 שניות)")

        result = crew.add_property(
            user_message=test_message,
            phone_number="0501234567",
            media_urls=[]
        )

        print(f"\n   סוג התוצאה: {type(result)}")
        print(f"   אורך התוצאה: {len(str(result)) if result else 0}")
        print(f"\n   תוצאה:")
        print("-" * 40)
        print(result if result else "❌ תוצאה ריקה!")
        print("-" * 40)

        if result and len(str(result)) > 10:
            print("\n✅ Property Crew מחזיר תשובה!")
            return True
        else:
            print("\n❌ Property Crew לא מחזיר תשובה!")
            return False

    except Exception as e:
        print(f"❌ שגיאה ב-Property Crew: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_5_orchestrator_full_flow():
    """
    🎼 בדיקה 5: Orchestrator - זרימה מלאה
    """
    print("\n" + "="*60)
    print("🎼 בדיקה 5: Orchestrator - זרימה מלאה")
    print("="*60)

    try:
        from crews.orchestrator import CrewAIOrchestrator

        orchestrator = CrewAIOrchestrator()

        test_message = "דירה 2 חדרים בירושלים 4500 שקל להשכרה"
        phone = "0509999999"

        print(f"   שולח: '{test_message}'")
        print("   מעבד... (זה יכול לקחת 20-40 שניות)")

        result = orchestrator.process_message(
            message=test_message,
            phone_number=phone,
            media_urls=[]
        )

        print(f"\n   סוג התוצאה: {type(result)}")
        print(f"   אורך התוצאה: {len(str(result)) if result else 0}")
        print(f"\n   תוצאה:")
        print("-" * 40)
        print(result if result else "❌ תוצאה ריקה!")
        print("-" * 40)

        if result and len(str(result)) > 10:
            print("\n✅ Orchestrator מחזיר תשובה!")
            return True
        else:
            print("\n❌ Orchestrator לא מחזיר תשובה!")
            return False

    except Exception as e:
        print(f"❌ שגיאה ב-Orchestrator: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_6_twilio_credentials():
    """
    📱 בדיקה 6: Twilio Credentials
    """
    print("\n" + "="*60)
    print("📱 בדיקה 6: Twilio Credentials")
    print("="*60)

    try:
        from config import settings
        from twilio.rest import Client

        client = Client(
            settings.TWILIO_ACCOUNT_SID,
            settings.TWILIO_AUTH_TOKEN
        )

        # בדוק שהחשבון קיים
        account = client.api.accounts(settings.TWILIO_ACCOUNT_SID).fetch()

        print(f"✅ Twilio Credentials תקינים!")
        print(f"   Account Status: {account.status}")
        print(f"   WhatsApp Number: {settings.TWILIO_WHATSAPP_NUMBER}")
        return True

    except Exception as e:
        print(f"❌ שגיאה ב-Twilio: {e}")
        return False


def test_7_webhook_simulation():
    """
    🌐 בדיקה 7: סימולציית Webhook
    """
    print("\n" + "="*60)
    print("🌐 בדיקה 7: סימולציית Webhook (ללא שליחה אמיתית)")
    print("="*60)

    try:
        from bot.twilio_handler import app

        # צור test client
        with app.test_client() as client:
            # סמלץ הודעה נכנסת
            response = client.post('/webhook', data={
                'From': 'whatsapp:+972501234567',
                'Body': 'שלום',
                'NumMedia': '0'
            })

            print(f"   Status Code: {response.status_code}")
            print(f"   Response Length: {len(response.data)}")
            print(f"\n   Response:")
            print("-" * 40)

            # פענח את התשובה
            response_text = response.data.decode('utf-8')
            print(response_text[:500] if len(response_text) > 500 else response_text)
            print("-" * 40)

            if response.status_code == 200 and len(response.data) > 50:
                print("\n✅ Webhook מגיב כראוי!")
                return True
            else:
                print("\n❌ בעיה בתגובת Webhook!")
                return False

    except Exception as e:
        print(f"❌ שגיאה בסימולציית Webhook: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """
    🚀 הרץ את כל הבדיקות בסדר
    """
    print("\n" + "🚀"*30)
    print("      מתחיל בדיקות שיטתיות")
    print("🚀"*30)

    results = {}

    # בדיקות בסיסיות קודם
    results['1. Database'] = test_1_database_connection()
    if not results['1. Database']:
        print("\n⛔ עצור! תקן את הבעיה במסד הנתונים לפני שממשיכים")
        return results

    results['2. OpenAI'] = test_2_openai_connection()
    if not results['2. OpenAI']:
        print("\n⛔ עצור! תקן את הבעיה ב-OpenAI לפני שממשיכים")
        return results

    results['3. Manager Agent'] = test_3_manager_agent()
    results['4. Property Crew'] = test_4_property_crew_response()
    results['5. Orchestrator'] = test_5_orchestrator_full_flow()
    results['6. Twilio'] = test_6_twilio_credentials()
    results['7. Webhook'] = test_7_webhook_simulation()

    # סיכום
    print("\n" + "="*60)
    print("📊 סיכום בדיקות:")
    print("="*60)

    for test_name, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"   {status} {test_name}")

    failed = [name for name, passed in results.items() if not passed]
    if failed:
        print(f"\n⚠️ בדיקות שנכשלו: {', '.join(failed)}")
        print("   התחל לדבג מהבדיקה הראשונה שנכשלה!")
    else:
        print("\n🎉 כל הבדיקות עברו!")

    return results


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        # הרץ בדיקה ספציפית
        test_num = sys.argv[1]
        tests = {
            "1": test_1_database_connection,
            "2": test_2_openai_connection,
            "3": test_3_manager_agent,
            "4": test_4_property_crew_response,
            "5": test_5_orchestrator_full_flow,
            "6": test_6_twilio_credentials,
            "7": test_7_webhook_simulation,
        }
        if test_num in tests:
            tests[test_num]()
        else:
            print(f"בדיקה {test_num} לא קיימת. בחר 1-7")
    else:
        # הרץ את כל הבדיקות
        run_all_tests()
