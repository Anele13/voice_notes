
import speech_recognition as sr
import pandas as pd
import es_core_news_sm
from spacy.matcher import Matcher

CATEGORIAS={
    'MUERTES': {'LEMMA':'morir'},
    'NACIMIENTOS' : {'LEMMA':'nacer'},
    'VENTAS': {'LEMMA':'vender'},
    'COMPRAS': {'LEMMA':'comprar'}
}

class VoiceNotes():
    text_from_voice = None 
    
    def set_text_from_voice(self, path):
        r = sr.Recognizer()
        audio=sr.AudioFile(path)
        with audio as source:
            audio = r.record(source)
        try:
            self.text_from_voice = r.recognize_google(audio, language = "es-AR")
        except Exception as e:
            pass
    
    def categorize(self,text):
        nlp = es_core_news_sm.load()
        doc = nlp(text)
        for categoria, regexp in CATEGORIAS.items():
            matcher = Matcher(nlp.vocab) 
            matcher.add("matching_father", [[regexp]])    
            matches = matcher(doc)
            if matches:
                return categoria

    def get_data(self):
        if self.text_from_voice:
            df = pd.DataFrame([self.text_from_voice],columns=['text'])
            text = df['text'][0]
            pattern_father = [[{'POS':'VERB'},{'POS':'NUM'}]]
            nlp = es_core_news_sm.load()
            doc = nlp(text)
            matcher = Matcher(nlp.vocab) 
            matcher.add("matching_father", pattern_father)    
            matches = matcher(doc)
            sub_text = ''
            df_final = pd.DataFrame()
            for match_id, start, end in matches:
                span = doc[start:end]
                sub_text = span.text
                tokens = sub_text.split(' ')
                categoria = self.categorize(tokens[0])
                df_final[categoria] = [tokens[1]]
            #respuesta = ''
            #for k,v in df_final.to_dict().items():
            #    respuesta = respuesta + f'{k} : {list(v.values())[0]}\n'
            return df_final.to_dict()
        return None

    def __init__(self, path):
        self.set_text_from_voice(path)
