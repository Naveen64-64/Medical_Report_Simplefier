from database.db import get_db_connection

class ReportModel:
    @staticmethod
    def create_report(report_id, user_id, filename, file_path, original_text, simplified_text):
        """Saves a new medical report record in the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                """INSERT INTO reports (id, user_id, filename, file_path, original_text, simplified_text)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (report_id, user_id, filename, file_path, original_text, simplified_text)
            )
            conn.commit()
            return report_id
        except Exception as e:
            print(f"Error saving report: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_report_by_id(report_id):
        """Fetches a specific report details by report UUID/id."""
        conn = get_db_connection()
        report = conn.execute(
            "SELECT * FROM reports WHERE id = ?", (report_id,)
        ).fetchone()
        conn.close()
        return report

    @staticmethod
    def get_reports_by_user(user_id):
        """Fetches all reports associated with a specific user."""
        conn = get_db_connection()
        reports = conn.execute(
            "SELECT * FROM reports WHERE user_id = ? ORDER BY created_at DESC", (user_id,)
        ).fetchall()
        conn.close()
        return reports
