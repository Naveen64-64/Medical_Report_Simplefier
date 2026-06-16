from werkzeug.security import generate_password_hash, check_password_hash
from database.db import get_db_connection

class UserModel:
    @staticmethod
    def create_user(username, email, password):
        """Creates a new user and returns their database ID."""
        password_hash = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error creating user: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_user_by_username(username):
        """Fetches a user record by username."""
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
        conn.close()
        return user

    @staticmethod
    def get_user_by_id(user_id):
        """Fetches a user record by primary key ID."""
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()
        conn.close()
        return user

    @staticmethod
    def verify_password(password_hash, password):
        """Verifies if the plaintext password matches the stored hash."""
        return check_password_hash(password_hash, password)
