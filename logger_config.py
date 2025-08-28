import logging
import sys

# Configure root logger
logging.basicConfig(
    level=logging.INFO, 
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  
    ]
)

logger = logging.getLogger("VoiceChatApp")
