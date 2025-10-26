#!/usr/bin/env python3
"""
Database module for AI Nutrition Help application.
Handles user authentication, profiles, and nutrition data storage.

USAGE:
    from database import init_database, create_user, get_user, update_user_profile
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime
from pathlib import Path


# Database file path
DB_FILE = Path(__file__).parent / "nutrition_app.db"

def migrate_to_imperial():
    """
    Add imperial unit columns to support feet/inches and pounds.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Check existing columns
        cursor.execute("PRAGMA table_info(user_profiles)")
        columns = [column[1] for column in cursor.fetchall()]

        # Add imperial height columns
        if 'height_feet' not in columns:
            print("Adding 'height_feet' column...")
            cursor.execute("ALTER TABLE user_profiles ADD COLUMN height_feet INTEGER")

        if 'height_inches' not in columns:
            print("Adding 'height_inches' column...")
            cursor.execute("ALTER TABLE user_profiles ADD COLUMN height_inches INTEGER")

        if 'height_display' not in columns:
            print("Adding 'height_display' column...")
            cursor.execute("ALTER TABLE user_profiles ADD COLUMN height_display TEXT")

        # Add imperial weight column
        if 'weight_lbs' not in columns:
            print("Adding 'weight_lbs' column...")
            cursor.execute("ALTER TABLE user_profiles ADD COLUMN weight_lbs REAL")

        # Add age category column
        if 'age_category' not in columns:
            print("Adding 'age_category' column...")
            cursor.execute("ALTER TABLE user_profiles ADD COLUMN age_category TEXT")

        conn.commit()
        print("✓ Database migrated to support imperial units and age category!")

    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

def hash_password(password: str, salt: str = None) -> tuple:
    """
    Hash a password using SHA-256 with a salt.

    Args:
        password (str): Plain text password
        salt (str, optional): Salt for hashing. Generated if not provided.

    Returns:
        tuple: (hashed_password, salt)
    """
    if salt is None:
        salt = secrets.token_hex(32)

    # Combine password and salt, then hash
    password_salt = f"{password}{salt}".encode('utf-8')
    hashed = hashlib.sha256(password_salt).hexdigest()

    return hashed, salt


