
import os
import google.generativeai as generativeai

class GeminiModel:
    def __init__(self, name="gemini-2.5-flash"):
        generativeai.configure(api_key="AIzaSyDPnmPNs6PpUD0wf-pbRFTdxJInAVoiYZc")
        self.model = generativeai.GenerativeModel(model_name=name)

    def SummarizeDoc(self, docData):
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
            response = self.model.generate_content(prompt)
            if response and response.text:
                return {"Success":True,"response":response.text.strip()}
            return {"Success":False,"response":"No translation generated."}
        except Exception as e:
            return {"Success":False,"response":f"Error during translation: {str(e)}"}

    def translate(self, inputText, fromLanguage, toLanguage):
        try:
            prompt = f"""
            Carefully understand the following text written in {fromLanguage}.
            Translate it into {toLanguage} **without losing meaning** or altering tone. 
            Make it natural and fluent.
            If the text contains domain-specific terms, try to preserve their meaning as accurately as possible.
            **Only provide the translation as output**, no explanations, no notes, no examples.

            Text:
            {inputText}
            """
            response = self.model.generate_content(prompt)
            if response and response.text:
                return {"Success":True,"response":response.text.strip()}
            return {"Success":False,"response":"No translation generated."}
        except Exception as e:
            return {"Success":False,"response":f"Error during translation: {str(e)}"}
    
    def detect_language(self, inputText):
        try:
            Prompt = f"""
                Detect the language of the following text and return ONLY the language 
                name (like English, Hindi, Telugu, Spanish, etc.) without extra explanation or translation.
                
                Text:
                {inputText}
                """

 
            response = self.model.generate_content(Prompt)
            
            if response and response.text:
                return {"Success":True,"response":response.text.strip()}
            return {"Success":False,"response":"Unable To Detect Language"} 
        except Exception as e:
            return {"Success":False,"response":f"Error in detect_language: {str(e)}"}
            
