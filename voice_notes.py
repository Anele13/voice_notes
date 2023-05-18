
import speech_recognition as sr
import pandas as pd
import es_core_news_sm
from spacy.matcher import Matcher

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
    

    def get_data(self):
        df_final = pd.DataFrame(columns=['accion', 'cantidad', 'categoria'])
        if self.text_from_voice:
            df = pd.DataFrame([self.text_from_voice],columns=['text'])
            text = df['text'][0]
            pattern_father = [
                [{'POS':'VERB', 'LEMMA': 'morir'},{'POS':'NUM'}, {'POS':'NOUN', 'LEMMA': 'oveja'}],
                [{'POS':'VERB', 'LEMMA': 'vender'},{'POS':'NUM'}, {'POS':'NOUN', 'LEMMA': 'oveja'}],
                [{'POS':'VERB', 'LEMMA': 'comprar'},{'POS':'NUM'}, {'POS':'NOUN', 'LEMMA': 'oveja'}],

                [{'POS':'VERB', 'LEMMA': 'morir'},{'POS':'NUM'}, {'POS':'NOUN', 'LEMMA': 'carnero'}],
                [{'POS':'VERB', 'LEMMA': 'vender'},{'POS':'NUM'}, {'POS':'NOUN', 'LEMMA': 'carnero'}],
                [{'POS':'VERB', 'LEMMA': 'comprar'},{'POS':'NUM'}, {'POS':'NOUN', 'LEMMA': 'carnero'}],

                [{'POS':'VERB', 'LEMMA': 'nacer'},{'POS':'NUM'}, {'POS':'NOUN', 'LEMMA': 'cordero'}], #--> poner el lemma, el lemma lo transforma en singular
                [{'POS':'VERB', 'LEMMA': 'morir'},{'POS':'NUM'}, {'POS':'NOUN', 'LEMMA': 'cordero'}],
                [{'POS':'VERB', 'LEMMA': 'vender'},{'POS':'NUM'}, {'POS':'NOUN', 'LEMMA': 'cordero'}],
                [{'POS':'VERB', 'LEMMA': 'comprar'},{'POS':'NUM'}, {'POS':'NOUN', 'LEMMA': 'cordero'}],
            ]
            nlp = es_core_news_sm.load()
            doc = nlp(text)
            """
            for token in doc:
                # Find named entities, phrases and concepts
                print("...........>")
                print(token.text, token.lemma_, token.pos_, token.tag_, token.dep_, token.shape_, token.is_alpha, token.is_stop)
            """
            matcher = Matcher(nlp.vocab) 
            matcher.add("matching_father", pattern_father)    
            matches = matcher(doc)
            sub_text = ''
            for match_id, start, end in matches:
                span = doc[start:end]
                sub_text = span.lemma_ #span.text
                tokens = sub_text.split(' ')
                l=[]
                l.append(tokens[0])
                l.append(tokens[1])
                l.append(tokens[2])
                df_final = df_final.append(pd.Series(l, index=['accion', 'cantidad', 'categoria']), ignore_index=True)
            try:
                df_final.cantidad = df_final.cantidad.apply(lambda row: str(row).replace('.',''))
                df_final.cantidad = df_final.cantidad.astype('int64')
            except Exception as e:
                raise e
        return df_final

    def __init__(self, path):
        self.set_text_from_voice(path)
