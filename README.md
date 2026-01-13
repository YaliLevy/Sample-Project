# WhatsApp Real Estate Bot - CrewAI + Twilio

A smart Hebrew-speaking WhatsApp bot for managing real estate properties and clients, powered by CrewAI multi-agent orchestration.

## Features

- **Property Management** - Add properties via natural Hebrew text, automatically parsed and stored
- **Photo Upload** - Send photos directly from WhatsApp, automatically downloaded and linked to properties
- **Client Management** - Register clients with their search requirements
- **Smart Matching** - Algorithm that finds perfect matches between properties and clients
- **Hebrew Search** - Search properties and clients in natural Hebrew
- **Natural Language** - Understands Hebrew slang, abbreviations, and colloquial speech

## Architecture

```
WhatsApp → Twilio → Flask Webhook → CrewAI Orchestrator
                         ↓ (async processing)
                   Background Thread
                         ↓
         ┌───────────────┼───────────────┐
         ↓               ↓               ↓
 Property Crew    Client Crew    Manager Agent
 (5 agents)       (4 agents)     (classifier)
         ↓               ↓
 Tools: Database, Media, Matching, WhatsApp
         ↓
 SQLite Database (Properties, Clients, Matches, Photos)
         ↓
 Response via Twilio API
```

### Key Components

#### Agents
- **Manager Agent** - Classifies intent (add property, add client, search, match)
- **Parser Agents** - Parse Hebrew text into structured data (JSON)
- **DB Agents** - Handle CRUD operations with database tools
- **Photo Agent** - Downloads and manages photos from WhatsApp/Twilio
- **Matcher Agent** - Calculates match scores between properties and clients
- **Response Agents** - Generate friendly Hebrew responses

#### Tools
- `PropertySaveTool` - Save new properties
- `PropertyGetByIdTool` - Fetch specific property with full details
- `PropertyQueryTool` - Search properties with filters
- `PropertyUpdateTool` - Update property status/details
- `ClientSaveTool` - Save new clients
- `ClientQueryTool` - Search clients
- `MediaDownloadTool` - Download photos from Twilio
- `PropertyMatcherTool` - Find properties matching client criteria
- `ClientMatcherTool` - Find clients matching property

## Requirements

- Python 3.11+
- Twilio account with WhatsApp Sandbox
- OpenAI API key (for GPT-4o)
- ngrok (for local development)

## Installation

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Create a `.env` file (copy from `.env.example`):

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

# ngrok (optional)
NGROK_AUTH_TOKEN=your_ngrok_token

# Logging
LOG_LEVEL=INFO
```

### 3. Initialize the database

```bash
python database/init_db.py
```

This creates:
- All required tables
- Sample test data in Hebrew (3 properties, 3 clients, 3 matches)

### 4. Start the server

```bash
python main.py
```

The server will start in development mode with automatic ngrok tunnel.

## Twilio WhatsApp Sandbox Setup

1. **Go to Twilio Console**:
   https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox

2. **Configure Webhook**:
   - In "When a message comes in" field
   - Paste the ngrok webhook URL (e.g., `https://abc123.ngrok.io/webhook`)
   - Click "Save"

3. **Connect to Sandbox**:
   - Send a WhatsApp message to the Twilio Sandbox number
   - Send the join code shown in the console
   - You'll receive: "You are all set!"

4. **Test**:
   - Send: "שלום" (Hello)
   - You should receive a response from the bot!

## Usage Examples

### Adding a Property

```
דירה 3 חדרים בתל אביב רחוב דיזנגוף 102 קומה 2
75 מטר משופצת וממוזגת
5000 שקל להשכרה
בעלים: יוסי כהן 053-4439430
```

You can also attach photos! Just send 1-5 images with the message.

**Response:**
```
מעולה! 🏠 שמרתי את הנכס:

📍 דיזנגוף 102, תל אביב
🛏️ 3 חדרים | 📐 75 מ״ר
💰 5,000 ₪ לחודש
📸 3 תמונות נשמרו

מספר נכס: #42

מצאתי לקוח שמתאים! יניב מחפש 2-3 חדרים עד 6000₪.
```

### Adding a Client

```
לקוח חדש דני לוי 050-2223344
מחפש 3 חדרים עד 7000 שקל
בצפון תל אביב
```

### Querying Properties

```
תראה לי נכסים בדיזנגוף
```

or

```
תראה לי נכס מספר 5
```

### Finding Matches

```
מה מתאים לדני לוי?
```

or

```
תמצא לקוחות לנכס בדיזנגוף 102
```

## Matching Algorithm

The bot calculates a match score (0-100) based on:

| Criterion | Weight | Details |
|-----------|--------|---------|
| **Transaction Type** | 30 points | Must match (rent ↔ rent, sale ↔ buy) |
| **Location** | 25 points | Exact city (25) or same area (15) |
| **Rooms** | 20 points | In range (20) or close (minus 5 per room difference) |
| **Price** | 15 points | Within budget (15), up to 10% over (10), more (minus) |
| **Size** | 10 points | Above minimum (10) or proportional |

**Good match threshold:** 65+ points

## Project Structure

