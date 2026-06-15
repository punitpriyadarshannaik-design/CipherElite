# =============================================================================
#  CipherElite Assistant Bot Plugin
#
#  Plugin Name:    assistant
#  Author:         CipherElite Dev (@rishabhops)
#  Repository:     https://github.com/rishabhops/CipherElite
#
#  License:        MIT
# =============================================================================

import json
from pathlib import Path
from telethon import events, Button
import html

# Database file path
DB_PATH = Path(__file__).parent.parent / "DB" / "assistant_db.json"

# Global variables
bot_instance = None
owner_user_id = None
owner_display_name = None


def load_database():
    """Load assistant database from JSON file"""

    if DB_PATH.exists():
        try:
            with open(DB_PATH, 'r') as f:
                return json.load(f)

        except Exception as e:
            print(f"Error loading assistant database: {e}")

    return {
        "assistant_enabled": False,
        "users": [],
        "user_message_map": {},
        "stats": {
            "total_messages": 0,
            "total_replies": 0
        }
    }


def repair_database(db):
    """Repair missing keys automatically"""

    if "assistant_enabled" not in db:
        db["assistant_enabled"] = False

    if "users" not in db or not isinstance(db["users"], list):
        db["users"] = []

    if "user_message_map" not in db:
        db["user_message_map"] = {}

    if "stats" not in db or not isinstance(db["stats"], dict):
        db["stats"] = {}

    if "total_messages" not in db["stats"]:
        db["stats"]["total_messages"] = 0

    if "total_replies" not in db["stats"]:
        db["stats"]["total_replies"] = 0

    return db


def save_database(db):
    """Save assistant database"""

    try:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)

        with open(DB_PATH, 'w') as f:
            json.dump(db, f, indent=2)

    except Exception as e:
        print(f"Error saving assistant database: {e}")
