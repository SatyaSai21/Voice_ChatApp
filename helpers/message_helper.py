# --------------------------
# Message storage helpers
# --------------------------

import time

from typing import Dict, List, Optional
from user_helper import get_user
from database.db import get_db_connection

def room_id_for(u1: str, u2: str) -> str:
    a, b = sorted([u1.strip().lower(), u2.strip().lower()])
    return f"{a}__{b}"

def peer_exists(email: str) -> bool:
    return get_user(email) is not None

def ensure_room_exists(me_email: str, peer_email: str) -> Optional[str]:
    """
    Ensure a room row exists if both users exist.
    Returns room_id if created/existing, else None (if peer doesn't exist).
    """
    me = me_email.strip().lower()
    peer = peer_email.strip().lower()
    if not peer_exists(peer):
        return None

    rid = room_id_for(me, peer)
    ts = int(time.time())

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM rooms WHERE room_id=%s", (rid,))
    r = cur.fetchone()
    if not r:
        # Insert new room
        cur.execute("""
            INSERT INTO rooms (room_id, user1_email, user2_email, created_at)
            VALUES (%s, %s, %s, %s)
        """, (rid, min(me, peer), max(me, peer), ts))
        conn.commit()
    cur.close()
    conn.close()
    return rid

def save_message(room, sender_id, receiver_id, message_type,
                 original_text=None, original_language=None,
                 translated_text=None, translated_language=None,
                 audio_format=None, audio_bytes=None,
                 file_path=None):
    """
    Save a message into the messages table.
    Also guarantees the room exists (if peer exists).
    """
    # Enforce peer existence and room creation rule
    rid = ensure_room_exists(sender_id, receiver_id)
    if rid is None:
        raise ValueError("Peer does not exist. Room not created, message not sent.")

    if room != rid:
        # normalize room id
        room = rid

    conn = get_db_connection()
    cur = conn.cursor()
    ts = int(time.time())

    cur.execute("""
        INSERT INTO messages (
            room, sender_id, receiver_id,
            message_type,
            original_text, original_language,
            translated_text, translated_language,
            audio_format, audio_bytes,
            file_path, is_read, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0, %s)
    """, (
        room, sender_id, receiver_id,
        message_type,
        original_text, original_language,
        translated_text, translated_language,
        audio_format, audio_bytes,
        file_path, ts
    ))
    conn.commit()
    cur.close()
    conn.close()

def load_messages(room: str, viewer_email: str, limit: int = 50) -> List[Dict]:
    """
    Load messages for a given room ordered by created_at DESC.
    Also marks messages as read where receiver==viewer and is_read==0.
    """
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Fetch
    cur.execute("""
        SELECT *
        FROM messages
        WHERE room = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (room, limit))
    messages = cur.fetchall()

    # Mark as read for this viewer
    cur2 = conn.cursor()
    cur2.execute("""
        UPDATE messages
        SET is_read = 1
        WHERE room = %s AND receiver_id = %s AND is_read = 0
    """, (room, viewer_email.strip().lower()))
    conn.commit()
    cur2.close()

    cur.close()
    conn.close()
    return messages

def list_inbox_for(user_email: str) -> List[Dict]:
    """
    Return a list of peers the user has chatted with, the last message time,
    and unread counts from that peer.
    """
    me = user_email.strip().lower()
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # Group conversations by 'peer' (the other participant)
    cur.execute("""
        SELECT 
            CASE 
                WHEN sender_id = %s THEN receiver_id
                ELSE sender_id
            END AS peer,
            MAX(created_at) AS last_ts,
            SUM(CASE WHEN receiver_id = %s AND is_read = 0 THEN 1 ELSE 0 END) AS unread
        FROM messages
        WHERE sender_id = %s OR receiver_id = %s
        GROUP BY peer
        ORDER BY last_ts DESC
    """, (me, me, me, me))

    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows
