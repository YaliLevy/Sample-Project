"""
Supabase Real Estate Management Skill
Advanced database operations and analytics for WhatsApp Real Estate Bot
"""
import logging
from typing import Optional, Dict, List, Any
from datetime import datetime, timedelta
from supabase import create_client, Client
from sqlalchemy import text

from config import settings
from database.connection import get_session, engine

logger = logging.getLogger(__name__)

# Initialize Supabase client
supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)


class SupabaseSkill:
    """Main skill class for Supabase operations"""

    def __init__(self):
        self.supabase = supabase
        self.bucket_name = settings.SUPABASE_STORAGE_BUCKET

    # ==========================================
    # SQL QUERY EXECUTION
    # ==========================================

    def execute_sql_query(self, query: str, params: Optional[Dict] = None, read_only: bool = True) -> List[Dict]:
        """
        Execute a parameterized SQL query safely.

        Args:
            query: SQL query with :param placeholders
            params: Dictionary of parameters
            read_only: If True, only SELECT queries allowed

        Returns:
            List of result rows as dictionaries
        """
        try:
            # Safety check for read-only mode
            if read_only and not query.strip().upper().startswith('SELECT'):
                raise ValueError("Only SELECT queries are allowed in read-only mode")

            with engine.connect() as conn:
                result = conn.execute(text(query), params or {})

                # If SELECT, return results
                if query.strip().upper().startswith('SELECT'):
                    columns = result.keys()
                    rows = result.fetchall()
                    return [dict(zip(columns, row)) for row in rows]
                else:
                    conn.commit()
                    return [{"affected_rows": result.rowcount}]

        except Exception as e:
            logger.error(f"SQL query error: {e}", exc_info=True)
            raise

    # ==========================================
    # PROPERTY ANALYTICS
    # ==========================================

    def get_property_analytics(self, city: Optional[str] = None, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive property analytics.

        Args:
            city: Filter by city (optional)
            days: Look back period in days

        Returns:
            Dictionary with analytics data
        """
        try:
            analytics = {}

            # Base query with optional city filter
            city_filter = f"AND city = :city" if city else ""
            date_filter = datetime.now() - timedelta(days=days)

            # Total counts by transaction type
            query = f"""
                SELECT
                    transaction_type,
                    COUNT(*) as count,
                    AVG(price) as avg_price,
                    MIN(price) as min_price,
                    MAX(price) as max_price,
                    AVG(rooms) as avg_rooms
                FROM properties
                WHERE created_at >= :date_filter {city_filter}
                GROUP BY transaction_type
            """
            params = {"date_filter": date_filter}
            if city:
                params["city"] = city

            analytics["by_transaction_type"] = self.execute_sql_query(query, params)

            # By city (if not filtered)
            if not city:
                query = """
                    SELECT
                        city,
                        COUNT(*) as count,
                        AVG(price) as avg_price
                    FROM properties
                    WHERE created_at >= :date_filter
                    GROUP BY city
                    ORDER BY count DESC
                    LIMIT 10
                """
                analytics["top_cities"] = self.execute_sql_query(query, {"date_filter": date_filter})

            # Status distribution
            query = f"""
                SELECT
                    status,
                    COUNT(*) as count
                FROM properties
                WHERE created_at >= :date_filter {city_filter}
                GROUP BY status
            """
            analytics["by_status"] = self.execute_sql_query(query, params)

            # Daily new listings
            query = f"""
                SELECT
                    DATE(created_at) as date,
                    COUNT(*) as count
                FROM properties
                WHERE created_at >= :date_filter {city_filter}
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """
            analytics["daily_new_listings"] = self.execute_sql_query(query, params)

            return analytics

        except Exception as e:
            logger.error(f"Property analytics error: {e}", exc_info=True)
            return {"error": str(e)}

    def get_property_performance(self, limit: int = 10) -> List[Dict]:
        """
        Get top performing properties by match count and scores.

        Args:
            limit: Number of properties to return

        Returns:
            List of property performance data
        """
        try:
            query = """
                SELECT
                    p.id,
                    p.city,
                    p.street,
                    p.rooms,
                    p.price,
                    p.transaction_type,
                    COUNT(m.id) as match_count,
                    AVG(m.score) as avg_score,
                    COUNT(CASE WHEN m.status = 'interested' THEN 1 END) as interested_count,
                    COUNT(CASE WHEN m.status = 'closed' THEN 1 END) as closed_count
                FROM properties p
                LEFT JOIN matches m ON p.id = m.property_id
                WHERE p.status = 'available'
                GROUP BY p.id, p.city, p.street, p.rooms, p.price, p.transaction_type
                HAVING COUNT(m.id) > 0
                ORDER BY match_count DESC, avg_score DESC
                LIMIT :limit
            """
            return self.execute_sql_query(query, {"limit": limit})

        except Exception as e:
            logger.error(f"Property performance error: {e}", exc_info=True)
            return []

    # ==========================================
    # CLIENT ANALYTICS
    # ==========================================

    def get_client_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive client analytics.

        Args:
            days: Look back period in days

        Returns:
            Dictionary with analytics data
        """
        try:
            analytics = {}
            date_filter = datetime.now() - timedelta(days=days)

            # By looking_for type
            query = """
                SELECT
                    looking_for,
                    COUNT(*) as count,
                    AVG(max_price) as avg_budget
                FROM clients
                WHERE created_at >= :date_filter AND status = 'active'
                GROUP BY looking_for
            """
            analytics["by_type"] = self.execute_sql_query(query, {"date_filter": date_filter})

            # By city preference
            query = """
                SELECT
                    city,
                    COUNT(*) as count
                FROM clients
                WHERE created_at >= :date_filter AND status = 'active' AND city IS NOT NULL
                GROUP BY city
                ORDER BY count DESC
            """
            analytics["by_city"] = self.execute_sql_query(query, {"date_filter": date_filter})

            # Budget distribution
            query = """
                SELECT
                    CASE
                        WHEN max_price < 3000 THEN 'Under 3,000'
                        WHEN max_price < 5000 THEN '3,000-5,000'
                        WHEN max_price < 7000 THEN '5,000-7,000'
                        WHEN max_price < 10000 THEN '7,000-10,000'
                        ELSE 'Over 10,000'
                    END as budget_range,
                    COUNT(*) as count
                FROM clients
                WHERE created_at >= :date_filter AND status = 'active' AND looking_for = 'rent'
                GROUP BY budget_range
                ORDER BY MIN(max_price)
            """
            analytics["budget_distribution"] = self.execute_sql_query(query, {"date_filter": date_filter})

            return analytics

        except Exception as e:
            logger.error(f"Client analytics error: {e}", exc_info=True)
            return {"error": str(e)}

    def get_client_satisfaction(self, limit: int = 10) -> List[Dict]:
        """
        Get clients with best match scores and engagement.

        Args:
            limit: Number of clients to return

        Returns:
            List of client satisfaction data
        """
        try:
            query = """
                SELECT
                    c.id,
                    c.name,
                    c.city,
                    c.looking_for,
                    c.max_price,
                    COUNT(m.id) as match_count,
                    AVG(m.score) as avg_match_score,
                    MAX(m.score) as best_match_score,
                    COUNT(CASE WHEN m.status = 'interested' THEN 1 END) as interested_count
                FROM clients c
                LEFT JOIN matches m ON c.id = m.client_id
                WHERE c.status = 'active'
                GROUP BY c.id, c.name, c.city, c.looking_for, c.max_price
                HAVING COUNT(m.id) > 0
                ORDER BY avg_match_score DESC, match_count DESC
                LIMIT :limit
            """
            return self.execute_sql_query(query, {"limit": limit})

        except Exception as e:
            logger.error(f"Client satisfaction error: {e}", exc_info=True)
            return []

    # ==========================================
    # MATCH ANALYTICS
    # ==========================================

    def get_match_analytics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get comprehensive match analytics and conversion rates.

        Args:
            days: Look back period in days

        Returns:
            Dictionary with match analytics
        """
        try:
            analytics = {}
            date_filter = datetime.now() - timedelta(days=days)

            # Overall statistics
            query = """
                SELECT
                    COUNT(*) as total_matches,
                    AVG(score) as avg_score,
                    COUNT(CASE WHEN status = 'suggested' THEN 1 END) as suggested,
                    COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent,
                    COUNT(CASE WHEN status = 'interested' THEN 1 END) as interested,
                    COUNT(CASE WHEN status = 'rejected' THEN 1 END) as rejected,
                    COUNT(CASE WHEN status = 'closed' THEN 1 END) as closed
                FROM matches
                WHERE suggested_at >= :date_filter
            """
            overall = self.execute_sql_query(query, {"date_filter": date_filter})
            if overall:
                analytics["overall"] = overall[0]
                # Calculate conversion rates
                total = overall[0].get('total_matches', 0)
                if total > 0:
                    analytics["conversion_rates"] = {
                        "suggested_to_sent": round(overall[0].get('sent', 0) / total * 100, 2),
                        "sent_to_interested": round(overall[0].get('interested', 0) / total * 100, 2),
                        "interested_to_closed": round(overall[0].get('closed', 0) / total * 100, 2)
                    }

            # Score distribution
            query = """
                SELECT
                    CASE
                        WHEN score < 50 THEN 'Poor (0-50)'
                        WHEN score < 65 THEN 'Fair (50-65)'
                        WHEN score < 80 THEN 'Good (65-80)'
                        ELSE 'Excellent (80+)'
                    END as score_range,
                    COUNT(*) as count
                FROM matches
                WHERE suggested_at >= :date_filter
                GROUP BY score_range
                ORDER BY MIN(score)
            """
            analytics["score_distribution"] = self.execute_sql_query(query, {"date_filter": date_filter})

            return analytics

        except Exception as e:
            logger.error(f"Match analytics error: {e}", exc_info=True)
            return {"error": str(e)}

    # ==========================================
    # STORAGE MANAGEMENT
    # ==========================================

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get Supabase Storage usage statistics."""
        try:
            # Get all files from bucket
            files = self.supabase.storage.from_(self.bucket_name).list()

            # Count photos in database
            with get_session() as session:
                db_photo_count = session.execute(text("SELECT COUNT(*) FROM photos")).scalar()

            stats = {
                "bucket_name": self.bucket_name,
                "total_files": len(files) if files else 0,
                "photos_in_db": db_photo_count,
                "files": files[:10] if files else []  # Sample of files
            }

            return stats

        except Exception as e:
            logger.error(f"Storage stats error: {e}", exc_info=True)
            return {"error": str(e)}

    def get_property_photos(self, property_id: int) -> List[Dict]:
        """
        Get all photos for a specific property.

        Args:
            property_id: Property ID

        Returns:
            List of photo URLs and metadata
        """
        try:
            query = """
                SELECT
                    id,
                    file_path,
                    twilio_media_url,
                    media_content_type,
                    created_at
                FROM photos
                WHERE property_id = :property_id
                ORDER BY created_at DESC
            """
            return self.execute_sql_query(query, {"property_id": property_id})

        except Exception as e:
            logger.error(f"Get property photos error: {e}", exc_info=True)
            return []

    def cleanup_orphaned_photos(self) -> Dict[str, int]:
        """
        Identify and optionally remove photos not linked to any property.

        Returns:
            Dictionary with cleanup statistics
        """
        try:
            # Find orphaned photos (properties that were deleted)
            query = """
                SELECT id, file_path
                FROM photos
                WHERE property_id NOT IN (SELECT id FROM properties)
            """
            orphaned = self.execute_sql_query(query)

            return {
                "orphaned_count": len(orphaned),
                "orphaned_photos": orphaned[:10]  # Sample
            }

        except Exception as e:
            logger.error(f"Cleanup orphaned photos error: {e}", exc_info=True)
            return {"error": str(e)}

    # ==========================================
    # REPORT GENERATION
    # ==========================================

    def generate_report(self, report_type: str, **filters) -> str:
        """
        Generate formatted reports.

        Args:
            report_type: Type of report (properties, clients, matches, monthly)
            **filters: Additional filters (city, date_range, etc.)

        Returns:
            Formatted report as string
        """
        try:
            if report_type == "properties":
                return self._generate_property_report(**filters)
            elif report_type == "clients":
                return self._generate_client_report(**filters)
            elif report_type == "matches":
                return self._generate_match_report(**filters)
            elif report_type == "monthly":
                return self._generate_monthly_report(**filters)
            else:
                return f"Unknown report type: {report_type}"

        except Exception as e:
            logger.error(f"Generate report error: {e}", exc_info=True)
            return f"Error generating report: {str(e)}"

    def _generate_property_report(self, city: Optional[str] = None, days: int = 30) -> str:
        """Generate property report."""
        analytics = self.get_property_analytics(city=city, days=days)
        performance = self.get_property_performance(limit=5)

        report = f"# Property Report ({days} days)\n\n"

        if city:
            report += f"**City:** {city}\n\n"

        # Transaction types
        report += "## By Transaction Type\n"
        for row in analytics.get("by_transaction_type", []):
            report += f"- **{row['transaction_type'].upper()}**: {row['count']} properties, "
            report += f"Avg: {int(row['avg_price']):,} ₪, "
            report += f"Range: {int(row['min_price']):,}-{int(row['max_price']):,} ₪\n"

        # Top cities
        if not city and analytics.get("top_cities"):
            report += "\n## Top Cities\n"
            for row in analytics.get("top_cities", []):
                report += f"- **{row['city']}**: {row['count']} properties, Avg: {int(row['avg_price']):,} ₪\n"

        # Top performers
        if performance:
            report += "\n## Top Performing Properties\n"
            for i, prop in enumerate(performance[:5], 1):
                report += f"{i}. **#{prop['id']}** - {prop['city']}, {prop['street']} | "
                report += f"{prop['rooms']} rooms, {int(prop['price']):,} ₪ | "
                report += f"Matches: {prop['match_count']}, Score: {prop['avg_score']:.1f}\n"

        return report

    def _generate_client_report(self, days: int = 30) -> str:
        """Generate client report."""
        analytics = self.get_client_analytics(days=days)
        satisfaction = self.get_client_satisfaction(limit=5)

        report = f"# Client Report ({days} days)\n\n"

        # By type
        report += "## By Type\n"
        for row in analytics.get("by_type", []):
            report += f"- **{row['looking_for'].upper()}**: {row['count']} clients, "
            if row['avg_budget']:
                report += f"Avg Budget: {int(row['avg_budget']):,} ₪\n"
            else:
                report += "\n"

        # Top cities
        if analytics.get("by_city"):
            report += "\n## Popular Cities\n"
            for row in analytics.get("by_city", [])[:5]:
                report += f"- **{row['city']}**: {row['count']} clients\n"

        # Best matches
        if satisfaction:
            report += "\n## Clients with Best Matches\n"
            for i, client in enumerate(satisfaction[:5], 1):
                report += f"{i}. **{client['name']}** ({client['city']}) | "
                report += f"Budget: {int(client['max_price']):,} ₪ | "
                report += f"Matches: {client['match_count']}, Avg Score: {client['avg_match_score']:.1f}\n"

        return report

    def _generate_match_report(self, days: int = 30) -> str:
        """Generate match report."""
        analytics = self.get_match_analytics(days=days)

        report = f"# Match Analytics Report ({days} days)\n\n"

        if "overall" in analytics:
            overall = analytics["overall"]
            report += "## Overall Statistics\n"
            report += f"- **Total Matches**: {overall['total_matches']}\n"
            report += f"- **Average Score**: {overall['avg_score']:.1f}\n"
            report += f"- **Suggested**: {overall['suggested']}\n"
            report += f"- **Sent**: {overall['sent']}\n"
            report += f"- **Interested**: {overall['interested']}\n"
            report += f"- **Rejected**: {overall['rejected']}\n"
            report += f"- **Closed**: {overall['closed']}\n"

        if "conversion_rates" in analytics:
            rates = analytics["conversion_rates"]
            report += "\n## Conversion Rates\n"
            report += f"- **Suggested → Sent**: {rates['suggested_to_sent']}%\n"
            report += f"- **Sent → Interested**: {rates['sent_to_interested']}%\n"
            report += f"- **Interested → Closed**: {rates['interested_to_closed']}%\n"

        return report

    def _generate_monthly_report(self) -> str:
        """Generate comprehensive monthly report."""
        property_report = self._generate_property_report(days=30)
        client_report = self._generate_client_report(days=30)
        match_report = self._generate_match_report(days=30)

        report = f"# Monthly Report - {datetime.now().strftime('%B %Y')}\n\n"
        report += property_report + "\n\n---\n\n"
        report += client_report + "\n\n---\n\n"
        report += match_report

        return report


# Singleton instance
skill = SupabaseSkill()


# Convenience functions for direct use
def execute_sql(query: str, params: Optional[Dict] = None) -> List[Dict]:
    """Execute SQL query"""
    return skill.execute_sql_query(query, params)


def get_analytics(analytics_type: str = "properties", **kwargs) -> Dict[str, Any]:
    """Get analytics by type"""
    if analytics_type == "properties":
        return skill.get_property_analytics(**kwargs)
    elif analytics_type == "clients":
        return skill.get_client_analytics(**kwargs)
    elif analytics_type == "matches":
        return skill.get_match_analytics(**kwargs)
    else:
        return {"error": f"Unknown analytics type: {analytics_type}"}


def generate_report(report_type: str, **filters) -> str:
    """Generate formatted report"""
    return skill.generate_report(report_type, **filters)


def get_storage_info() -> Dict[str, Any]:
    """Get storage statistics"""
    return skill.get_storage_stats()
