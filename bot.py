from asyncore import dispatcher
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler)

from pydub import AudioSegment
from voice_notes import VoiceNotes
from firebase import FirebaseDB
import os
from utils import send_typing_action, restricted

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.getenv('TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
LISTEN_PORT = os.getenv('LISTEN_PORT')

CARGANDO, REINTENTANDO = range(2)
class Command():
    f = FirebaseDB() #TODO corregir esto

    @classmethod
    @send_typing_action
    @restricted
    def start_ovejas(self, update, context):
        update.message.reply_text('Ingrese la cantidad de ovejas o /cancelar para cancelar el comando')
        return CARGANDO


    @classmethod
    @send_typing_action
    #@restricted
    def retry_ovejas(self, update, context):
        cantidad_ovejas = update.message.text #TODO validar que sea entero --> filters de telegram
        update.message.reply_text(f"las cantidades deben ser numeros mayores a 0. Reintente o /cancelar")
        return CARGANDO


    @classmethod
    @send_typing_action
    #@restricted
    def end_ovejas(self, update, context):
        cantidad_ovejas = update.message.text #TODO validar que sea entero --> filters de telegram
        self.f.send_realtime_data(update.message.from_user.id, {'ovejas': int(cantidad_ovejas)})
        update.message.reply_text(f"Ovejas actualizadas correctamente {cantidad_ovejas}")
        return ConversationHandler.END
    

    @classmethod
    def cancelar(self, update, context):
        update.message.reply_text("Muchas Gracias :)")
        return ConversationHandler.END  


    @classmethod
    def voice_processing(self, update, context):
        user = update.message.from_user
        filepath_origen = "archivo.ogg"
        filepath_destino = "archivo.ogg"
        with open(filepath_origen, 'wb') as f:
            context.bot.get_file(update.message.voice.file_id).download(out=f)
        AudioSegment.from_ogg(filepath_origen).export(filepath_destino, format='wav')
        vn = VoiceNotes(filepath_destino)
        data = vn.get_data()
        if not data.empty:
            self.f.send_realtime_data(user.id, data)
            context.bot.send_message(update.message.chat_id, "Comando recibido")
        else: 
           context.bot.send_message(update.message.chat_id, "No se pudo procesar el mensaje. Por favor reintente") 


class Bot():
    dispatcher = None
    updater = None

    def __init__(self):
        self.updater = Updater(TOKEN, use_context=True)
        self.dispatcher= self.updater.dispatcher

    def add_commands(self):
        #self.dispatcher.add_handler(CommandHandler('start_ovejas', Command.start_ovejas))
        self.dispatcher.add_handler(MessageHandler(Filters.voice, Command.voice_processing))

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("cargar_ovejas", Command.start_ovejas)],
            states={
                CARGANDO: [
                    #Si la respuesta es un numero
                    MessageHandler(Filters.regex('^[0-9]+$') , Command.end_ovejas),
                    #Sino reintento o cancelo
                    MessageHandler((~Filters.regex('^[0-9]+$') & ~Filters.command), Command.retry_ovejas)
                ],
            },
            fallbacks=[CommandHandler("cancelar", Command.cancelar)],
        )
        self.dispatcher.add_handler(conv_handler)



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


"""
- todas las variables 
    'corderos': 0,
    'ovejas': 0,
    'carneros': 0,
    'pariciones': 0,
    'muertes_corderos': 0,
    'lana_producida': 0,
    'carne_producida': 0,
    'rinde_lana': 0,
    'finura_lana': 0,
"""