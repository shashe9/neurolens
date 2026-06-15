import re
from typing import Dict, Optional

class StructuringService:
    def __init__(self):
        # Transliteration glossary for Hinglish expressions
        self.glossary = {
            "ishaara": "pointing", "ishara": "pointing",
            "khaana": "food", "khana": "food",
            "bolna": "speaking", "bola": "said",
            "chala": "walked", "chalna": "walking",
            "aankh": "eye", "aankhen": "eyes",
            "kaan": "ear", "kaanon": "ears",
            "naak": "nose", "haath": "hand",
            "pair": "foot", "ungli": "finger",
            "ungliyon": "fingers", "angutha": "thumb",
            "anguthe": "thumb", "bolo": "speak",
            "bol": "speak", "bolta": "speaks",
            "bolti": "speaks", "baat": "talk",
            "baatein": "conversation", "pooch": "ask",
            "poochta": "asks", "poochti": "asks",
            "jawab": "answer", "suno": "listen",
            "dikhao": "show", "dekho": "look",
            "gussa": "anger", "gusse": "angry",
            "khush": "happy", "dukhi": "sad",
            "rota": "crying", "rote": "crying",
            "rona": "cry", "roti": "crying",
            "darr": "fear", "dost": "friend",
            "baccha": "child", "bacche": "child",
            "bacho": "child", "mummy": "mother",
            "papa": "father", "dada": "grandfather",
            "dadi": "grandmother", "gale": "hug",
            "khel": "play", "khelna": "play",
            "khelta": "playing", "khelti": "playing",
            "khilona": "toy", "khilone": "toys",
            "gudiya": "doll", "chal": "walk",
            "chalta": "walking", "chalti": "walking",
            "daud": "run", "daudta": "running",
            "daudti": "running", "kood": "hop",
            "koodna": "hopping", "chadha": "climbed",
            "chadhna": "climb", "seedhi": "stairs",
            "seedhiyan": "stairs", "seedhiyon": "stairs",
            "chammach": "spoon", "plate": "plate",
            "dabba": "box", "dabbe": "box",
            "gadi": "car", "gaadi": "car",
            "dekhta": "looks", "dekhte": "looking",
            "dekha": "looked", "dekhkar": "looking",
            "aaya": "came", "daal": "put",
            "daala": "put", "daali": "put",
            "rakha": "kept", "rakhi": "kept",
            "bataya": "told", "bina": "without",
            "atkan": "stutter", "atke": "stutter",
            "anjaan": "stranger", "pata": "knows",
            "kahani": "story", "sach": "real",
            "jaise": "similar", "sath": "together",
            "alag": "different", "bana": "make",
            "nahi": "not", "hota": "is", "hai": "is", "ko": "to", "ke": "of", "liye": "for",
            "karta": "does", "karti": "does", "krta": "does", "krti": "does", "kya": "what",
            "bhi": "also", "ek": "one", "aur": "and", "se": "with"
        }

        # Multi-word phrase mappings for common Hinglish structures
        self.phrase_mappings = [
            (r"\bbaccha khilona lane ke liye bolta hai\b", "Child asks to bring the toy"),
            (r"\bbaccha khilona lane ke liye bolta\b", "Child asks to bring the toy"),
            (r"\bkhilona lane ke liye bolta hai\b", "Asks to bring the toy"),
            (r"\bishaara karta hai\b", "points"),
            (r"\bishara karta hai\b", "points"),
            (r"\bishaara karti hai\b", "points"),
            (r"\bishara karti hai\b", "points"),
            (r"\bbolta hai\b", "speaks"),
            (r"\bbolti hai\b", "speaks"),
            (r"\brota hai\b", "cries"),
            (r"\broti hai\b", "cries"),
            (r"\bchalna seekh gaya\b", "learned to walk"),
            (r"\bchalne laga hai\b", "has started walking"),
            (r"\baankh milata hai\b", "makes eye contact"),
            (r"\baankh milati hai\b", "makes eye contact"),
            (r"\beye contact nahi karta\b", "does not make eye contact"),
            (r"\beye contact nahi karti\b", "does not make eye contact"),
            (r"\bapne naam par dekhta hai\b", "looks when their name is called"),
            (r"\bnaam bolne par dekhta hai\b", "looks when their name is called"),
            (r"\bnaam par respond karta hai\b", "responds to their name"),
            (r"\bnaam par respond karti hai\b", "responds to their name"),
        ]

    def structure_text(self, text: str) -> str:
        """
        Translates raw Hinglish/English text into structured English observations.
        Uses exact phrase match mappings first, then falls back to word-by-word glossary transliteration.
        """
        cleaned_text = text.strip()
        if not cleaned_text:
            return ""

        # 1. Attempt phrase-based translation first
        lower_text = cleaned_text.lower()
        for pattern, replacement in self.phrase_mappings:
            if re.search(pattern, lower_text):
                # Apply replacement
                lower_text = re.sub(pattern, replacement.lower(), lower_text)
                
        # Let's do word-by-word substitution on the translated/partially translated text
        words = re.findall(r"\b\w+\b", lower_text)
        translated_words = []
        for w in words:
            translated_words.append(self.glossary.get(w, w))
            
        result = " ".join(translated_words)
        
        # Clean up common grammar glitches from raw word substitution
        result = re.sub(r"\bis is\b", "is", result)
        result = re.sub(r"\bchild speaks\b", "Child speaks", result)
        result = re.sub(r"\bchild asks\b", "Child asks", result)
        result = re.sub(r"\bchild points\b", "Child points", result)
        result = re.sub(r"\bchild walks\b", "Child walks", result)
        result = re.sub(r"\bchild is\b", "Child is", result)
        
        # Clean up spacing
        result = re.sub(r"\s+", " ", result).strip()
        
        # Capitalize and add period if missing
        if result:
            result = result[0].upper() + result[1:]
            if not result.endswith((".", "!", "?")):
                result += "."
                
        return result
