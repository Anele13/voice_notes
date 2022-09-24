from asyncore import dispatcher
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters)
from pydub import AudioSegment
from voice_notes import VoiceNotes
from firebase import FirebaseDB
import os
from dotenv import load_dotenv

load_dotenv()

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.getenv('TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
LISTEN_PORT = os.getenv('LISTEN_PORT')

class Command():
    f = FirebaseDB() #TODO corregir esto

    @classmethod
    def start(self, update, context):
        # Enviar un mensaje a un ID determinado.
        context.bot.send_message(update.message.chat_id, "Bienvenido")
    
    @classmethod
    def ovejas(self, update, context):
        # Enviar un mensaje a un ID determinado.
        context.bot.send_message(update.message.chat_id, "Ovejas")
    
    @classmethod
    def vacas(self, update, context):
        # Enviar un mensaje a un ID determinado.
        context.bot.send_message(update.message.chat_id, "Vacas")
    
    @classmethod
    def voice_processing(self, update, context):
        user = update.message.from_user
        filepath_origen = "archivo.ogg"
        filepath_destino = "archivo.ogg"
        with open(filepath_origen, 'wb') as f:
            context.bot.get_file(update.message.voice.file_id).download(out=f)
        #Conversion de ogg a wav
        AudioSegment.from_ogg(filepath_origen).export(filepath_destino, format='wav')
        #Traduccion
        vn = VoiceNotes(filepath_destino)
        data = vn.get_data()
        if data:
            self.f.send_realtime_data(user.id, data)
            context.bot.send_message(update.message.chat_id, "Comando recibido")


class Bot():
    dispatcher = None
    updater = None

    def __init__(self):
        self.updater = Updater(TOKEN, use_context=True)
        self.dispatcher= self.updater.dispatcher

    def add_commands(self):
        self.dispatcher.add_handler(CommandHandler('ovejas', Command.ovejas))
        self.dispatcher.add_handler(MessageHandler(Filters.voice, Command.voice_processing))

    def start(self, environment):
        self.add_commands()
        if environment == '-l': #Local
            self.updater.start_polling()
        else:
            self.updater.start_webhook(listen=LISTEN_PORT, 
                                        port=int(PORT),
                                        url_path= TOKEN,
                                        webhook_url=WEBHOOK_URL+TOKEN)
        self.updater.idle()

if __name__ == '__main__':
    environment = '-l'
    bot = Bot()
    bot.start(environment)