import requests
from typing import Dict, Optional

from com.mhire.config.config import Config

class Translation:
    def __init__(self, config: Config):
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {self.config.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Translation system prompts
        self.translation_prompts = {
            ("ar", "en"): "You are a direct Arabic-to-English translator. Output ONLY the translated text — no explanations, no commentary. Translate naturally, preserving religious and cultural context where applicable:",
            ("ar", "de"): "You are a direct Arabic to German translator. Output ONLY the translated text — no explanations, no commentary. Translate naturally, preserving accurate grammer, sentence structure, and cultural context where applicable:",
            ("en", "ar"): "You are a direct English to Arabic translator. Output ONLY the translated text — no explanations, no commentary. Translate naturally, preserving accurate grammer, sentence structure, and cultural context where applicable:",
            ("en", "de"): "You are a direct English to German translator. Output ONLY the translated text — no explanations, no commentary. Translate naturally, preserving accurate grammer, sentence structure, and cultural context where applicable:",
            ("de", "ar"): "You are a direct German to Arabic translator. Output ONLY the translated text — no explanations, no commentary. DON'T INCLUDE any explanations, questions, or other text. Translate naturally, preserving accurate grammer, sentence structure, and cultural context where applicable:",
            ("de", "en"): "You are a direct German to English translator. Output ONLY the translated text — no explanations, no commentary. Translate naturally, preserving accurate grammer, sentence structure, and cultural context where applicable:"
        }
        
        # Language mapping
        self.languages = {
            "Auto": None,
            "Arabic": "ar",
            "English": "en",
            "German": "de"
        }

    def translate_text(self, text: str, src_lang: str, tgt_lang: str) -> str:
        """Translate text using Groq's LLaMA API"""
        if not text.strip():
            return ""
            
        if src_lang == tgt_lang:
            return text
        
        try:
            # Get the appropriate translation prompt
            lang_pair = (src_lang, tgt_lang)
            if lang_pair in self.translation_prompts:
                completion = requests.post(
                    self.config.GROQ_TRANSLATION_ENDPOINT,
                    headers=self.headers,
                    json={
                        "model": self.config.GROQ_TRANSLATION_MODEL,
                        "messages": [
                            {"role": "system", "content": self.translation_prompts[lang_pair]},
                            {"role": "user", "content": text}
                        ],
                        "temperature": 0.3,
                        "max_tokens": 2048
                    }
                )
                
                if completion.status_code == 200:
                    translated_text = completion.json()['choices'][0]['message']['content']
                    return self.clean_translation(translated_text).strip()
                else:
                    print(f"Translation error: {completion.text}")
                    return f"[Translation error: {completion.status_code}]"
            else:
                return f"[Unsupported language pair: {src_lang}->{tgt_lang}]"
                
        except Exception as e:
            print(f"Translation error: {e}")
            return f"[Error: {str(e)}]"

    def clean_translation(self, text: str) -> str:
        """Clean up translation output to remove any meta text"""
        # Remove common prefixes that might appear
        prefixes_to_remove = [
            "Translation:", "Here's the translation:", "Translated text:",
            "Here is the translation:", "Arabic translation:", "English translation:",
            "German translation:", "The translation is:", "Please find the translation below:",
        ]
        
        cleaned = text.strip()
        for prefix in prefixes_to_remove:
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix):].strip()
        
        # Remove any lines that look like instructions or meta text
        lines = cleaned.split('\n')
        content_lines = [line for line in lines if not any(
            indicator in line.lower() for indicator in 
            ["translate", "translation", "please", "here", "you would like", "text:", "note:"]
        )]
        
        return ' '.join(content_lines).strip()

    def get_language_code(self, language_name: str) -> Optional[str]:
        """Get language code from language name"""
        return self.languages.get(language_name)

    def get_supported_languages(self) -> Dict[str, Optional[str]]:
        """Get dictionary of supported languages"""
        return self.languages