"""
Skills package for WhatsApp Real Estate Bot
"""
from .supabase_skill import (
    skill,
    execute_sql,
    get_analytics,
    generate_report,
    get_storage_info
)

__all__ = [
    'skill',
    'execute_sql',
    'get_analytics',
    'generate_report',
    'get_storage_info'
]
