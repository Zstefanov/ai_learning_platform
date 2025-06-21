import json
import os
from typing import List, Dict

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "chat_history.json")

print(f"Absolute path to history file: {os.path.abspath(HISTORY_FILE)}")

# Load chat history from the file
def load_history() -> List[Dict]:
    """
    Load chat history from the HISTORY_FILE.
    If the file doesn't exist, return a hint indicating FileNotFoundError.
    If the file contains invalid JSON, return a hint indicating JSONDecodeError.
    If the file is empty, return a hint indicating Empty JSON.
    """
    try:
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
            if not data:  # Check if the JSON is empty
                return [{"hint": "Empty JSON"}]
            return data
    except FileNotFoundError:
        # Return a hint if the file does not exist
        return [{"hint": "FileNotFoundError"}]
    except json.JSONDecodeError:
        # Return a hint if the file contains invalid JSON
        return [{"hint": "JSONDecodeError"}]

# Save chat history to the file
def save_history(history: List[Dict]) -> None:
    """
    Save chat history to the HISTORY_FILE.
    Overwrites the file with the new history.
    """
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)