```
real_estate_bot/
├── config/                 # Configuration
│   ├── settings.py         # Environment variables
│   └── llm_config.py       # GPT-4o configuration
│
├── database/               # Database layer
│   ├── models.py           # SQLAlchemy models
│   ├── connection.py       # Database connection
│   └── init_db.py          # Initialize & seed data
│
├── tools/                  # Agent tools
│   ├── database_tool.py    # CRUD operations
│   ├── media_tool.py       # Photo download from Twilio
│   ├── whatsapp_tool.py    # Send messages
│   ├── matching_tool.py    # Matching algorithm
│   ├── schemas.py          # Pydantic input schemas
│   └── search_tool.py      # Hebrew search
│
├── agents/                 # AI agents
│   ├── manager/            # Manager agent (routing)
│   ├── property/           # Property agents (parser, db, photo, response)
│   └── client/             # Client agents (parser, db, matcher, response)
│
├── crews/                  # Workflow orchestration
│   ├── property_crew.py    # Property workflow (5 tasks)
│   ├── client_crew.py      # Client workflow (4 tasks)
│   └── orchestrator.py     # Main router & intent classifier
│
├── bot/                    # Flask webhook
│   ├── twilio_handler.py   # Async webhook endpoint
│   └── conversation_state.py # Conversation history
│
├── storage/                # Storage
│   ├── photos/             # Property photos
│   └── database.db         # SQLite database
│
├── main.py                 # Entry point
├── ngrok_setup.py          # ngrok helper
└── requirements.txt        # Python dependencies
```

## Technical Details

### Async Processing

The bot uses background threading to handle Twilio's 15-second webhook timeout:

1. Webhook receives message → returns `200 OK` immediately
2. Background thread processes message with CrewAI agents
3. Response sent via Twilio REST API (not webhook response)

This allows unlimited processing time without Twilio timeout errors.

### Hebrew Text Parsing

The parser agent understands:
- **Abbreviations**: חד׳ (rooms), מ״ר (sqm), ת״א (Tel Aviv)
- **Numbers**: "2 מיליון" → 2000000, "5000 שקל" → 5000
- **Slang**: משופצת (renovated), ממוזגת (air-conditioned)
- **Transaction types**: "להשכרה" → rent, "למכירה" → sale

### Owner Information Extraction

When a message contains owner details:
```
בעלים משה כהן 0541234567
```
The parser extracts:
- `owner_name`: "משה כהן"
- `owner_phone`: "0541234567"

### Property Details

When querying a specific property by ID, the bot returns full details:
- Property type, address, city
- Rooms, size, floor
- Price and transaction type
- Owner name and phone
- Description
- Photo count
- Creation date

## Troubleshooting

### Bot not responding to messages

1. Check ngrok is running: http://localhost:4040
2. Verify webhook is set correctly in Twilio Console
3. Check logs in terminal running `python main.py`

### Twilio Authentication Error

- Verify `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` in `.env`
- Make sure you sent the join code to the Sandbox

### OpenAI Rate Limit (429 Error)

- Wait a few seconds between messages
- Consider upgrading your OpenAI plan for higher TPM limits
- The system auto-retries, but may fail on sustained load

### Photos not downloading

- Check write permissions for `storage/photos/`
- Check logs for Twilio authentication errors

### Processing takes too long

- CrewAI workflows can take 10-30 seconds
- This is handled by async processing
- Check logs to identify bottlenecks

## Performance

**Estimated response times:**
- Intent classification: 2-3 seconds
- Add property (no photos): 10-15 seconds
- Add property (with photos): 16-20 seconds
- Add client + find matches: 15-20 seconds
- Search query: 5-8 seconds

**API Usage:**
- Each workflow uses 4-6 OpenAI API calls
- Estimated cost: ~$0.02-0.05 per message (varies by length)

## Production Deployment

For production (without ngrok):

1. **Deploy to server** (Heroku, AWS, GCP, etc.)

2. **Set environment variables**:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
```

3. **Configure permanent webhook in Twilio**:
   - Use your production URL instead of ngrok
   - Example: `https://your-domain.com/webhook`

4. **Use production WSGI server**:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 bot.twilio_handler:app
```

5. **Consider PostgreSQL** instead of SQLite for better performance

## Future Improvements

- [ ] **Optimize agent architecture** - Reduce API calls (currently 4-6 per message)
- [ ] **Intent classification without LLM** - Use regex/keywords for common patterns
- [ ] **Caching** - Cache common responses
- [ ] **Cheaper models** - Use GPT-3.5 or Claude Haiku for simple tasks
- [ ] **Calendar Crew** - Schedule viewings with Google Calendar
- [ ] **Background tasks** - Celery for async processing
- [ ] **Admin Dashboard** - Web management interface
- [ ] **Analytics** - Track matches and conversions
- [ ] **Multi-language** - English and Arabic support
- [ ] **Voice messages** - Transcribe voice messages

## License

MIT License - Free to use

## Contributing

Pull requests are welcome!

## Tips

1. **Supported abbreviations**: חד׳, מ״ר, ת״א, ירוש׳, ק״ג, ש״ח, מיל׳
2. **Flexible formats**: Bot understands "2 מיליון", "2,000,000", "2000000"
3. **Areas**: Bot recognizes areas (גוש דן, צפון ת״א, etc.)
4. **Photos**: Up to 5 photos per property
5. **History**: All conversations are saved for tracking

## Support

Having issues? Open a GitHub issue or send a message.

---

**Built with CrewAI, Twilio, and GPT-4o**
