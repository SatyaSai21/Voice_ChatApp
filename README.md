## Voice Chat Messenger Especially for Mute People along with Normal Users.

A real-time chat messenger built with Streamlit, featuring:

Text messaging

Voice messages powered by Murf TextToSpeech

File & image Stored in AWS S3 bucket and shared

MySQL database for chat history & metadata

# Features

Secure User Login

Users register & login with encrypted passwords.

Text + Audio Messaging (Messages are converted to audio )

File & Image Sharing

Upload images, docs, or any file → Stored securely in AWS S3.

Shared files are accessible directly inside the chat.

Chat History

All messages, audio links, and file URLs are stored in MySQL.

Easy retrieval when users reopen the chat.

Room Creation Security Check

Chat rooms created only if peer exists.

Optional request-accept flow before starting a conversation.

# UNIQUE FEATURES : What Makes My APP Different and Unique From Others

Type a message → Receiver gets text + generated voice message (via Murf TextToSpeech).Hence,Making it useful for Mute People to send what they want to speak through text,but message will be delivered to receiver as if the sender is speaking.

Security Check before creating Room, To avoid Ghost Rooms (Rooms that have no reason to exist,reciever doesn't exist).

Summarize and Send Option,User can upload a PDF and send summary of that pdf instead of pdf file.Useful for sending Articles etc.

Allows Personal Room for user to store or message to user itself (SELF-CHAT).

AutoTranslate Using GEMINI AI,leveraged Gemini AI to translate user's message to language of reciever,so receiver always listens messages in his/her own language.

Therefore User can send text in any language (ex.TELUGU, which is not available in Murf AI TTS)->used Gemini AI to detect the sender language and used Gemini AI to Translate it into Receiver's Language.Hence receiver can receive and listen messages in his preferred language(Which is Set at the time of signup).

Incase of GEMINI AI Failure To translate receiver still recieves message (Ensuring Message Delivery)

Text + Audio → Every message has both forms.

It is a multi-modal chat app — not just text, but voice and file sharing too.

# Tech Stack

Frontend: Streamlit

Backend: Python

Database: MySQL

Storage: AWS S3 (files, images)

Voice: Murf TTS SDK

# Setup

Install dependencies

pip install -U streamlit murf bcrypt python-dotenv mysql-connector-python boto3

Set environment variables (in .env)

MURF_API_KEY=your_api_key
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_BUCKET_NAME=your_bucket_name
DB_HOST=localhost
DB_USER=user
DB_PASSWORD=password
DB_NAME=dbname

Run app

streamlit run main.py
