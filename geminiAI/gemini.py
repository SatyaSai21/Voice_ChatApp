import os
from google import genai
class Gemini:
    def __init__(self, api_key):
        self.Client=genai.Client(api_key=api_key)
    
    def GeminiSummarizeDoc(self, docData,model_name='gemini-2.5-flash'):
        try:
            prompt = f"""
            Carefully read the following text extracted from a document.
            Provide a clear, concise summary in **no more than 300 words**.
            Preserve the main ideas and meaning, but avoid unnecessary details.
            Focus only on the key ideas, important details, and overall context. 
            Do not add extra commentary or assumptions.

            Text:
            {docData}
            """
            response = self.Client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return {"Success":True,"response":response.text.strip()}
            return {"Success":False,"response":"No translation generated."}
        except Exception as e:
            return {"Success":False,"response":f"Error during translation: {str(e)}"}

    def GeminiTranslate(self, inputText, fromLanguage, toLanguage,model_name='gemini-2.5-flash'):
        try:
            prompt = f"""
            Carefully understand the following text written in {fromLanguage}.
            Translate it into {toLanguage} **without losing meaning** or altering tone.
            Avoid literal word-for-word translation; make it natural and fluent.
            If the text contains domain-specific terms, try to preserve their meaning as accurately as possible.

            Text:
            {inputText}
            """
            response = self.Client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            if response and response.text:
                return {"Success":True,"response":response.text.strip()}
            return {"Success":False,"response":"No translation generated."}
        except Exception as e:
            return {"Success":False,"response":f"Error during translation: {str(e)}"}
    
    def GeminiDetect_language(self, inputText,model_name='gemini-2.5-flash'):
        try:
            prompt = f"""
                Detect the language of the following text and return ONLY the language 
                name (like English, Hindi, Telugu, Spanish, etc.) without extra explanation or translation.
                
                Text:
                {inputText}
                """

 
            response = self.Client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            
            if response and response.text:
                return {"Success":True,"response":response.text.strip()}
            return {"Success":False,"response":"Unable To Detect Language"} 
        except Exception as e:
            return {"Success":False,"response":f"Error in detect_language: {str(e)}"}
            

if __name__ == "__main__":
    t=Gemini(os.getenv("GEMINI_API_KEY"))
    res1=t.GeminiDetect_language("बच्चों के लिए हिंदी कहानियाँ सिर्फ मनोरंजन का साधन नहीं हैं, बल्कि शिक्षा का भी एक महत्वपूर्ण माध्यम हैं। ये कहानियाँ बच्चों को नैतिक शिक्षा और प्रेरणा प्रदान करती हैं, साथ ही उन्हें जीवन जीने का सही तरीका भी सिखाती हैं।")
    print(res1)
    res2=t.GeminiTranslate("बच्चों के लिए सिर्फ मनोरंजन का साधन नहीं होती, बल्कि उन्हें जीवन की मूल बातें सिखाने का एक शक्तिशाली तरीका भी होती है। जब कभी भी कहानियों का जिक्र होता है तब बच्चो का भी जिक्र जरुर से किया जाता है, ऐसा इसलिए क्यूंकि Hindi Short Story मुख्य रूप से बच्चों को ही सबसे ज्यादा पसदं होती है। बच्चों के लिए नैतिक शिक्षा वाली कहानियां ही वो माध्यम हैं जिससे यक़ीनन उन्हें नयी प्रेरणा मिलती है और साथ ही जीवन को सही तरीके से जीने का सिख मिलती है।","Hindi","English")
    print(res2)