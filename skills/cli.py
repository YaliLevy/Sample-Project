#!/usr/bin/env python
"""
CLI tool for Supabase Skill operations
Usage: python skills/cli.py [command] [options]
"""
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from skills.supabase_skill import skill


def main():
    if len(sys.argv) < 2:
        print_help()
        return

    command = sys.argv[1]

    try:
        if command == "analytics":
            analytics_type = sys.argv[2] if len(sys.argv) > 2 else "properties"
            result = None

            if analytics_type == "properties":
                city = sys.argv[3] if len(sys.argv) > 3 else None
                result = skill.get_property_analytics(city=city)
            elif analytics_type == "clients":
                result = skill.get_client_analytics()
            elif analytics_type == "matches":
                result = skill.get_match_analytics()

            print(json.dumps(result, indent=2, default=str))

        elif command == "report":
            report_type = sys.argv[2] if len(sys.argv) > 2 else "properties"
            result = skill.generate_report(report_type)
            print(result)

        elif command == "sql":
            if len(sys.argv) < 3:
                print("Usage: python skills/cli.py sql \"SELECT * FROM properties LIMIT 10\"")
                return

            query = sys.argv[2]
            result = skill.execute_sql_query(query)
            print(json.dumps(result, indent=2, default=str))

        elif command == "storage":
            result = skill.get_storage_stats()
            print(json.dumps(result, indent=2, default=str))

        elif command == "performance":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            result = skill.get_property_performance(limit=limit)
            print(json.dumps(result, indent=2, default=str))

        elif command == "satisfaction":
            limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            result = skill.get_client_satisfaction(limit=limit)
            print(json.dumps(result, indent=2, default=str))

        elif command == "help":
            print_help()

        else:
            print(f"Unknown command: {command}")
            print_help()

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def print_help():
    help_text = """
Supabase Skill CLI - WhatsApp Real Estate Bot

Usage: python skills/cli.py [command] [options]

Commands:
  analytics [type] [city]    Get analytics (properties/clients/matches)
    Example: python skills/cli.py analytics properties
    Example: python skills/cli.py analytics properties "תל אביב"

  report [type]              Generate formatted report
    Types: properties, clients, matches, monthly
    Example: python skills/cli.py report monthly

  sql "query"                Execute SQL query
    Example: python skills/cli.py sql "SELECT * FROM properties LIMIT 10"

  storage                    Get storage statistics
    Example: python skills/cli.py storage

  performance [limit]        Get top performing properties
    Example: python skills/cli.py performance 10

  satisfaction [limit]       Get client satisfaction data
    Example: python skills/cli.py satisfaction 10

  help                       Show this help message

Examples:
  # Get property analytics for Tel Aviv
  python skills/cli.py analytics properties "תל אביב"

  # Generate monthly report
  python skills/cli.py report monthly

  # Execute custom SQL
  python skills/cli.py sql "SELECT city, COUNT(*) FROM properties GROUP BY city"

  # Get storage stats
  python skills/cli.py storage
"""
    print(help_text)


if __name__ == "__main__":
    main()
