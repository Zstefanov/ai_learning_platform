import sqlite3

def create_connection(db_file):
    # Create a database connection to the SQLite db
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        print(f"SQLite database connected: {db_file}")
        return connection
    except sqlite3.Error as e:
        print(e)
    return connection

def create_table(connection):
    """Create the history table with the new schema."""
    try:
        cursor = connection.cursor()
        #cursor.execute("DROP TABLE IF EXISTS history;") #-> Uncomment this line to drop the table if needed
        sql_create_history_table = """
        CREATE TABLE history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor.execute(sql_create_history_table)
        print("Table 'history' created with new schema.")
    except sqlite3.Error as e:
        print(e)

if __name__ == "__main__":
    database_path = "my_database.db"
    db_connection = create_connection(database_path)
    if db_connection is not None:
        create_table(db_connection)
        db_connection.close()
    else:
        print("Error! Cannot create the database connection.")