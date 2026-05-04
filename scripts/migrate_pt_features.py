
import sqlite3

def update_db():
    conn = sqlite3.connect('smart_gym.db')
    cursor = conn.cursor()
    
    # Add columns to users table
    columns_to_add = [
        ('training_days', 'INTEGER DEFAULT 3'),
        ('has_injury', 'INTEGER DEFAULT 0'),
        ('injury_details', 'TEXT')
    ]
    
    for col, dtype in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {dtype}")
            print(f"Added column {col}")
        except sqlite3.OperationalError:
            print(f"Column {col} already exists")
            
    # Create exercise_logs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS exercise_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        exercise_name TEXT,
        muscle_group TEXT,
        max_weight REAL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    print("Checked/Created exercise_logs table.")
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_db()
