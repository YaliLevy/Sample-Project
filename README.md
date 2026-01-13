# 🏠 בוט WhatsApp לניהול נדל"ן - CrewAI + Twilio

בוט חכם בעברית לניהול נכסים ולקוחות דרך WhatsApp, משתמש ב-CrewAI לתיאום מספר AI agents שעובדים ביחד.

## ✨ תכונות

- **הוספת נכסים** - שלח פרטי נכס בעברית טבעית והבוט יפרק ויישמור במאגר
- **העלאת תמונות** - שלח תמונות ישירות מ-WhatsApp, הבוט יוריד ויקשר לנכס
- **ניהול לקוחות** - רשום לקוחות עם דרישות חיפוש
- **התאמה אוטומטית** - אלגוריתם חכם למציאת התאמות מושלמות בין נכסים ללקוחות
- **חיפוש** - חפש נכסים ולקוחות בעברית
- **שפה טבעית** - הבוט מבין עברית דיבורית, קיצורים (חד׳, מ״ר, ת״א) וסלנג

## 🏗️ ארכיטקטורה

```
WhatsApp → Twilio → Flask Webhook → CrewAI Orchestrator
                                            ↓
                            ┌───────────────┼───────────────┐
                            ↓               ↓               ↓
                    Property Crew    Client Crew    Manager Agent
                    (4 agents)       (4 agents)     (classifier)
                            ↓               ↓
                    Tools: Database, Media, Matching, WhatsApp
                            ↓
                    SQLite Database (Properties, Clients, Matches, Photos)
```

### Agents:
- **Manager Agent** - מזהה כוונות (add property, add client, search, match)
- **Parser Agents** - מפרקים טקסט עברית לנתונים מובנים
- **DB Agents** - מבצעים פעולות CRUD במאגר
- **Photo Agent** - מוריד ומנהל תמונות מ-WhatsApp
- **Matcher Agent** - מחשב ציוני התאמה בין נכסים ללקוחות
- **Response Agents** - כותבים תשובות ידידותיות בעברית

## 📋 דרישות

- Python 3.11+
- חשבון Twilio עם WhatsApp Sandbox
- OpenAI API key (ל-GPT-4o)
- ngrok (לפיתוח מקומי)

## 🚀 התקנה

### 1. התקן תלויות

```bash
pip install -r requirements.txt
```

### 2. הגדר משתני סביבה

צור קובץ `.env` (העתק מ `.env.example`):

```bash
# Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Database
DATABASE_URL=sqlite:///storage/database.db

# Flask
FLASK_ENV=development
FLASK_SECRET_KEY=your_random_secret_key
FLASK_DEBUG=True

# ngrok (אופציונלי)
NGROK_AUTH_TOKEN=your_ngrok_token

# Logging
LOG_LEVEL=INFO
```

### 3. אתחל את מאגר הנתונים

```bash
python database/init_db.py
```

זה ייצור:
- את כל הטבלאות הנדרשות
- נתוני בדיקה בעברית (3 נכסים, 3 לקוחות, 3 התאמות)

### 4. הפעל את השרת

```bash
python main.py
```

השרת יתחיל ב-development mode עם ngrok אוטומטי.

## 🔧 הגדרת Twilio WhatsApp Sandbox

1. **היכנס ל-Twilio Console**:
   https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox

2. **הגדר Webhook**:
   - בשדה "When a message comes in":
   - הדבק את ה-webhook URL ש-ngrok הדפיס (משהו כמו: `https://abc123.ngrok.io/webhook`)
   - לחץ "Save"

3. **התחבר ל-Sandbox**:
   - שלח הודעה WhatsApp למספר Sandbox של Twilio
   - שלח את קוד ה-join שמופיע בקונסול
   - תקבל אישור: "You are all set!"

4. **בדוק**:
   - שלח: "שלום"
   - אמור לקבל תשובה מהבוט!

## 📱 דוגמאות שימוש

### הוספת נכס

```
דירה 3 חדרים בתל אביב רחוב דיזנגוף 102 קומה 2
75 מטר משופצת וממוזגת
5000 שקל להשכרה
בעלים: יוסי כהן 053-4439430
```

אפשר גם לשלוח עם תמונות! פשוט תצרף 1-5 תמונות להודעה.

