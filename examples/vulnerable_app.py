"""
⚠️ WARNING: This file contains INTENTIONAL security vulnerabilities.
DO NOT use this code in production. This is only for testing RepoGuardian.
"""

import os
import pickle
import hashlib
import sqlite3
import subprocess
from flask import Flask, request

app = Flask(__name__)

# VULNERABILITY 1: Hardcoded Secrets
API_KEY = "sk-1234567890abcdef"
DATABASE_PASSWORD = "super_secret_password_123"
AWS_SECRET = "AKIAIOSFODNN7EXAMPLE"

# VULNERABILITY 2: Weak Cryptography (MD5 for passwords)
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

# VULNERABILITY 3: SQL Injection
def get_user(username):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    # Direct string concatenation - vulnerable to SQL injection!
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor.execute(query)
    return cursor.fetchone()

# VULNERABILITY 4: Command Injection
def run_system_command(user_input):
    # Using shell=True with user input - extremely dangerous!
    result = subprocess.call(f"echo {user_input}", shell=True)
    return result

# VULNERABILITY 5: Insecure Deserialization
def load_user_session(session_data):
    # Pickle can execute arbitrary code during deserialization
    return pickle.loads(session_data)

# VULNERABILITY 6: Path Traversal
def read_user_file(filename):
    # No validation - user can read any file on the system
    filepath = f"/var/www/uploads/{filename}"
    with open(filepath, 'r') as f:
        return f.read()

# VULNERABILITY 7: XSS (if rendered in HTML)
@app.route('/profile')
def user_profile():
    username = request.args.get('username')
    # Directly returning user input without sanitization
    return f"<h1>Welcome, {username}!</h1>"

# VULNERABILITY 8: Missing Error Handling / Information Disclosure
@app.route('/admin')
def admin_panel():
    try:
        # Sensitive operation
        result = os.environ.get('ADMIN_SECRET')
        return f"Admin secret is: {result}"
    except Exception as e:
        # Exposing internal error details to user
        return f"Error occurred: {str(e)}"

if __name__ == "__main__":
    # VULNERABILITY 9: Debug mode in production
    app.run(debug=True, host='0.0.0.0', port=5000)