def init_database():
    """
    Initialize the database with all required tables.
    Creates tables for users, user_profiles, and nutrition_logs.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Users table - authentication
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            password_salt TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    """)

    # User profiles table - personal and nutrition information
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,

            -- Personal Information
            date_of_birth DATE,
            gender TEXT CHECK(gender IN ('male', 'female', 'other', 'prefer_not_to_say')),
            height_cm REAL,
            current_weight_kg REAL,

            -- Fitness Goals
            goal_type TEXT CHECK(goal_type IN ('weight_loss', 'weight_gain', 'muscle_gain', 'maintain', 'lean_muscle', 'general_health')),
            target_weight_kg REAL,
            activity_level TEXT CHECK(activity_level IN ('sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extremely_active')),

            -- Dietary Preferences
            diet_type TEXT CHECK(diet_type IN ('standard', 'vegetarian', 'vegan', 'keto', 'paleo', 'mediterranean', 'low_carb', 'high_protein', 'other')),
            allergies TEXT,  -- Comma-separated list of allergies
            dietary_restrictions TEXT,  -- JSON or comma-separated restrictions

            -- Calculated Metrics
            bmi REAL,
            daily_calorie_target INTEGER,
            daily_protein_target_g INTEGER,
            daily_carbs_target_g INTEGER,
            daily_fat_target_g INTEGER,

            -- Metadata
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # Nutrition logs table - stores scanned nutrition data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS nutrition_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,

            -- Log Information
            log_date DATE DEFAULT CURRENT_DATE,
            meal_type TEXT CHECK(meal_type IN ('breakfast', 'lunch', 'dinner', 'snack', 'other')),
            food_name TEXT,
            price REAL,  -- Price of the food item

            -- Nutrition Data (stored as JSON from OCR)
            nutrition_json TEXT NOT NULL,  -- Full JSON from nutrition_reader.py

            -- Quick Access Fields (extracted from JSON)
            calories INTEGER,
            protein_g REAL,
            total_fat_g REAL,
            total_carbs_g REAL,

            -- Metadata
            image_path TEXT,  -- Optional: path to scanned image
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # Weight tracking table - historical weight data
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weight_history (
            weight_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            weight_kg REAL NOT NULL,
            recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notes TEXT,

            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    """)

    # Create indexes for better query performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_nutrition_logs_user_date ON nutrition_logs(user_id, log_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_weight_history_user ON weight_history(user_id, recorded_at)")

    conn.commit()
    conn.close()

    print(f"Database initialized successfully at: {DB_FILE}")


def create_user(username: str, email: str, password: str) -> int:
    """
    Create a new user account.

    Args:
        username (str): Unique username
        email (str): User email address
        password (str): Plain text password (will be hashed)

    Returns:
        int: user_id of created user, or None if creation failed
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Hash the password
        password_hash, salt = hash_password(password)

        # Insert user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, password_salt)
            VALUES (?, ?, ?, ?)
        """, (username, email, password_hash, salt))

        user_id = cursor.lastrowid

        # Create empty profile for user
        cursor.execute("""
            INSERT INTO user_profiles (user_id)
            VALUES (?)
        """, (user_id,))

        conn.commit()
        conn.close()

        return user_id

    except sqlite3.IntegrityError as e:
        print(f"Error: Username or email already exists. {e}")
        return None
    except Exception as e:
        print(f"Error creating user: {e}")
        return None


def authenticate_user(username: str, password: str) -> dict:
    """
    Authenticate a user with username and password.

    Args:
        username (str): Username
        password (str): Plain text password

    Returns:
        dict: User data if authenticated, None otherwise
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Get user data
    cursor.execute("""
        SELECT user_id, username, email, password_hash, password_salt
        FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    if not user:
        conn.close()
        return None

    user_id, username, email, stored_hash, salt = user

    # Verify password
    computed_hash, _ = hash_password(password, salt)

    if computed_hash == stored_hash:
        # Update last login
        cursor.execute("""
            UPDATE users
            SET last_login = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (user_id,))
        conn.commit()
        conn.close()

        return {
            'user_id': user_id,
            'username': username,
            'email': email
        }

    conn.close()
    return None


def update_user_profile(user_id: int, profile_data: dict) -> bool:
    """
    Update user profile information.

    Args:
        user_id (int): User ID
        profile_data (dict): Dictionary of profile fields to update

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Build dynamic UPDATE query
        valid_fields = [
        'date_of_birth', 'gender', 'age_category', 'height_cm', 'current_weight_kg',
        'height_feet', 'height_inches', 'height_display', 'weight_lbs',
        'goal_type', 'target_weight_kg', 'activity_level', 'diet_type',
        'allergies', 'dietary_restrictions', 'bmi',
        'daily_calorie_target', 'daily_protein_target_g',
        'daily_carbs_target_g', 'daily_fat_target_g'
    ]

        # Filter only valid fields
        update_fields = {k: v for k, v in profile_data.items() if k in valid_fields}

        if not update_fields:
            return False

        # Build SET clause
        set_clause = ", ".join([f"{field} = ?" for field in update_fields.keys()])
        values = list(update_fields.values())
        values.append(user_id)

        # Execute update
        cursor.execute(f"""
            UPDATE user_profiles
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, values)

        conn.commit()
        conn.close()

        return True

    except Exception as e:
        print(f"Error updating profile: {e}")
        return False


def get_user_profile(user_id: int) -> dict:
    """
    Get complete user profile data.

    Args:
        user_id (int): User ID

    Returns:
        dict: User profile data
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT u.username, u.email, u.created_at, u.last_login,
               p.*
        FROM users u
        LEFT JOIN user_profiles p ON u.user_id = p.user_id
        WHERE u.user_id = ?
    """, (user_id,))

    row = cursor.fetchone()
    conn.close()

    if row:
        return dict(row)
    return None


