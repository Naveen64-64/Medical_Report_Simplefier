import re
from config import Config

def allowed_file(filename):
    """Checks if the uploaded file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def validate_signup(username, email, password):
    """Validates signup form inputs."""
    errors = []
    
    # Username check
    if not username or len(username) < 3:
        errors.append("Username must be at least 3 characters long.")
    elif not re.match("^[a-zA-Z0-9_-]+$", username):
        errors.append("Username can only contain alphanumeric characters, underscores, and dashes.")
        
    # Email check
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not email or not re.match(email_regex, email):
        errors.append("Invalid email address.")
        
    # Password check
    if not password or len(password) < 6:
        errors.append("Password must be at least 6 characters long.")
        
    return errors
