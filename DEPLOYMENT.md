# 🚀 Deployment Guide - Railway

מדריך מלא להעלאת WhatsApp Real Estate Bot ל-Railway.

## ✅ מה כבר מוכן

הפרויקט כבר הוכן ל-Railway עם:
- ✅ `Procfile` - מגדיר איך להריץ את האפליקציה
- ✅ `runtime.txt` - מגדיר Python 3.11
- ✅ `railway.json` - קונפיגורציה מתקדמת
- ✅ `requirements.txt` - כולל gunicorn (production WSGI server)
- ✅ Supabase מוגדר (PostgreSQL + Storage)

**אין צורך ב-ngrok!** Railway נותן לך domain קבוע.

---

## 📋 שלב 1: הכנה

### 1.1 וודא שיש לך:
- ✅ חשבון Railway: https://railway.app
- ✅ GitHub account (מומלץ)
- ✅ Supabase project מוכן
- ✅ Twilio account עם WhatsApp Sandbox
- ✅ OpenAI API key

### 1.2 משתני הסביבה שתצטרך:
```bash
# Twilio
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Supabase
DATABASE_URL=postgresql+psycopg://postgres:PASSWORD@db.PROJECT.supabase.co:5432/postgres
SUPABASE_URL=https://PROJECT.supabase.co
SUPABASE_KEY=eyJhbG...
SUPABASE_STORAGE_BUCKET=property-photos

# Flask (חובה לפרודקשן!)
FLASK_ENV=production
FLASK_SECRET_KEY=<סיסמה-חזקה-רנדומלית>
FLASK_DEBUG=False

# Logging
LOG_LEVEL=INFO
```

---

## 🚂 שלב 2: העלאה ל-Railway

### אופציה A: דרך GitHub (מומלץ)

#### 1. צור Git repository
```bash
cd "c:\Users\Galia\Desktop\Sample Project"
git init
git add .
git commit -m "Initial commit - WhatsApp Real Estate Bot"
```

#### 2. העלה ל-GitHub
```bash
# צור repository ב-GitHub (דרך האתר)
# אחרי שיצרת:
git remote add origin https://github.com/YOUR-USERNAME/whatsapp-real-estate-bot.git
git branch -M main
git push -u origin main
```

#### 3. חבר ל-Railway
1. לך ל: https://railway.app
2. לחץ **"New Project"**
3. בחר **"Deploy from GitHub repo"**
4. חבר את ה-GitHub account שלך
5. בחר את הrepository: `whatsapp-real-estate-bot`
6. Railway יתחיל לעלות אוטומטית!

### אופציה B: דרך Railway CLI

#### 1. התקן Railway CLI
```bash
npm install -g @railway/cli
```

#### 2. התחבר
```bash
railway login
```

#### 3. צור פרויקט והעלה
```bash
cd "c:\Users\Galia\Desktop\Sample Project"
railway init
railway up
```

---

## ⚙️ שלב 3: הגדר משתני סביבה ב-Railway

### 3.1 דרך Dashboard:
1. לך לפרויקט ב-Railway: https://railway.app/dashboard
2. לחץ על השירות שלך (ייקרא בשם הrepo)
3. לחץ על **"Variables"** בתפריט צד
4. לחץ **"+ New Variable"**
5. הוסף **כל אחד** מהמשתנים הבאים:

```
TWILIO_ACCOUNT_SID = AC...
TWILIO_AUTH_TOKEN = ...
TWILIO_WHATSAPP_NUMBER = whatsapp:+14155238886
OPENAI_API_KEY = sk-proj-...
DATABASE_URL = postgresql+psycopg://postgres:PASSWORD@db....supabase.co:5432/postgres
SUPABASE_URL = https://....supabase.co
SUPABASE_KEY = eyJhbG...
SUPABASE_STORAGE_BUCKET = property-photos
FLASK_ENV = production
FLASK_SECRET_KEY = <סיסמה-חזקה-אקראית-כאן>
FLASK_DEBUG = False
LOG_LEVEL = INFO
```

**חשוב:** `FLASK_SECRET_KEY` - צור סיסמה חזקה! אפשר להשתמש ב:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### 3.2 דרך CLI:
```bash
railway variables set TWILIO_ACCOUNT_SID=AC...
railway variables set TWILIO_AUTH_TOKEN=...
# וכן הלאה...
```

---

## 🌐 שלב 4: קבל את ה-URL של Railway

אחרי שהפרויקט deployed:

### דרך Dashboard:
1. לך ל-**Settings** של השירות
2. מצא **"Public Networking"** או **"Domains"**
3. לחץ **"Generate Domain"**
4. תקבל משהו כמו: `https://whatsapp-bot-production.up.railway.app`

### דרך CLI:
```bash
railway domain
```

**שמור את ה-URL הזה!** תצטרך אותו לTwilio.

---

## 📱 שלב 5: הגדר Webhook ב-Twilio

### 5.1 לך ל-Twilio Console:
https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox

### 5.2 עדכן Webhook:
1. בשדה **"When a message comes in"**
2. שים: `https://YOUR-RAILWAY-URL.up.railway.app/webhook`
3. **Method:** POST
4. **Save!**

