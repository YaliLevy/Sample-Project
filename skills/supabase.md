# Supabase Real Estate Management Skill

This skill provides advanced Supabase database operations for the WhatsApp Real Estate Bot.

## Capabilities

### 1. Direct SQL Queries
Execute custom SQL queries on the Supabase PostgreSQL database for advanced operations.

### 2. Property Analytics
- Total properties by city, type, transaction type
- Average prices, room counts
- Properties added per day/week/month
- Status distribution (available/rented/sold)

### 3. Client Analytics
- Active clients by search criteria
- Budget distribution
- Location preferences
- Match success rates

### 4. Match Analytics
- Top performing properties (most matches)
- Client satisfaction (match scores)
- Conversion rates (suggested → interested → closed)

### 5. Storage Management
- List all photos for a property
- Get storage usage statistics
- Clean up orphaned photos
- Generate public URLs

## Usage

When you need to perform advanced database operations, use this skill with commands like:

- "Show me analytics for properties in Tel Aviv"
- "What's the average price for 3-room apartments?"
- "Which properties have the most client matches?"
- "Generate a monthly report of new listings"
- "Clean up unused photos from storage"
- "Run SQL: SELECT city, COUNT(*) FROM properties GROUP BY city"

## Configuration

Required environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_KEY`: Your Supabase anon/service key
- `DATABASE_URL`: PostgreSQL connection string

## Examples

### Example 1: Property Analytics by City
```
User: "Show property statistics by city"
Skill: Queries database and returns:
- Tel Aviv: 45 properties (30 rent, 15 sale), avg price: 6,200 ₪
- Jerusalem: 23 properties (18 rent, 5 sale), avg price: 5,500 ₪
- Haifa: 12 properties (10 rent, 2 sale), avg price: 4,800 ₪
```

### Example 2: Match Success Report
```
User: "Which properties are most popular with clients?"
Skill: Returns properties with:
- Property ID, address, room count
- Number of matches generated
- Average match score
- Conversion rate (matches → interested)
```

### Example 3: Custom SQL Query
```
User: "Run SQL: SELECT * FROM properties WHERE rooms >= 3 AND price < 7000"
Skill: Executes query safely and returns formatted results
```

## Safety

- All SQL queries are parameterized to prevent SQL injection
- Read-only operations are prioritized
- Write operations require explicit confirmation
- Storage operations are logged for audit

## Tools Available

The skill has access to these internal tools:
- `execute_sql_query(query, params)`: Run parameterized SQL
- `get_property_analytics()`: Property statistics
- `get_client_analytics()`: Client statistics
- `get_match_analytics()`: Match performance
- `get_storage_stats()`: Storage usage
- `cleanup_orphaned_photos()`: Remove unused photos
- `generate_report(report_type, filters)`: Generate formatted reports
