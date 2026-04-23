"""
Supabase database — permanent storage that survives Railway redeployments.

Every user profile, business plan, brand, and conversation history is
saved here. The bot reads from this on every start, so nothing is ever lost.
"""
import os
import json

SUPABASE_URL = None
SUPABASE_KEY = None
_client = None

# Fields saved to / loaded from the database
SAVED_FIELDS = [
    "interview_answers",     # Profile from onboarding questions
    "chosen_method",         # The method they chose
    "top_methods",           # Research results
    "recommendation",        # Personalized recommendation
    "plan",                  # 30-day business plan
    "brand",                 # Brand identity (name, colors, tagline, etc.)
    "pain_points",           # Audience pain point research
    "build_niche",           # Niche entered during build
    "build_service",         # Service entered during build
    "build_platforms",       # Platforms chosen during build
    "conversation_history",  # Last 40 messages of chat history
    "formatted_research",    # Raw research text
]


def _get_client():
    global _client, SUPABASE_URL, SUPABASE_KEY
    if _client:
        return _client
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        from supabase import create_client
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _client
    except Exception as e:
        print(f"[DB] Could not connect to Supabase: {e}")
        return None


def is_available() -> bool:
    return _get_client() is not None


def load_user(telegram_user_id: int) -> dict:
    """
    Load a user's full data from Supabase.
    Returns an empty dict if user not found or DB unavailable.
    """
    client = _get_client()
    if not client:
        return {}
    try:
        result = (
            client.table("user_sessions")
            .select("*")
            .eq("telegram_user_id", telegram_user_id)
            .execute()
        )
        if result.data:
            row = result.data[0]
            user_data = {}
            for field in SAVED_FIELDS:
                val = row.get(field)
                if val is not None and val != "" and val != [] and val != {}:
                    user_data[field] = val
            return user_data
    except Exception as e:
        print(f"[DB] Load error for user {telegram_user_id}: {e}")
    return {}


def save_user(telegram_user_id: int, user_data: dict) -> bool:
    """
    Save a user's data to Supabase (insert or update).
    Returns True on success.
    """
    client = _get_client()
    if not client:
        return False
    try:
        record = {"telegram_user_id": telegram_user_id}
        for field in SAVED_FIELDS:
            if field in user_data:
                val = user_data[field]
                # Trim conversation history to last 40 messages before saving
                if field == "conversation_history" and isinstance(val, list):
                    val = val[-40:]
                record[field] = val

        client.table("user_sessions").upsert(record).execute()
        return True
    except Exception as e:
        print(f"[DB] Save error for user {telegram_user_id}: {e}")
        return False


def delete_user(telegram_user_id: int) -> bool:
    """Wipe all data for a user (used by /reset)."""
    client = _get_client()
    if not client:
        return False
    try:
        client.table("user_sessions").delete().eq("telegram_user_id", telegram_user_id).execute()
        return True
    except Exception as e:
        print(f"[DB] Delete error for user {telegram_user_id}: {e}")
        return False
