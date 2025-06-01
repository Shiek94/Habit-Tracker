import sqlite3

def create_tables(db):
    """Create the necessary tables in the SQLite database."""
    cur = db.cursor()

    # Create habit table with all relevant fields for the habits
    cur.execute("""CREATE TABLE IF NOT EXISTS habits (
        name TEXT PRIMARY KEY,
        description TEXT,
        periodicity TEXT,
        streak INTEGER DEFAULT 0,
        event_count INTEGER DEFAULT 0)""")

    # Create habit_tracker table to track habit events
    cur.execute("""CREATE TABLE IF NOT EXISTS habit_tracker (
        date TEXT,
        habitName TEXT,
        FOREIGN KEY (habitName) REFERENCES habits(name))""")

    db.commit()

def get_connection(name = "main.db"):
    """Establish a connection to the SQLite database."""
    db = sqlite3.connect(name)
    create_tables(db)
    return db



