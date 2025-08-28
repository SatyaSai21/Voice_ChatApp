

import os
import time
import streamlit as st
from datetime import datetime
from translator import GeminiModel
from streamlit_autorefresh import st_autorefresh
from constants import SUPPORTED_LANGUAGES
from datetime import datetime
from gemini import Gemini
from mysql.connector import Error
from dotenv import load_dotenv
load_dotenv()

from db import init_db
from user_helper import create_user,authenticate_user,get_user,get_user_language
from message_helper import save_message,load_messages,peer_exists,list_inbox_for,room_id_for,ensure_room_exists
from murf_helper import murf_client,tts_to_bytes
from s3bucket import upload_file_to_s3

# --------------------------
# Streamlit UI
# --------------------------
def main():
    GeminiAI = GeminiModel()
    st.set_page_config(page_title="Voice Chat (Murf TTS)", page_icon="🔊", layout="wide")
    st.title("🔊 Voice Chat Messenger (Murf TTS)")
    st.caption("Type a message and your friend receives both text and synthesized audio.")

    init_db()

    # Keep selected peer in session for inbox -> open chat
    if "peer" not in st.session_state:
        st.session_state["peer"] = ""

    with st.sidebar:
        st.header("Account")
        if 'user' not in st.session_state:
            with st.expander("Log in", expanded=True):
                login_email = st.text_input("Gmail", key="login_email")
                login_password = st.text_input("Password", type="password", key="login_password")
                if st.button("Log in"):
                    ok, user, msg = authenticate_user(login_email, login_password)
                    if ok:
                        st.session_state['user'] = user
                        st.success(msg)
                        st.session_state["rerun"] = not st.session_state.get("rerun", False)
                        st.stop()
                    else:
                        st.error(msg)

            with st.expander("Register new account"):
                reg_email = st.text_input("Gmail (must be @gmail.com)", key="reg_email")
                reg_name = st.text_input("Display name (optional)", key="reg_name")
                reg_gender = st.selectbox("Gender", ['male', 'female', 'others'])
                reg_password = st.text_input("Password (min 8 chars)", type="password", key="reg_password")

                reg_language = st.selectbox(
                    "Enter Your Preferred Language",
                    list(SUPPORTED_LANGUAGES.keys()),
                    format_func=lambda x: SUPPORTED_LANGUAGES[x]
                )

                if st.button("Create account"):
                    default_voice = "en-US-ken"
                    if reg_gender.lower() in ("female",):
                        default_voice = "en-US-natalie"

                    ok, msg = create_user(
                        reg_email,
                        reg_password,
                        reg_language,
                        reg_gender,
                        default_voice,
                        reg_name
                    )
                    if ok:
                        st.success(msg)
                    else:
                        st.error(msg)
        else:
            user = st.session_state['user']
            st.success(f"Signed in as {user['display_name']} ({user['email']})")
            if st.button("Log out"):
                del st.session_state['user']
                st.session_state["rerun"] = not st.session_state.get("rerun", False)
                st.stop()

        st.header("Settings")
        default_voice = st.text_input(
            "Voice ID",
            value=(st.session_state.get('user', {}) or {}).get('preferred_voice', 'en-US-natalie'),
            help="Pick a Murf voice ID ",
            disabled=True
        )
        preferred_lang = (st.session_state.get('user', {}) or {}).get('preferred_language', "en-US")

        audio_format = st.selectbox("Format", ["MP3", "WAV", "FLAC"], index=0)
        sample_rate = st.selectbox("Sample rate", [24000, 44100, 48000], index=1)
        channel_type = st.selectbox("Channel", ["MONO", "STEREO"], index=0)
        style = st.text_input("Style (optional)", value=None)
        rate = st.slider("Rate (−100..+100)", min_value=-100, max_value=100, value=0)
        pitch = st.slider("Pitch (−100..+100)", min_value=-100, max_value=100, value=0)

        st.divider()
        st.caption("Users & Room")
        if 'user' not in st.session_state:
            st.info("Please log in to start chatting.")
            me = ''
        else:
            me = st.session_state['user']['email']
            st.text_input("You (gmail)", value=me, disabled=True)

        # Inbox: show peers with unread counts and open buttons
        if me:
            st.subheader("📥 Inbox")
            inbox = list_inbox_for(me)
            if not inbox:
                st.caption("No conversations yet.")
            else:
                for row in inbox:
                    peer_email = row["peer"]
                    unread = int(row["unread"] or 0)
                    last_ts = row["last_ts"]
                    line = f"{peer_email}"
                    if unread > 0:
                        line += f"  •  🔔 Unread: {unread}"
                    if st.button(f"Open chat: {line}", key=f"inbox_{peer_email}"):
                        st.session_state["peer"] = peer_email
                        st.session_state["rerun"] = not st.session_state.get("rerun", False)
                        st.rerun()

        # Peer select / input (pre-filled from Inbox selection)
        peer = st.text_input("Chat with (gmail)", value=st.session_state.get("peer", ""))

        if me and peer:
            rid = room_id_for(me, peer)
            st.write("Room:", f"`{rid}`" if rid else "Not a valid room")

    if 'user' not in st.session_state:
        st.info("Log in to view and send messages.")
        return
    if not (me and peer):
        st.info("Enter your peer's Gmail in the sidebar to start chatting.")
        return

    # Enforce: only create room if peer exists
    if not peer_exists(peer):
        st.error("Peer not found. Please ask your friend to register first.")
        return

    client = murf_client(os.getenv("MURF_API_KEY"))
    left, right = st.columns([2, 1])

    with left:
        st.subheader("Conversation")

        # Ensure room exists here (on view)
        rid = ensure_room_exists(me, peer)
        room = rid or room_id_for(me, peer)

        st_autorefresh(interval=300000, key="chat_refresh")

        msgs = load_messages(room, me)
        if not msgs:
            st.write("No messages yet. Start the conversation below!")
        else:
            for msg in msgs:
                _id = msg["id"]
                sender = msg["sender_id"]
                receiver = msg["receiver_id"]
                message_type = msg["message_type"]
                original_text = msg["original_text"]
                original_language = msg["original_language"]
                translated_text = msg["translated_text"]
                translated_language = msg["translated_language"]
                audio_format = msg["audio_format"]
                audio_bytes = msg["audio_bytes"]
                file_path = msg["file_path"]
                ts = msg["created_at"]

                is_me = sender.strip().lower() == me.strip().lower()
                bubble = st.chat_message("user" if is_me else "assistant")

                header = f"{sender} · {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}"

                if message_type == "text":
                    if is_me:
                        content = original_text
                        bubble.markdown(f"{header}\n\n{content}")
                    else:
                        content = translated_text if translated_text else original_text
                        bubble.markdown(f"{header}\n\n{content}")
                        if audio_bytes:
                            bubble.audio(audio_bytes, format=f"audio/{audio_format.lower()}")

                elif message_type in ["image", "file", "pdf"]:
                    bubble.markdown(header)
                    if file_path:
                        if message_type == "image":
                            bubble.image(file_path, caption=original_text or "Image")
                        else:
                            bubble.markdown(f"[📂 Download {message_type.upper()}]({file_path})")
                else:
                    bubble.markdown(f"{header}\n\nUnsupported message type")

    with right:
        uniqueIdentifier = st.session_state.get('user')['email'].split("@")[0]
        st.subheader("Send a message")

        tab_text, tab_image, tab_file = st.tabs(["Text", "Image", "File"])

        # ------------------ TEXT ------------------
        with tab_text:
            with st.form("send_text", clear_on_submit=True):
                text = st.text_area("Type message", height=120)
                submitted_text = st.form_submit_button("Send ➜")

            if submitted_text:
                if not text.strip():
                    st.warning("Please enter a message.")
                else:
                    # Enforce peer existence again on send (race-safe)
                    if not peer_exists(peer):
                        st.error("Peer not found. Please ask your friend to register first.")
                        st.stop()

                    # Detect sender language
                    detect_Response = GeminiAI.detect_language(text.strip())
                    sender_lang = detect_Response['response'] if detect_Response['Success'] else None

                    # Receiver preferred language (db stores locale code; mapping to human is in SUPPORTED_LANGUAGES)
                    recv_locale = get_user_language(peer) or "en-US"
                    receiver_lang = SUPPORTED_LANGUAGES.get(recv_locale, "English")

                    translated_text = None
                    final_text = text.strip()

                    # Translate if needed
                    if receiver_lang and sender_lang and sender_lang.lower() != receiver_lang.lower():
                        translated = GeminiAI.translate(final_text, sender_lang, receiver_lang)
                        if isinstance(translated, dict) and translated.get("Success") is False:
                            st.error(f"Translation failed: {translated.get('error')}")
                        else:
                            translated_text = translated['response'] if isinstance(translated, dict) else str(translated)
                            final_text = translated_text.strip()

                    # Convert final text to speech
                    audio_bytes = tts_to_bytes(
                        client,
                        final_text,
                        default_voice,
                        audio_format=audio_format,
                        sample_rate=int(sample_rate),
                        channel_type=channel_type,
                        style=style or None,
                        rate=rate,
                        pitch=pitch,
                    )

                    # Save message (unread for receiver)
                    try:
                        save_message(
                            room=room_id_for(me, peer),
                            sender_id=me,
                            receiver_id=peer,
                            message_type='text',
                            original_text=text.strip(),
                            original_language=sender_lang,
                            translated_text=translated_text,
                            translated_language=receiver_lang,
                            audio_format=audio_format,
                            audio_bytes=audio_bytes,
                            file_path=None
                        )
                        st.success("Text Sent!")
                        st.session_state["rerun"] = not st.session_state.get("rerun", False)
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))

        # ------------------ IMAGE ------------------
        with tab_image:
            imgs = st.file_uploader("Upload Image", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
            if imgs and st.button("Send Image ➜"):
                if not peer_exists(peer):
                    st.error("Peer not found. Please ask your friend to register first.")
                    st.stop()
                room_id=room_id_for(me, peer)
                for img in imgs:
                    filename = f"{uniqueIdentifier}_{img.name}"
                    file_bytes = img.read()

                    # Upload to S3 (public URL)
                    file_url = upload_file_to_s3(
                        file_bytes=file_bytes,
                        key=f"messages/{room_id}/{filename}",
                        content_type=img.type  # e.g. image/png
                    )
                    save_message(room_id, me, peer, 'image', file_path=file_url)
                st.success("Image Sent!")
                st.session_state["rerun"] = not st.session_state.get("rerun", False)
                st.rerun()

        # ------------------ FILE / PDF ------------------
        with tab_file:
            file = st.file_uploader("Upload File", type=["pdf", "txt", "docx"])
            
            if file:
                room_id=room_id_for(me, peer)
                if st.button("Send File ➜"):
                    if not peer_exists(peer):
                        st.error("Peer not found. Please ask your friend to register first.")
                        st.stop()
                    filename = f"{uniqueIdentifier}_{file.name}"
                    file_bytes = file.read()

                    # Upload to S3
                    file_url = upload_file_to_s3(
                        file_bytes=file_bytes,
                        key=f"messages/{room_id}/{filename}",
                        content_type=file.type  # application/pdf, text/plain, etc.
                    )
                        
                    save_message(room_id, me, peer, 'file', file_path=file_url)
                    st.success("File Sent!")
                    st.session_state["rerun"] = not st.session_state.get("rerun", False)
                    st.rerun()

                if file.type == "application/pdf" and st.button("Summarize & Send (Voice)"):
                    if not peer_exists(peer):
                        st.error("Peer not found. Please ask your friend to register first.")
                        st.stop()

                    from PyPDF2 import PdfReader
                    reader = PdfReader(file)
                    pdf_text = " ".join([p.extract_text() or "" for p in reader.pages])
                    summary = GeminiAI.SummarizeDoc(pdf_text)

                    if not summary.get("Success"):
                        st.error("PDF summarization failed")
                        st.stop()

                    summary_text = summary['response']
                    print(f"summary : {summary_text}\n")
                    audio_bytes = tts_to_bytes(
                        client,
                        summary_text,
                        st.session_state['user']['preferred_voice'],
                        audio_format=audio_format,
                        sample_rate=int(sample_rate),
                        channel_type=channel_type,
                        style=(style or None),
                        rate=rate,
                        pitch=pitch,
                    )
                    # Upload original PDF to S3 (so chat keeps a reference to it)
                    filename = f"{uniqueIdentifier}_{file.name}"
                    
                    file_bytes = file.getbuffer().tobytes()
                    file_url = upload_file_to_s3(
                        file_bytes=file_bytes,
                        key=f"messages/{room_id}/{filename}",
                        content_type="application/pdf"
                    )
                    save_message(
                        room=room_id,
                        sender_id=me,
                        receiver_id=peer,
                        message_type='text',
                        original_text=summary_text,
                        original_language="en",
                        translated_text=None,
                        translated_language=None,
                        audio_format=audio_format,
                        audio_bytes=audio_bytes,
                        file_path=file_url
                    )

                    st.success("PDF Summary Sent via Voice!")
                    st.session_state["rerun"] = not st.session_state.get("rerun", False)
                    st.rerun()

    st.divider()
    with st.expander("About this demo"):
        st.markdown(
            """
            • Rooms are created only when both users exist.\n
            • Inbox shows unread counts and lets receivers open chats.\n
            • Messages are marked read when the receiver opens the room.\n
            • Uses Murf TTS via Base64 so audio persists.\n
            """
        )

if __name__ == "__main__":
    main()