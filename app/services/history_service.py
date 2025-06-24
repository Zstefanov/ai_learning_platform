import json
import os
from typing import List, Dict, Union

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "chat_history.json")

# Load chat history from the file
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


# Save chat history to the file
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