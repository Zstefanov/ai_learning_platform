import json
import os
import sqlite3
from typing import List, Dict, Union

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "chat_history.json")

def get_db_path():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base_dir, "db", "my_database.db")

# /old implementation/ Load chat history from the JSON file
def load_history() -> List[List[Dict[str, str]]]:
    """
    Load chat history as a list of conversations (each a list of message dicts).
    Returns an empty list if the file is not found or invalid.
    """
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
            if not isinstance(data, list):
                return []  # Fallback to empty if structure is unexpected
            return data
    except FileNotFoundError:
        return []  # No history yet
    except json.JSONDecodeError:
        return []  # Invalid file content

# To be used to fetch chat history from the DB, instead of the JSON file
def load_history_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT conversation_id, role, content FROM history ORDER BY conversation_id, id")
    rows = cursor.fetchall()
    conn.close()

    # Group messages by conversation_id
    from collections import defaultdict
    conversations = defaultdict(list)
    for conversation_id, role, content in rows:
        conversations[conversation_id].append({'role': role, 'content': content})
    # Convert to list-of-lists like the old JSON structure
    return [msgs for _, msgs in sorted(conversations.items())]

# Save chat history to the json file
def save_history(history: List[List[Dict[str, str]]]) -> None:
    """
    Save the entire list of conversations to the HISTORY_FILE.
    """
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

# Save chat history to the database (overwrite all existing history)
def save_history_to_db(history: List[List[Dict[str, str]]]) -> None:
    """
    Save the entire list of conversations to the database,
    overwriting all existing records in the history table.
    """
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    # Delete all old records
    cur.execute("DELETE FROM history")
    # Insert new history
    for conversation_id, conversation in enumerate(history, start=1):
        for msg in conversation:
            cur.execute(
                "INSERT INTO history (conversation_id, role, content) VALUES (?, ?, ?)",
                (conversation_id, msg['role'], msg['content'])
            )
    conn.commit()
    conn.close()

def get_next_conversation_id():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT MAX(conversation_id) FROM history")
    result = cur.fetchone()
    conn.close()
    return (result[0] or 0) + 1

def add_message_to_db(conversation_id: int, role: str, content: str):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO history (conversation_id, role, content) VALUES (?, ?, ?)",
        (conversation_id, role, content)
    )
    conn.commit()
    conn.close()

def get_conversation_ids():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT conversation_id FROM history ORDER BY conversation_id")
    ids = [row[0] for row in cur.fetchall()]
    conn.close()
    return ids

def get_conversation(conversation_id: int):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT role, content FROM history WHERE conversation_id = ? ORDER BY id", (conversation_id,)
    )
    messages = [{"role": row[0], "content": row[1]} for row in cur.fetchall()]
    conn.close()
    return messages

#Delete history items from db
def delete_history_item(conversation_id: int) -> Dict[str, Union[str, List[Dict[str, str]]]]:
    try:
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        # Optionally, fetch the deleted messages for response
        cur.execute("SELECT role, content FROM history WHERE conversation_id = ? ORDER BY id", (conversation_id,))
        deleted_msgs = [{"role": row[0], "content": row[1]} for row in cur.fetchall()]

        cur.execute("DELETE FROM history WHERE conversation_id = ?", (conversation_id,))
        conn.commit()
        conn.close()

        if not deleted_msgs:
            return {"status": "error", "message": f"Conversation with id {conversation_id} not found."}

        return {
            "status": "success",
            "message": f"Conversation {conversation_id} deleted",
            "deleted_item": deleted_msgs
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to delete history item: {str(e)}"}
