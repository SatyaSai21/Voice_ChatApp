---

#### Voice Chat Messenger for Mute and Normal Users

A real-time chat messenger built with Streamlit, featuring:

* Text messaging
* Voice messages powered by Murf TextToSpeech
* File & image storage in AWS S3
* MySQL database for chat history and metadata
* Supports **text + audio + file + image messages**

## Features

### Secure User Login

* Users can register and log in with password encrypted using bcrypt.

### Text + Audio Messaging

* Messages are stored as text and also converted to audio (via Murf TTS).
* Makes the app especially useful for mute people, who can type and have their message delivered as speech.

### File & Image Sharing

* Upload images, documents, or any file.
* Files are securely stored in AWS S3 and shared via accessible URLs directly inside the chat.

### Chat History

* All messages, audio and file URLs are stored in MySQL.
* Easy retrieval when users reopen the chat.

### Room Creation Security Check

* Chat rooms are created only if the peer exists.
* Prevents ghost rooms (empty or unused rooms).

---

## Unique Features : What Makes My APP Different and Unique From Others

- **Text-to-Speech for mute users**:

  - A typed message is converted into a voice message for the receiver (via Murf TextToSpeech).
  - Hence,Making it useful for Mute People to send what they want to speak through text,but message will be delivered to receiver as if the sender is speaking.

- **Security check for rooms**: Prevents ghost rooms by verifying peer existence before creation.

- **Summarize and send**:

  - Upload a PDF, generate a summary, and send the summary instead of the full file (ideal for sharing articles,notes).
  - Used Gemini AI to generate summary of not more than 300 words.

- **Self-chat**: Personal room for storing notes and messages to self.

- **Auto-translate with Gemini AI**:

  - Messages are automatically translated into the receiver’s preferred language.
  - Receiver always hears messages in their own language.
  - Example: User can send text in any language (ex.TELUGU, not supported by Murf AI)->used Gemini AI to detect the sender language and to Translate it into Receiver's Language.Hence receiver can receive and listen messages in his preferred language(Which is Set at the time of signup).

- **Ensuring Message Delivery**: If Gemini AI translation fails, the original message is still delivered ,but in sender's language.

- **Multi-modal chat**: Every message exists as both text and audio.

---

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: MySQL
- **Storage**: AWS S3 (files, images)
- **Voice**: Murf TTS SDK
- **Translation**: Gemini AI

---

## Setup

### Install dependencies

```bash
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file with:

```ini
MURF_API_KEY=your_api_key

GEMINI_API_KEY=your_gemini_api_key

SQL_USER=your_db_user
SQL_PWD=your_db_password
SQL_DB=your_db_name
SQL_HOST=your_db_host

AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=your_aws_region
AWS_BUCKET_NAME=your_aws_bucket_name

```

### Run the app

```bash
streamlit run main.py
```

---

## Live Demo

[Live App Link](https://voicechatappformutists.streamlit.app/)

---

## Sample Credentials

You can use the following test accounts to log in:

- **User-1** :

  - **Email**: one@gmail.com
  - **Password**: Qwert@123

- **User-2** :
  - **Email**: two@gmail.com
  - **Password**: Qwert@123

(Or register a new account from the home screen.)

---
