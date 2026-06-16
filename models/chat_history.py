from database.db import get_db_connection

class ChatHistoryModel:
    @staticmethod
    def add_message(report_id, sender, message):
        """Appends a new chat message to the history of a specific report."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO chat_history (report_id, sender, message) VALUES (?, ?, ?)",
                (report_id, sender, message)
            )
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error adding chat message: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_history_by_report(report_id):
        """Fetches the conversation log chronologically for a report."""
        conn = get_db_connection()
        history = conn.execute(
            "SELECT * FROM chat_history WHERE report_id = ? ORDER BY created_at ASC",
            (report_id,)
        ).fetchall()
        conn.close()
        return history
