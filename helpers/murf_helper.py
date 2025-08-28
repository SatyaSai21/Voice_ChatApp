# --------------------------
# Murf TEXT_TO_SPEECH
# --------------------------
import base64
import streamlit as st
from typing import Optional
from murf import Murf


@st.cache_resource(show_spinner=False)
def murf_client(api_key: Optional[str] = None) -> Murf:
    return Murf(api_key=api_key)  # your existing behavior

def tts_to_bytes(client: Murf, text: str, voice_id: str, *,
                 audio_format: str = "MP3",
                 sample_rate: int = 44100,
                 channel_type: str = "MONO",
                 style: Optional[str] = None,
                 rate: Optional[int] = None,
                 pitch: Optional[int] = None,
                 multi_native_locale: Optional[str] = None,
                 pronunciation_dictionary: Optional[dict] = None) -> bytes:
    """Call Murf TTS and return raw audio bytes from base64 response."""
    kwargs = dict(
        text=text,
        voice_id=voice_id,
        format=audio_format,
        sample_rate=sample_rate,
        channel_type=channel_type,
        encode_as_base_64=True,
    )
    
    if (multi_native_locale is not None) and multi_native_locale != "en-US":
        kwargs["multi_native_locale"] = multi_native_locale
    if style is not None:
        kwargs["style"] = style
    if rate is not None:
        kwargs["rate"] = rate
    if pitch is not None:
        kwargs["pitch"] = pitch
    if pronunciation_dictionary:
        kwargs["pronunciation_dictionary"] = pronunciation_dictionary
    #print("--------00000000-------------")
    res = client.text_to_speech.generate(**kwargs)
    encoded = getattr(res, "encoded_audio", None) or getattr(res, "encodedAudio", None)
    if not encoded:
        raise RuntimeError("Murf SDK did not return Base64 audio. Ensure encode_as_base_64=True is supported.")
    #print("--------11111111-------------")
    return base64.b64decode(encoded)