**תשובה:**
```
מעולה! 🏠 שמרתי את הנכס:

📍 דיזנגוף 102, תל אביב
🛏️ 3 חדרים | 📐 75 מ״ר
💰 5,000 ₪ לחודש
📸 3 תמונות נשמרו

מספר נכס: #42

מצאתי לקוח שמתאים! יניב מחפש 2-3 חדרים עד 6000₪.
רוצה שאשלח את הפרטים?
```

### הוספת לקוח

```
לקוח חדש דני לוי 050-2223344
מחפש 3 חדרים עד 7000 שקל
בצפון תל אביב
```

**תשובה:**
```
רשמתי את דני לוי! 📝

🔍 מחפש: 3 חדרים | עד 7,000₪ | צפון ת״א | שכירות

מספר לקוח: #5

מצאתי 2 נכסים מתאימים:

🏠 ארלוזורוב 55 - 3 חד׳ | 6,800₪ (התאמה 95%)
   ✓ עיר מדויקת | ✓ בתקציב | ✓ מספר חדרים מתאים

🏠 דיזנגוף 200 - 3 חד׳ | 7,200₪ (התאמה 80%)
   ✓ עיר מדויקת | ⚠ מעל תקציב ב-3%

רוצה לתאם סיור?
```

### חיפוש נכסים

```
תראה לי נכסים בדיזנגוף
```

או

```
חפש 3 חדרים עד 6000 בתל אביב
```

### מציאת התאמות

```
מה מתאים לדני לוי?
```

או

```
תמצא לקוחות לנכס בדיזנגוף 102
```

### עזרה

```
עזרה
```

או

```
שלום
```

## 🎯 אלגוריתם ההתאמה

הבוט מחשב ציון התאמה (0-100) לפי:

| קריטריון | משקל | פירוט |
|----------|------|-------|
| **סוג עסקה** | 30 נקודות | חייב להתאים (rent ↔ rent, sale ↔ buy) |
| **מיקום** | 25 נקודות | עיר מדויקת (25) או אותו אזור (15) |
| **חדרים** | 20 נקודות | בטווח (20) או קרוב (מינוס 5 לכל חדר הפרש) |
| **מחיר** | 15 נקודות | בתקציב (15), עד 10% מעל (10), יותר (מינוס) |
| **גודל** | 10 נקודות | מעל מינימום (10) או מתחת (יחסי) |

**סף התאמה טובה:** 65+ נקודות

**דוגמה:**
- לקוח: 3 חדרים, עד 7000₪, תל אביב
- נכס: 3 חדרים, 6800₪, תל אביב
- ציון: **95** (התאמה מצוינת! ✨)

## 📂 מבנה הפרויקט

```
real_estate_bot/
├── config/                 # הגדרות וקונפיגורציה
│   ├── settings.py         # משתני סביבה
│   └── llm_config.py       # GPT-4o configuration
│
├── database/               # מאגר נתונים
│   ├── models.py           # SQLAlchemy models
│   ├── connection.py       # Database connection
│   └── init_db.py          # אתחול ומילוי נתונים
│
├── tools/                  # כלים לשימוש ה-agents
│   ├── database_tool.py    # פעולות CRUD
│   ├── media_tool.py       # הורדת תמונות מ-Twilio
│   ├── whatsapp_tool.py    # שליחת הודעות
│   ├── matching_tool.py    # אלגוריתם התאמה
│   └── search_tool.py      # חיפוש בעברית
│
├── agents/                 # AI agents
│   ├── manager/            # Manager agent (routing)
│   ├── property/           # 4 property agents
│   └── client/             # 4 client agents
│
├── crews/                  # תהליכי עבודה
│   ├── property_crew.py    # Property workflow
│   ├── client_crew.py      # Client workflow
│   └── orchestrator.py     # Main router
│
├── bot/                    # Flask webhook
│   ├── twilio_handler.py   # Webhook endpoint
│   └── conversation_state.py # ניהול היסטוריה
│
├── storage/                # אחסון
│   ├── photos/             # תמונות נכסים
│   └── database.db         # SQLite database
│
├── main.py                 # נקודת כניסה ראשית
├── ngrok_setup.py          # עזר ל-ngrok
└── requirements.txt        # תלויות Python
```

