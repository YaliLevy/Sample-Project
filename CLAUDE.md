# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Setup & Initialization
```bash
# Install dependencies
pip install -r requirements.txt

# Initialize database with sample data
python database/init_db.py

# Start development server (includes ngrok tunnel)
python main.py
```

### Database Operations
```bash
# Reset database (creates fresh tables + sample data)
python database/init_db.py

# Inspect database directly
sqlite3 storage/database.db
```

### Twilio Configuration
After starting the server, configure Twilio webhook:
1. Copy ngrok URL from terminal output
2. Go to: https://console.twilio.com/us1/develop/sms/settings/whatsapp-sandbox
3. Set "When a message comes in" to: `https://[ngrok-url]/webhook`
4. Send join code to Twilio sandbox number via WhatsApp

## Architecture Overview

### Message Processing Flow

```
WhatsApp Message → Twilio Webhook → Flask (/webhook endpoint)
                                      ↓
                            Returns 200 OK immediately
                                      ↓
                            Background thread spawns
                                      ↓
                        CrewAIOrchestrator.process()
                                      ↓
                    ┌──────────── Manager Agent ────────────┐
                    │    (Intent Classification - 6 types)  │
                    └──────────────────┬────────────────────┘
                                       ↓
        ┌──────────────────────────────┼──────────────────────────────┐
        ↓                              ↓                               ↓
   PropertyCrew                   ClientCrew                    General Handler
   (5 sequential tasks)           (3-4 sequential tasks)        (Direct response)
        ↓                              ↓
   Parser → DB → Photo → Match    Parser → DB → Match → Response
        ↓                              ↓
   Tools: PropertySave, MediaDownload, PropertyMatcher, etc.
        ↓                              ↓
   SQLite Database (Properties, Clients, Matches, Photos)
        ↓
   Response via Twilio REST API (not webhook response)
```

**Critical Design Decision**: Flask webhook ALWAYS returns 200 OK within milliseconds to avoid Twilio's 15-second timeout. Actual CrewAI processing (10-30 seconds) happens in a background thread, with responses sent via Twilio REST API.

### CrewAI Architecture Patterns

#### 1. Orchestrator Pattern
`CrewAIOrchestrator` in `crews/orchestrator.py` is the single entry point:
- Creates Manager Agent for intent classification
- Routes to specialized crews based on intent
- Handles 6 intent types: ADD_PROPERTY, ADD_CLIENT, QUERY_PROPERTY, QUERY_CLIENT, FIND_MATCHES, GENERAL
- All errors caught and converted to friendly Hebrew responses

#### 2. Sequential Task Chaining
Tasks depend on previous task outputs via `context` parameter:
```python
parse_task = Task(description="...", agent=parser)
save_task = Task(description="...", agent=db_agent, context=[parse_task])
match_task = Task(description="...", agent=matcher, context=[save_task])
response_task = Task(..., context=[parse_task, save_task, match_task])
```
Task outputs automatically passed to dependent tasks. No manual state management needed.

#### 3. Agent Temperature Strategy
- **Parsing agents** (temp=0.3): PropertyParser, ClientParser - Need consistent JSON extraction
- **Response agents** (temp=0.7): PropertyResponse, ClientResponse - Need natural conversational tone
- **Classification agents** (temp=0.3): Manager Agent - Need reliable intent detection
- Use `config/llm_config.py` helpers: `get_gpt4o()`, `get_creative_gpt4o()`, `get_deterministic_gpt4o()`

#### 4. No Delegation
All agents set `allow_delegation=False` - each owns its responsibility fully. Coordination happens at Crew/Task level, not agent level.

### Tool System Architecture

All tools extend `BaseTool` from CrewAI and use Pydantic schemas from `tools/schemas.py` for input validation.

**Database Tools** (`tools/database_tool.py`):
- Always use context manager: `with get_session() as session:`
- Return Hebrew-formatted strings (not Python objects) for agent consumption
- Handle None values gracefully: `getattr(obj, 'field', 'N/A')`

