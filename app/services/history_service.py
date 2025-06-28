import json
import os
import sqlite3
from typing import List, Dict, Union

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "chat_history.json")

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


# Delete a full conversation by its index
def delete_history_item(index: int) -> Dict[str, Union[str, List[Dict[str, str]]]]:
    """
    Delete a conversation by its index.
    """
    try:
        history = load_history()

        if index < 0 or index >= len(history):
            return {"status": "error", "message": f"Invalid index: {index}"}

        removed_item = history.pop(index)
        save_history(history)

        return {
            "status": "success",
            "message": f"Conversation {index} deleted",
            "deleted_item": removed_item
        }

    except Exception as e:
        return {"status": "error", "message": f"Failed to delete history item: {str(e)}"}