## 🔍 Troubleshooting

### הבוט לא מגיב להודעות

1. בדוק ש-ngrok פועל: http://localhost:4040
2. בדוק ש-webhook מוגדר נכון ב-Twilio Console
3. בדוק logs ב-terminal שבו רץ `python main.py`

### שגיאת Authentication מ-Twilio

וודא ש:
- `TWILIO_ACCOUNT_SID` ו-`TWILIO_AUTH_TOKEN` נכונים ב-.env
- שלחת את קוד ה-join ל-Sandbox

### שגיאת OpenAI API

- בדוק ש-`OPENAI_API_KEY` תקף
- בדוק שיש לך קרדיט ב-OpenAI account

### תמונות לא מורדות

- בדוק שיש הרשאות כתיבה ל-`storage/photos/`
- בדוק את ה-logs - אולי יש שגיאת Authentication מ-Twilio

### הבוט "תקוע" או לא מסיים

- CrewAI לפעמים לוקח זמן (10-30 שניות)
- בדוק logs לזיהוי בעיות
- נסה הודעה פשוטה יותר

## 🧪 בדיקות

### הרץ את אתחול ה-DB עם נתונים לדוגמה:

```bash
python database/init_db.py
```

### בדוק נתונים במאגר:

```python
from database.connection import get_session
from database.models import Property, Client

with get_session() as session:
    properties = session.query(Property).all()
    print(f"Properties: {len(properties)}")

    clients = session.query(Client).all()
    print(f"Clients: {len(clients)}")
```

### בדוק כלי בודד:

```python
from tools.matching_tool import PropertyMatcherTool

matcher = PropertyMatcherTool()
result = matcher._run(client_id=1, limit=5)
print(result)
```

## 🚀 Production Deployment

להרצה ב-production (ללא ngrok):

1. **Deploy לשרת** (Heroku, AWS, GCP, וכו')

2. **הגדר משתני סביבה**:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
```

3. **הגדר webhook קבוע ב-Twilio**:
   - במקום ngrok URL, השתמש ב-production URL שלך
   - דוגמה: `https://your-domain.com/webhook`

4. **השתמש ב-production WSGI server**:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 bot.twilio_handler:app
```

5. **שקול PostgreSQL** במקום SQLite לביצועים טובים יותר

## 📊 סטטיסטיקות ביצועים

**זמני תגובה משוערים:**
- סיווג כוונה (Manager): 2-3 שניות
- הוספת נכס (ללא תמונות): 10-15 שניות
- הוספת נכס (עם 3 תמונות): 16-20 שניות
- הוספת לקוח + התאמות: 15-20 שניות
- חיפוש: 5-8 שניות

**שימוש ב-OpenAI:**
- כל workflow משתמש ב-4-6 קריאות API
- עלות משוערת: ~$0.02-0.05 לכל הודעה (תלוי באורך)

## 🔮 תכונות עתידיות (לא ב-MVP)

- [ ] Calendar Crew - תיאום פגישות עם Google Calendar
- [ ] Background tasks - Celery לעיבוד אסינכרוני
- [ ] Admin Dashboard - ממשק ניהול Web
- [ ] Analytics - מעקב אחרי התאמות והמרות
- [ ] Multi-language - אנגלית וערבית
- [ ] Voice messages - תמלול הודעות קוליות
- [ ] Map integration - חיפוש מבוסס מיקום

## 📝 רישיון

MIT License - חופשי לשימוש

## 🤝 תרומה

Pull requests מתקבלים בברכה!

## 💡 טיפים

1. **קיצורים נתמכים**: חד׳, מ״ר, ת״א, ירוש׳, ק״ג, ש״ח, מיל׳
2. **פורמטים גמישים**: הבוט מבין "2 מיליון", "2,000,000", "2000000"
3. **אזורים**: הבוט מזהה אזורים (גוש דן, צפון ת״א, וכו')
4. **תמונות**: עד 5 תמונות לנכס
5. **היסטוריה**: כל שיחה נשמרת למעקב

## 📞 תמיכה

יש בעיה? פתח issue ב-GitHub או שלח הודעה.

---

**Built with ❤️ using CrewAI, Twilio, and GPT-4o**
