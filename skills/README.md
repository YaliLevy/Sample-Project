# Supabase Skills for WhatsApp Real Estate Bot

Advanced database operations, analytics, and reporting capabilities for the bot.

## Features

### 1. SQL Query Execution
Execute safe, parameterized SQL queries directly on the Supabase PostgreSQL database.

```python
from skills import execute_sql

# Simple query
results = execute_sql("SELECT * FROM properties WHERE city = :city", {"city": "תל אביב"})

# Aggregate query
results = execute_sql("""
    SELECT city, COUNT(*) as count, AVG(price) as avg_price
    FROM properties
    GROUP BY city
    ORDER BY count DESC
""")
```

### 2. Property Analytics
Get comprehensive statistics about properties.

```python
from skills import get_analytics

# All properties
analytics = get_analytics("properties")

# Specific city
analytics = get_analytics("properties", city="תל אביב", days=30)
```

**Returns:**
- Counts by transaction type (rent/sale)
- Average/min/max prices
- Top cities
- Status distribution
- Daily new listings

### 3. Client Analytics
Understand client behavior and preferences.

```python
analytics = get_analytics("clients", days=30)
```

**Returns:**
- Clients by type (rent/buy)
- Popular cities
- Budget distribution
- Active client counts

### 4. Match Analytics
Analyze matching performance and conversion rates.

```python
analytics = get_analytics("matches", days=30)
```

**Returns:**
- Total matches created
- Average match scores
- Status distribution (suggested/interested/closed)
- Conversion rates at each stage

### 5. Report Generation
Generate formatted markdown reports.

```python
from skills import generate_report

# Property report
report = generate_report("properties", city="תל אביב", days=30)
print(report)

# Monthly comprehensive report
report = generate_report("monthly")
```

### 6. Storage Management
Manage Supabase Storage and photos.

```python
from skills import get_storage_info

stats = get_storage_info()
# Returns: bucket info, file counts, sample files
```

## CLI Usage

Use the command-line interface for quick analytics:

```bash
# Property analytics
python skills/cli.py analytics properties

# Property analytics for specific city
python skills/cli.py analytics properties "תל אביב"

# Client analytics
python skills/cli.py analytics clients

# Match analytics
python skills/cli.py analytics matches

# Generate monthly report
python skills/cli.py report monthly

# Execute custom SQL
python skills/cli.py sql "SELECT * FROM properties WHERE rooms >= 3 LIMIT 10"

# Get storage stats
python skills/cli.py storage

# Top performing properties
python skills/cli.py performance 10

# Client satisfaction
python skills/cli.py satisfaction 10
```

## Using with Claude Code

The skill is automatically available to Claude Code. You can ask:

- "Show me property analytics for Tel Aviv"
- "Generate a monthly report"
- "What's the average price for 3-room apartments?"
- "Which properties have the most matches?"
- "Run SQL: SELECT city, COUNT(*) FROM properties GROUP BY city"
- "Show storage statistics"

## Advanced Usage

### Direct Skill Instance

```python
from skills.supabase_skill import skill

# Get top performing properties
performance = skill.get_property_performance(limit=10)

# Get client satisfaction
satisfaction = skill.get_client_satisfaction(limit=10)

# Get photos for a property
photos = skill.get_property_photos(property_id=42)

# Cleanup orphaned photos
cleanup_stats = skill.cleanup_orphaned_photos()
```

### Custom Reports

```python
# Property report with filters
report = skill.generate_report("properties", city="תל אביב", days=7)

# Client report
report = skill.generate_report("clients", days=14)

# Match report
report = skill.generate_report("matches", days=30)

# Full monthly report
report = skill.generate_report("monthly")
```

## Safety & Best Practices

1. **SQL Queries**: Always use parameterized queries to prevent SQL injection
   ```python
   # Good
   execute_sql("SELECT * FROM properties WHERE city = :city", {"city": user_input})

   # Bad
   execute_sql(f"SELECT * FROM properties WHERE city = '{user_input}'")
   ```

2. **Read-Only Mode**: By default, only SELECT queries are allowed. To execute write operations:
   ```python
   skill.execute_sql_query("UPDATE properties SET status = :status WHERE id = :id",
                           {"status": "sold", "id": 42},
                           read_only=False)
   ```

3. **Error Handling**: All functions return errors in result dictionaries:
   ```python
   result = get_analytics("properties")
   if "error" in result:
       print(f"Error occurred: {result['error']}")
   ```

## Configuration

Make sure these environment variables are set in `.env`:

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
DATABASE_URL=postgresql+psycopg://postgres:password@db.your-project.supabase.co:5432/postgres
SUPABASE_STORAGE_BUCKET=property-photos
```

## Examples

### Example 1: Daily Property Report

```python
from skills import generate_report

# Generate report for last 7 days
report = generate_report("properties", days=7)
print(report)
```

Output:
```markdown
# Property Report (7 days)

## By Transaction Type
- **RENT**: 23 properties, Avg: 5,200 ₪, Range: 3,000-8,500 ₪
- **SALE**: 8 properties, Avg: 1,850,000 ₪, Range: 980,000-3,200,000 ₪

## Top Cities
- **תל אביב**: 15 properties, Avg: 6,100 ₪
- **ירושלים**: 8 properties, Avg: 4,800 ₪
...
```

### Example 2: Find Best Properties

```python
from skills.supabase_skill import skill

# Get properties with most matches
top_props = skill.get_property_performance(limit=5)

for prop in top_props:
    print(f"Property #{prop['id']}: {prop['city']}, {prop['street']}")
    print(f"  Matches: {prop['match_count']}, Avg Score: {prop['avg_score']:.1f}")
    print(f"  Interested: {prop['interested_count']}, Closed: {prop['closed_count']}")
```

### Example 3: Custom SQL Analysis

```python
from skills import execute_sql

# Find properties with no matches
query = """
    SELECT p.id, p.city, p.street, p.price
    FROM properties p
    LEFT JOIN matches m ON p.id = m.property_id
    WHERE m.id IS NULL AND p.status = 'available'
    ORDER BY p.created_at DESC
    LIMIT 10
"""

no_matches = execute_sql(query)
for prop in no_matches:
    print(f"Property #{prop['id']}: {prop['city']}, {prop['street']} - {prop['price']:,} ₪")
```

## Troubleshooting

### Connection Issues

If you get connection errors:
1. Check `.env` file has correct Supabase credentials
2. Verify network connectivity (may not work from restricted networks)
3. Check Supabase project is active and healthy

### Permission Errors

If SQL queries fail:
1. Ensure the anon key has sufficient permissions
2. Check RLS (Row Level Security) policies in Supabase
3. Consider using service_role key for admin operations (in `.env` only!)

### Performance

For large datasets:
- Add `LIMIT` clauses to queries
- Use date filters to reduce result sets
- Consider indexing frequently queried columns

## Contributing

To add new analytics or reports:

1. Add method to `SupabaseSkill` class in `supabase_skill.py`
2. Add CLI command in `cli.py`
3. Update this README with usage examples
4. Test thoroughly with sample data

---

**Built for WhatsApp Real Estate Bot** | Powered by Supabase & PostgreSQL
