# 🚀 התחלה מהירה - בוט WhatsApp לנדל"ן

## התקנה מהירה (5 דקות)

### 1. הורד את הקוד
```bash
cd "c:\Users\Galia\Desktop\Sample Project"
```

### 2. צור סביבה וירטואלית
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux
```

### 3. התקן תלויות
```bash
pip install -r requirements.txt
```

### 4. הגדר משתני סביבה

צור קובץ `.env` (העתק מ `.env.example`):

```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux
```

**ערוך את `.env` ומלא:**
```
TWILIO_ACCOUNT_SID=AC...    # מ-Twilio Console
TWILIO_AUTH_TOKEN=...       # מ-Twilio Console
OPENAI_API_KEY=sk-...       # מ-OpenAI
```

### 5. הרץ!
```bash
python main.py
```

זהו! השרת רץ ב-http://localhost:5000

ngrok פתח אוטומטית - תעתיק את ה-webhook URL שהודפס.

---

## הגדרת Twilio (פעם אחת)

### שלב 1: צור חשבון Twilio (חינם)
1. https://www.twilio.com/try-twilio
2. אמת מספר טלפון

### שלב 2: WhatsApp Sandbox
1. https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
2. תעתיק את מספר Sandbox (משהו כמו: +1 415 523 8886)
3. תעתיק את קוד ה-join

### שלב 3: הגדר Webhook
1. באותו עמוד של Sandbox
2. "When a message comes in" → הדבק את ה-webhook URL מ-ngrok
   - דוגמה: `https://abc123.ngrok.io/webhook`
3. שמור

### שלב 4: התחבר ל-Sandbox
1. פתח WhatsApp
2. שלח הודעה למספר Sandbox
3. שלח את קוד ה-join שהעתקת (משהו כמו: `join happy-cat`)
4. תקבל: "You are all set!"

---

## בדיקה מהירה

שלח ב-WhatsApp:

```
שלום
```

אמור לקבל:
```
שלום! 👋 אני עוזר חכם לניהול נדל"ן...
```

---

## דוגמה מלאה

**1. הוסף נכס:**
```
דירה 3 חדרים בתל אביב דיזנגוף 102
5000 שקל להשכרה
```

**2. הוסף לקוח:**
```
לקוח חדש יניב מחפש 2-3 חדרים עד 6000 בת״א
```

**3. קבל התאמות:**
הבוט אוטומטית יציג שיניב מתאים לדירה בדיזנגוף! ✨

---

## בעיות נפוצות

### הבוט לא מגיב
- ✅ בדוק ש-ngrok רץ: http://localhost:4040
- ✅ בדוק ש-webhook מוגדר נכון ב-Twilio
- ✅ בדוק שיש ב-.env את כל המפתחות

### שגיאת "Configuration Error"
- ✅ יצרת `.env` file?
- ✅ מילאת `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `OPENAI_API_KEY`?

### "You are not authorized"
- ✅ שלחת את קוד ה-join ל-Sandbox?
- ✅ מהמספר הנכון?

---

## מה הלאה?

📖 קרא את [README.md](README.md) המלא לפרטים נוספים

🎯 נסה תכונות מתקדמות:
- שלח תמונות עם הנכס
- חפש התאמות: "מה מתאים ליניב"
- חפש נכסים: "תראה לי 3 חדרים עד 6000"

🔧 התאם אישית:
- שנה templates ב-agents
- הוסף שדות למאגר
- שנה ציוני התאמה

---

**יש לך שאלות? פתח issue ב-GitHub!**
