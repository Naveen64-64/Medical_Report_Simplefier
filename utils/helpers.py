import uuid
from datetime import datetime

def generate_unique_id():
    """Generates a secure unique identifier string."""
    return str(uuid.uuid4())

def format_datetime(timestamp_str):
    """Formats an SQLite timestamp string into a readable format."""
    try:
        dt = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%b %d, %Y - %I:%M %p")
    except ValueError:
        return timestamp_str