### 5.3 בדוק שהכל עובד:
1. שלח הודעה ל-WhatsApp Sandbox: `join <code>`
2. שלח: `שלום`
3. הבוט אמור להגיב!

---

## 🔍 שלב 6: בדיקה ו-Debugging

### 6.1 בדוק Logs ב-Railway:
```bash
# דרך CLI
railway logs

# דרך Dashboard
Dashboard → Your Service → "Deployments" → בחר deployment → "View Logs"
```

### 6.2 בדוק שהטבלאות נוצרו:
לך ל-Supabase Dashboard → Table Editor
אמור לראות:
- ✅ properties
- ✅ clients
- ✅ matches
- ✅ photos
- ✅ conversations

### 6.3 בדוק שה-Storage Bucket קיים:
Supabase → Storage → `property-photos`

### 6.4 בדוק את הבוט:
שלח ב-WhatsApp:
```
דירה 3 חדרים בתל אביב דיזנגוף 102
75 מטר קומה 2
5000 שקל להשכרה
בעלים: משה כהן 050-1234567
```

הבוט אמור לענות עם אישור!

---

## 🐛 Troubleshooting

### בעיה: הבוט לא עונה ב-WhatsApp
**פתרון:**
1. בדוק Logs ב-Railway: `railway logs`
2. וודא שה-Webhook URL ב-Twilio נכון
3. בדוק שכל משתני הסביבה מוגדרים ב-Railway

### בעיה: Database connection error
**פתרון:**
1. בדוק את `DATABASE_URL` ב-Railway variables
2. וודא שהפורמט נכון: `postgresql+psycopg://...`
3. בדוק ב-Supabase שהפרויקט פעיל

### בעיה: OpenAI API error
**פתרון:**
1. בדוק שיש לך קרדיט ב-OpenAI account
2. וודא ש-`OPENAI_API_KEY` נכון
3. בדוק rate limits

### בעיה: Application Error / Crash
**פתרון:**
```bash
# ראה logs מפורטים
railway logs --follow

# רסטרט את השירות
railway service restart
```

### בעיה: תמונות לא מועלות
**פתרון:**
1. בדוק את `SUPABASE_KEY` ו-`SUPABASE_URL`
2. וודא שה-bucket `property-photos` קיים ב-Supabase Storage
3. בדוק שה-bucket מוגדר כ-Public
4. ראה logs: `railway logs | grep "photo"`

---

## 📊 Monitoring

### Railway Dashboard:
- **Metrics**: CPU, Memory, Network usage
- **Logs**: Real-time logs
- **Deployments**: History של כל deployment

### Supabase Dashboard:
- **Database**: Size, queries
- **Storage**: File count, size
- **API**: Request count

---

## 🔄 עדכון הבוט (אחרי שינויים בקוד)

### אם משתמש ב-GitHub:
```bash
git add .
git commit -m "Your changes description"
git push origin main
```
Railway יעדכן אוטומטית!

### אם משתמש ב-Railway CLI:
```bash
railway up
```

---

## 💰 עלויות

### Railway (Free Tier):
- ✅ $5 credit/month
- ✅ 500 שעות execution
- ✅ 1GB RAM
- ✅ 1GB storage

**מספיק לפרויקט קטן-בינוני!**

אם צריך יותר:
- **Hobby Plan**: $5/month
- **Pro Plan**: $20/month

### Supabase (Free Tier):
- ✅ 500MB database
- ✅ 1GB storage
- ✅ 2GB bandwidth

---

## ✨ Tips

1. **שמור סיסמאות בבטחה** - אל תcommit את `.env` ל-Git!
2. **גבה את הDB** - Supabase עושה זאת אוטומטית, אבל טוב לבדוק
3. **מוניטור logs** - בדוק מדי פעם שהכל עובד
4. **Restart אוטומטי** - Railway יעשה restart אוטומטי אם יש crash
5. **Custom Domain** - אפשר לחבר domain משלך (דורש Railway Pro)

---

## 🎯 Checklist לפני Go-Live

- [ ] כל משתני הסביבה מוגדרים ב-Railway
- [ ] `FLASK_ENV=production` ו-`FLASK_DEBUG=False`
- [ ] `FLASK_SECRET_KEY` חזק ואקראי
- [ ] Webhook URL מוגדר ב-Twilio
- [ ] טבלאות נוצרו ב-Supabase
- [ ] Storage bucket קיים ו-public
- [ ] בדקת שהבוט עונה ב-WhatsApp
- [ ] לא נותר קוד ngrok (הוסר!)
- [ ] Logs נראים תקינים
- [ ] יש credit ב-OpenAI account

---

## 📞 תמיכה

אם יש בעיות:
1. בדוק את ה-logs ב-Railway
2. בדוק את [CLAUDE.md](CLAUDE.md) למידע טכני
3. בדוק את [README.md](README.md) למבנה הפרויקט

---

**בהצלחה! 🚀**

הבוט שלך מוכן לעבוד בפרודקשן!
