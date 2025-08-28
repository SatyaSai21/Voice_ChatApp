# --------------------------
# User storage helpers
# --------------------------

import bcrypt
import time
import mysql.connector

from typing import Optional, Tuple

from database.db import get_db_connection


def create_user(email: str, password: str, preferred_language: str, gender: str, preferred_voice: str, display_name: Optional[str] = None) -> Tuple[bool, str]:
    email = email.strip().lower()
    if not email.endswith('@gmail.com'):
        return False, 'Please use a Gmail address (@gmail.com).'
    if len(password) < 8:
        return False, 'Password must be at least 8 characters.'
    if not display_name:
        display_name = email.split("@")[0]

    pw_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO users (email, display_name, password_hash, preferred_language, gender, preferred_voice, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (email, display_name, pw_hash, preferred_language, gender, preferred_voice, int(time.time()))
        )
        conn.commit()
        cur.close()
        conn.close()
        return True, 'Account created. You can log in now.'
    except mysql.connector.IntegrityError:
        return False, 'An account with this email already exists.'

def authenticate_user(email: str, password: str) -> Tuple[bool, Optional[dict], str]:
    email = email.strip().lower()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, email, display_name, password_hash, preferred_voice, preferred_language
        FROM users WHERE email = %s
    """, (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return False, None, 'No account found for this email.'

    user_id, email, display_name, pw_hash, preferred_voice, preferred_language = row
    if bcrypt.checkpw(password.encode('utf-8'), pw_hash):
        return True, {
            'id': user_id,
            'email': email,
            'display_name': display_name or email.split('@')[0],
            'preferred_voice': preferred_voice,
            'preferred_language': preferred_language,
        }, 'Login successful.'
    else:
        return False, None, 'Incorrect password.'

def get_user(email: str) -> Optional[dict]:
    email = email.strip().lower()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, email, display_name, preferred_voice, preferred_language
        FROM users WHERE email = %s
    """, (email,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None

    user_id, email, display_name, preferred_voice, preferred_language = row
    return {
        'id': user_id,
        'email': email,
        'display_name': display_name or email.split('@')[0],
        'preferred_voice': preferred_voice,
        'preferred_language': preferred_language,
    }

def get_user_language(user_identifier: str) -> Optional[str]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT preferred_language FROM users WHERE email = %s", (user_identifier.strip().lower(),))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        return None
    return row[0]