def log_nutrition(user_id: int, nutrition_json: str, meal_type: str = 'other',
                 food_name: str = None, price: float = None, notes: str = None, image_path: str = None) -> int:
    """
    Log nutrition data from a scanned label.

    Args:
        user_id (int): User ID
        nutrition_json (str): JSON string from nutrition_reader.py
        meal_type (str): Type of meal
        food_name (str): Name of the food item
        price (float): Price of the food item
        notes (str): Additional notes
        image_path (str): Path to scanned image

    Returns:
        int: log_id if successful, None otherwise
    """
    try:
        import json
        nutrition_data = json.loads(nutrition_json)

        # Extract quick access fields
        calories = nutrition_data.get('calories', {}).get('total')
        protein = nutrition_data.get('macronutrients', {}).get('protein', {}).get('amount_g')
        fat = nutrition_data.get('macronutrients', {}).get('fat', {}).get('total_g')
        carbs = nutrition_data.get('macronutrients', {}).get('carbohydrates', {}).get('total_g')

        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO nutrition_logs
            (user_id, meal_type, food_name, price, nutrition_json, calories, protein_g, total_fat_g, total_carbs_g, notes, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, meal_type, food_name, price, nutrition_json, calories, protein, fat, carbs, notes, image_path))

        log_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return log_id

    except Exception as e:
        print(f"Error logging nutrition: {e}")
        return None


def get_nutrition_logs(user_id: int, start_date: str = None, end_date: str = None) -> list:
    """
    Get nutrition logs for a user within a date range.

    Args:
        user_id (int): User ID
        start_date (str): Start date (YYYY-MM-DD format), defaults to today
        end_date (str): End date (YYYY-MM-DD format), defaults to today

    Returns:
        list: List of nutrition log dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if not start_date:
        start_date = datetime.now().strftime('%Y-%m-%d')
    if not end_date:
        end_date = start_date

    cursor.execute("""
        SELECT *
        FROM nutrition_logs
        WHERE user_id = ? AND log_date BETWEEN ? AND ?
        ORDER BY log_date DESC, created_at DESC
    """, (user_id, start_date, end_date))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def add_weight_entry(user_id: int, weight_kg: float, notes: str = None) -> int:
    """
    Add a weight tracking entry.

    Args:
        user_id (int): User ID
        weight_kg (float): Weight in kilograms
        notes (str): Optional notes

    Returns:
        int: weight_id if successful, None otherwise
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO weight_history (user_id, weight_kg, notes)
            VALUES (?, ?, ?)
        """, (user_id, weight_kg, notes))

        weight_id = cursor.lastrowid

        # Also update current weight in profile
        cursor.execute("""
            UPDATE user_profiles
            SET current_weight_kg = ?, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = ?
        """, (weight_kg, user_id))

        conn.commit()
        conn.close()

        return weight_id

    except Exception as e:
        print(f"Error adding weight entry: {e}")
        return None


def get_weight_history(user_id: int, limit: int = 30) -> list:
    """
    Get weight history for a user.

    Args:
        user_id (int): User ID
        limit (int): Number of recent entries to return

    Returns:
        list: List of weight history dictionaries
    """
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM weight_history
        WHERE user_id = ?
        ORDER BY recorded_at DESC
        LIMIT ?
    """, (user_id, limit))

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# Helper function to calculate BMI
def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI from weight and height."""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def migrate_database():
    """
    Migrate existing database to add new columns if they don't exist.
    This ensures backward compatibility with existing databases.
    """
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    try:
        # Check if price column exists in nutrition_logs
        cursor.execute("PRAGMA table_info(nutrition_logs)")
        columns = [column[1] for column in cursor.fetchall()]

        if 'price' not in columns:
            print("Adding 'price' column to nutrition_logs table...")
            cursor.execute("ALTER TABLE nutrition_logs ADD COLUMN price REAL")
            conn.commit()
            print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    # Initialize database when run directly
    print("Initializing database...")
    init_database()
    print("Database setup complete!")