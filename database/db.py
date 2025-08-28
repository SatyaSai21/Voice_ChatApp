# --------------------------
# Storage (MYSQL)
# --------------------------
import os
import mysql.connector

from dotenv import load_dotenv
load_dotenv()

DB_CONFIG = {
    "host": os.getenv("SQL_HOST"),
    "user": os.getenv("SQL_USER"),
    "password":os.getenv("SQL_PWD"),
    "database": "railway",
    "port":14647
    
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            email VARCHAR(255) NOT NULL UNIQUE,
            display_name VARCHAR(255),
            password_hash BLOB NOT NULL,
            preferred_language VARCHAR(100) DEFAULT 'en-US', 
            gender VARCHAR(16),
            preferred_voice VARCHAR(100) DEFAULT 'en-US-natalie', 
            created_at BIGINT NOT NULL,
            CONSTRAINT chk_gender CHECK (gender IN ('male','female','other','others'))
        )
    """)

    # Rooms table — ensures we only create room if both peers exist and we can list chats cleanly
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rooms (
            id INT AUTO_INCREMENT PRIMARY KEY,
            room_id VARCHAR(255) NOT NULL UNIQUE,
            user1_email VARCHAR(255) NOT NULL,
            user2_email VARCHAR(255) NOT NULL,
            created_at BIGINT NOT NULL,
            INDEX idx_user1 (user1_email),
            INDEX idx_user2 (user2_email)
        )
    """)

    # Messages table (added is_read + helpful indexes)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            room VARCHAR(255) NOT NULL,
            sender_id VARCHAR(255) NOT NULL,
            receiver_id VARCHAR(255) NOT NULL,

            -- message type: text, audio, image, file, pdf
            message_type VARCHAR(100) NOT NULL,

            -- Original text if applicable
            original_text TEXT,
            original_language VARCHAR(50),

            -- Translated version (for receiver’s preferred language)
            translated_text TEXT,
            translated_language VARCHAR(50),

            -- For audio messages
            audio_format VARCHAR(20),
            audio_bytes LONGBLOB,

            -- For file/image/pdf messages
            file_path VARCHAR(500),

            is_read TINYINT(1) NOT NULL DEFAULT 0,
            created_at BIGINT NOT NULL,
            INDEX idx_room_created (room, created_at DESC),
            INDEX idx_receiver_read (receiver_id, is_read, created_at DESC)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()

