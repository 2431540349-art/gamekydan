#!/usr/bin/env python3
import sqlite3
import os

def migrate():
    db_path = os.environ.get('DB_NAME', 'data.db')
    print(f"Initializing database structures using reload()...")
    from models.engine.sql import reload
    reload()
    
    print(f"Connecting to database: {db_path} for raw migrations...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 1. Update users table schema dynamically
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]

    new_user_cols = {
        'avatar': "TEXT DEFAULT 'avatar_1'",
        'badges': "TEXT DEFAULT '[]'",
        'total_games': "INTEGER DEFAULT 0",
        'best_streak': "INTEGER DEFAULT 0",
        'difficulty': "TEXT DEFAULT 'medium'"
    }

    for col, definition in new_user_cols.items():
        if col not in columns:
            print(f"Adding column '{col}' to table 'users'...")
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {definition}")
        else:
            print(f"Column '{col}' already exists in table 'users'.")

    # 2. Drop the old questions table to recreate it with the new schema (as it changed completely)
    # But wait, let's drop it if it has old schema. We can check if it has option_a.
    cursor.execute("PRAGMA table_info(questions)")
    q_columns = [row[1] for row in cursor.fetchall()]
    if q_columns and 'option_a' not in q_columns:
        print("Old questions table detected. Dropping it to recreate with the new schema...")
        cursor.execute("DROP TABLE questions")
        q_columns = []

    # 3. Create the new questions table
    print("Ensuring table 'questions' exists...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        option_a TEXT NOT NULL,
        option_b TEXT NOT NULL,
        option_c TEXT NOT NULL,
        option_d TEXT NOT NULL,
        correct_answer TEXT NOT NULL,
        explanation TEXT NOT NULL,
        article_id INTEGER NOT NULL,
        article_name TEXT NOT NULL,
        difficulty TEXT NOT NULL DEFAULT 'medium',
        category TEXT NOT NULL DEFAULT 'general',
        category_id INTEGER,
        created_at DATETIME,
        updated_at DATETIME
    )
    """)

    # 4. Create player_answers table
    print("Ensuring table 'player_answers' exists...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS player_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        game_id TEXT NOT NULL,
        question_id INTEGER NOT NULL,
        article_id INTEGER NOT NULL,
        is_correct BOOLEAN NOT NULL,
        time_taken REAL NOT NULL,
        difficulty TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    """)

    # 5. Create badges_definitions table
    print("Ensuring table 'badges_definitions' exists...")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS badges_definitions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        badge_key TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT NOT NULL,
        condition TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    migrate()