**Matching Algorithm** (`tools/matching_tool.py`):
Calculates 0-100 score:
- 30 pts: Transaction type match (must be exact: rent↔rent, sale↔buy)
- 25 pts: Location (exact city=25, same region=15, using REGIONS dict)
- 20 pts: Rooms (in range=20, outside range=-5 per room difference)
- 15 pts: Price (within budget=15, ≤10% over=10, >10% over=-15)
- 10 pts: Size (meets minimum=10, below minimum=proportional)
- **Good match threshold: 65+**

**Media Tools** (`tools/media_tool.py`):
- Photos stored locally: `storage/photos/[user_phone]/[property_id]/`
- Both local path and Twilio URL stored in database
- Batch download for multiple photos

### Database Schema Key Points

**Session Management**: Always use context manager:
```python
from database.connection import get_session
with get_session() as session:
    # Operations here
# Auto-commits on success, rolls back on exception
```

**Multi-user Support**: Properties and Clients both store `phone_number` of who added them.

**Indexing**: Critical fields indexed: price, transaction_type, city, status (on both Property and Client models).

**Relationships**:
- Property ↔ Photos (1-to-many, cascade delete)
- Property ↔ Matches ↔ Client (many-to-many via Match table)
- Match.status lifecycle: suggested → sent → interested → rejected → closed

**Conversation History**: All user/bot messages stored in `Conversation` table for debugging and context.

## Hebrew-Specific Considerations

### Text Parsing Patterns
Parser agents understand:
- **Abbreviations**: חד׳ (rooms), מ״ר (sqm), ת״א (Tel Aviv), ירוש׳ (Jerusalem), ש״ח (shekels)
- **Number formats**: "2 מיליון" → 2000000, "5000 שקל" → 5000
- **Slang**: משופצת (renovated), ממוזגת (air-conditioned), מרווחת (spacious)
- **Transaction types**: "להשכרה" → rent, "למכירה" → sale, "מחפש לקנות" → buy

### Owner Information Extraction
When message contains "בעלים [name] [phone]", parser extracts to `owner_name` and `owner_phone` fields.

### Response Formatting
- Use consistent emoji set: 🏠📍🛏️💰📸✨🔍📝
- Keep responses under 1500 chars (WhatsApp best practice)
- Auto-split long responses into 1600-char chunks in `twilio_handler.py`

## Configuration & Environment

**Required Environment Variables** (`.env`):
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER` - WhatsApp integration
- `OPENAI_API_KEY` - GPT-4o access (must support Hebrew well)
- `DATABASE_URL` - Default: `sqlite:///storage/database.db`
- `FLASK_SECRET_KEY` - Session security
- `NGROK_AUTH_TOKEN` - Optional, for automatic tunnel

**Critical**: All credentials validated on startup in `config/settings.py`. Server won't start if missing.

## Important Conventions

### Agent Creation Pattern
Functions named `create_[type]_[function]_agent()` in `agents/` directories, always return `Agent` instance.

### Tool Naming
Tool descriptions in Hebrew verb form: "שמירת נכס במאגר" (Save property to database), "חיפוש נכסים לפי קריטריונים" (Search properties by criteria).

### Error Handling
- Webhook endpoint NEVER raises exceptions (always returns 200)
- Background processing catches all exceptions, sends friendly Hebrew error message
- Tools return error strings in Hebrew, not exceptions

### Adding New Intent Types
1. Add to Manager Agent's instructions in `agents/manager/manager_agent.py`
2. Add case in `orchestrator.py`'s `process()` method
3. Create new crew method or add to existing crew
4. Test with real Hebrew messages

### Adding New Tools
1. Create tool class extending `BaseTool` in `tools/`
2. Add Pydantic input schema to `tools/schemas.py`
3. Import and pass to agent in `agents/[type]/[agent].py`
4. Reference in task description using Hebrew name

## Testing & Debugging

### Logs
- All logging configured in `config/settings.py` (default: INFO level)
- Set `LOG_LEVEL=DEBUG` in `.env` for verbose output
- Background processing logs appear in server console

### Testing WhatsApp Flow
1. Start server: `python main.py`
2. Note ngrok URL from output
3. Configure Twilio webhook
4. Send test message: "שלום" (should get greeting)
5. Test property add: "דירה 3 חדרים בתל אביב 5000 שקל"
6. Check database: `sqlite3 storage/database.db` → `SELECT * FROM properties;`

