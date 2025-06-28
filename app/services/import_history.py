import sqlite3
import json
import os


# This script was used for the initial import of the chat history from a JSON file into an SQLite database.
def create_connection(db_file):
    try:
        connection = sqlite3.connect(db_file)
        return connection
    except sqlite3.Error as e:
        print(e)
    return None

def insert_message(conn, conversation_id, role, content):
    sql = """INSERT INTO history (conversation_id, role, content) VALUES (?, ?, ?)"""
    cursor = conn.cursor()
    cursor.execute(sql, (conversation_id, role, content))
    conn.commit()

def import_history(json_path, db_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        conversations = json.load(f)

    conn = create_connection(db_path)
    if not conn:
        print("Failed to connect to database.")
        return

    for conversation_id, msgs in enumerate(conversations, start=1):
        for msg in msgs:
            insert_message(conn, conversation_id, msg['role'], msg['content'])

    conn.close()
    print("Import completed.")

if __name__ == "__main__":
    # Go up two levels from 'app/services' to project root, then into 'db'
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "db", "my_database.db")
    json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chat_history.json")
    print("Database path:", db_path)
    print("JSON path:", json_path)
    import_history(json_path=json_path, db_path=db_path)

    with open(json_path, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    print(f"Loaded {len(conversations)} conversations from {json_path}")