### Common Issues
- **Bot not responding**: Check ngrok tunnel at http://localhost:4040, verify webhook URL in Twilio console
- **OpenAI rate limits**: Wait between messages, system auto-retries but may fail under sustained load
- **Photo download fails**: Check write permissions for `storage/photos/`, verify Twilio auth in `.env`
- **Processing timeout**: Background threads handle long operations; check server logs for actual errors

## Extending the System

### Adding a New Agent Type
Follow existing pattern in `agents/` - create directory with agent creation functions, pass necessary tools, set appropriate temperature.

### Adding a New Crew
1. Create in `crews/` directory, extend base pattern
2. Define sequential tasks with context dependencies
3. Register in `orchestrator.py`
4. Add corresponding intent to Manager Agent

### Supabase Configuration (Current Setup)

**Database:** PostgreSQL on Supabase (Frankfurt region)
**Storage:** Supabase Storage bucket `property-photos` (public)

#### Environment Variables Required:
```bash
DATABASE_URL=postgresql+psycopg://postgres:[PASSWORD]@db.[PROJECT-ID].supabase.co:5432/postgres
SUPABASE_URL=https://[PROJECT-ID].supabase.co
SUPABASE_KEY=[ANON-PUBLIC-KEY]
SUPABASE_STORAGE_BUCKET=property-photos
```

#### Database Setup:
- Tables created via SQL script: `database/supabase_setup.sql`
- Run in Supabase SQL Editor if tables need recreation
- All indexes and triggers configured automatically

#### Photo Storage:
- Photos uploaded to Supabase Storage (not local filesystem)
- Structure: `user_[phone]/property_[id]/[uuid]_[timestamp].jpg`
- Public URLs stored in `photos.file_path` column
- Bucket is public (read-only) - anyone with URL can view
- Only bot can upload/delete (via RLS policies)

#### Migration from SQLite:
If migrating existing SQLite data:
1. Export data: `sqlite3 storage/database.db .dump > backup.sql`
2. Manually migrate data or recreate test data
3. Photos need to be re-uploaded from local to Supabase Storage

## Supabase Skill (Advanced Operations)

**Location:** `skills/` directory

The Supabase Skill provides advanced database operations, analytics, and reporting beyond the standard bot functionality.

### Features:
1. **Direct SQL Queries** - Execute parameterized SQL safely
2. **Property Analytics** - Statistics by city, type, price ranges
3. **Client Analytics** - Budget distribution, location preferences
4. **Match Analytics** - Conversion rates, success metrics
5. **Report Generation** - Formatted markdown reports
6. **Storage Management** - Photo statistics, cleanup operations

### CLI Usage:
```bash
# Property analytics
python skills/cli.py analytics properties "תל אביב"

# Generate monthly report
python skills/cli.py report monthly

# Custom SQL query
python skills/cli.py sql "SELECT city, COUNT(*) FROM properties GROUP BY city"

# Storage stats
python skills/cli.py storage
```

### Python Usage:
```python
from skills import execute_sql, get_analytics, generate_report

# Get analytics
analytics = get_analytics("properties", city="תל אביב", days=30)

# Generate report
report = generate_report("monthly")

# Custom SQL
results = execute_sql("SELECT * FROM properties WHERE rooms >= :rooms", {"rooms": 3})
```

### Integration with Bot:
The skill is designed for admin/analytics use cases, not real-time WhatsApp interactions. Use it for:
- Generating daily/weekly/monthly reports
- Analyzing bot performance
- Debugging data issues
- Custom queries and exports

See `skills/README.md` for full documentation.

### Production Deployment
- Database: Already on Supabase (production-ready)
- Photos: Already on Supabase Storage (CDN-backed)
- Set `FLASK_ENV=production`, `FLASK_DEBUG=False`
- Use production WSGI server: `gunicorn -w 4 -b 0.0.0.0:5000 bot.twilio_handler:app`
- Configure permanent Twilio webhook (not ngrok)
- Supabase handles backups, scaling, and monitoring automatically
