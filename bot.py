from asyncore import dispatcher
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext, CallbackQueryHandler, ContextTypes)
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from pydub import AudioSegment
from voice_notes import VoiceNotes
from firebase import FirebaseDB
import os
from utils import send_typing_action, restricted, get_info_campo
import pandas as pd 

PORT = int(os.environ.get('PORT', 5000))
TOKEN = os.getenv('TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
LISTEN_PORT = os.getenv('LISTEN_PORT')
CARGANDO_ANIMALES, CARGANDO_OPCIONES, SWITCHING, INGRESANDO_OVEJAS, INGRESANDO_CARNEROS, INGRESANDO_CORDEROS= range(6)

class Command():
    f = FirebaseDB() 

    @classmethod
    @send_typing_action
    @restricted
    def start(self, update, context):
        context.bot.send_message(update.message.chat_id, "Ingrese el comando /actualizar_datos para registrar nuevos datos \
                                                            o /info para conocer sus datos actualizados")

    @classmethod
    @send_typing_action
    @restricted
    def cargar_datos_animales(self, update, context):
        reply_keyboard = [
                ["Ovejas", "Corderos"],
                ["Carneros"],
            ]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True)
        update.message.reply_text('Seleccione una categoria', reply_markup=markup)
        return CARGANDO_ANIMALES

    @classmethod
    @send_typing_action
    @restricted
    def cargar_opciones(self, update, context):
        animal_elegido = update.message.text
        context.user_data['categoria'] = animal_elegido.lower()[:-1] #Quita la s final de Ovejas, Carneros, Corderos
        keyboar_options = [['Ventas', 'Compras'],['Muertes']] 
        if animal_elegido == 'Corderos':
            keyboar_options[1].append('Pariciones')
        markup = ReplyKeyboardMarkup(keyboar_options, one_time_keyboard=True)
        update.message.reply_text('Seleccione una accion', reply_markup=markup)
        return SWITCHING


    @classmethod
    @send_typing_action
    @restricted
    def switching(self, update, context):
        accion_elegida = update.message.text
        match = {
            'Ventas':'vender',
            'Compras': 'comprar',
            'Pariciones': 'nacer',
            'Muertes': 'morir'
        }
        context.user_data["accion"] = match[accion_elegida]
        animal_elegido = context.user_data['categoria']
        if 'oveja' in animal_elegido:
            update.message.reply_text('Ingrese la cantidad de ovejas o /cancelar para cancelar el comando')
            return INGRESANDO_OVEJAS
        elif 'carnero' in animal_elegido:
            update.message.reply_text('Ingrese la cantidad de carneros o /cancelar para cancelar el comando')
            return INGRESANDO_CARNEROS
        update.message.reply_text('Ingrese la cantidad de corderos o /cancelar para cancelar el comando')
        return INGRESANDO_CORDEROS


    #############################################################3
    @classmethod
    @send_typing_action
    #@restricted
    def retry_ovejas(self, update, context):
        update.message.reply_text(f"las cantidades deben ser numeros mayores a 0. Reintente o /cancelar")
        return INGRESANDO_OVEJAS
    @classmethod
    @send_typing_action
    #@restricted
    def end_ovejas(self, update, context):
        cantidad_ovejas = update.message.text 
        data = context.user_data
        data.update({'cantidad': int(cantidad_ovejas)})
        df = pd.DataFrame(data, index=[0])
        self.f.send_realtime_data(update.message.from_user.id, df)
        update.message.reply_text(f"Ovejas actualizadas correctamente {cantidad_ovejas}")
        return ConversationHandler.END
    

    @classmethod
    @send_typing_action
    #@restricted
    def retry_carneros(self, update, context):
        update.message.reply_text(f"las cantidades deben ser numeros mayores a 0. Reintente o /cancelar")
        return INGRESANDO_CARNEROS
    @classmethod
    @send_typing_action
    #@restricted
    def end_carneros(self, update, context):
        cantidad_carneros = update.message.text 
        data = context.user_data
        data.update({'cantidad': int(cantidad_carneros)})
        df = pd.DataFrame(data, index=[0])
        self.f.send_realtime_data(update.message.from_user.id, df)
        update.message.reply_text(f"Carneros actualizados correctamente {cantidad_carneros}")
        return ConversationHandler.END



    @classmethod
    @send_typing_action
    #@restricted
    def retry_corderos(self, update, context):
        update.message.reply_text(f"las cantidades deben ser numeros mayores a 0. Reintente o /cancelar")
        return INGRESANDO_CORDEROS
    
    @classmethod
    @send_typing_action
    #@restricted
    def end_corderos(self, update, context):
        cantidad_corderos = update.message.text
        data = context.user_data
        data.update({'cantidad': int(cantidad_corderos)})
        df = pd.DataFrame(data, index=[0])
        self.f.send_realtime_data(update.message.from_user.id, df)
        update.message.reply_text(f"Corderos actualizados correctamente {cantidad_corderos}")
        return ConversationHandler.END


    @classmethod
    def cancelar(self, update, context):
        update.message.reply_text("Muchas Gracias :)")
        return ConversationHandler.END  


    @classmethod
    @send_typing_action
    @restricted
    def voice_processing(self, update, context):
        user = update.message.from_user
        try:
            filepath_origen = "archivo.ogg"
            filepath_destino = "archivo.ogg"
            with open(filepath_origen, 'wb') as f:
                context.bot.get_file(update.message.voice.file_id).download(out=f)
            AudioSegment.from_ogg(filepath_origen).export(filepath_destino, format='wav')
            vn = VoiceNotes(filepath_destino)
            data = vn.get_data()
            if not data.empty:
                self.f.send_realtime_data(user.id, data)
                respuesta = ''
                data_dict = {
                    'morir': 'muertes',
                    'nacer': 'pariciones',
                    'vender': 'ventas',
                    'comprar': 'compras'
                }
                for index, row in data.iterrows():
                    respuesta += f'{row.categoria} --> {data_dict.get(row.accion)}-{row.cantidad} \n'
                context.bot.send_message(update.message.chat_id, f"Datos actualizados correctamente: \n{respuesta}")
            else: 
                context.bot.send_message(update.message.chat_id, "No se pudo procesar el mensaje. Por favor reintente") 
        except Exception as e:
            print(e)
            context.bot.send_message(update.message.chat_id, "No se pudo procesar el mensaje. Por favor reintente") 


    @classmethod
    @send_typing_action
    @restricted
    def info_campo(self, update, context):
        user = update.message.from_user
        data = get_info_campo(user)
        if data:
            respuesta = f"Ultimo registro de su campo: \n{data['localidad']} - {data['periodo']} ✅ \n \n"
            data.pop('periodo')
            data.pop('localidad')
            respuesta += 'Datos Climaticos 🌤 \n'
            for k, v in data.items():
                if k in ['direccion_viento','humedad' ,'mm_lluvia' ,'temperatura_maxima' ,'temperatura_minima' ,'velocidad_viento']:
                    respuesta += f"{k}: {v} \n"
            
            data.pop('direccion_viento')
            data.pop('humedad') 
            data.pop('mm_lluvia') 
            data.pop('temperatura_maxima') 
            data.pop('temperatura_minima') 
            data.pop('velocidad_viento') 
            respuesta += '\n'
            respuesta += 'Datos de Producción 🐏 \n'
            for k, v in data.items():
                respuesta += f"{k}: {v} \n"
            context.bot.send_message(update.message.chat_id, respuesta)
        else:
            context.bot.send_message(update.message.chat_id, 'Su campo no posee registros.')


class Bot():
    dispatcher = None
    updater = None

    def __init__(self):
        self.updater = Updater(TOKEN, use_context=True)
        self.dispatcher= self.updater.dispatcher

    def add_commands(self):
        self.dispatcher.add_handler(CommandHandler('start', Command.start))
        self.dispatcher.add_handler(CommandHandler('info', Command.info_campo))
        self.dispatcher.add_handler(MessageHandler(Filters.voice, Command.voice_processing))

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler("actualizar_datos", Command.cargar_datos_animales)],
            states={
                CARGANDO_ANIMALES: [
                    MessageHandler(Filters.regex("^(Ovejas|Corderos|Carneros)$"), Command.cargar_opciones),
                ],
                SWITCHING: [
                    MessageHandler(Filters.regex("^(Muertes|Ventas|Pariciones|Compras)$"), Command.switching),
                ],
                INGRESANDO_OVEJAS: [
                    #Si la respuesta es un numero
                    MessageHandler(Filters.regex('^[0-9]+$') , Command.end_ovejas),
                    #Sino reintento o cancelo
                    MessageHandler((~Filters.regex('^[0-9]+$') & ~Filters.command), Command.retry_ovejas)
                ],
                INGRESANDO_CARNEROS: [
                    #Si la respuesta es un numero
                    MessageHandler(Filters.regex('^[0-9]+$') , Command.end_carneros),
                    #Sino reintento o cancelo
                    MessageHandler((~Filters.regex('^[0-9]+$') & ~Filters.command), Command.retry_carneros)
                ],
                INGRESANDO_CORDEROS: [
                    #Si la respuesta es un numero
                    MessageHandler(Filters.regex('^[0-9]+$') , Command.end_corderos),
                    #Sino reintento o cancelo
                    MessageHandler((~Filters.regex('^[0-9]+$') & ~Filters.command), Command.retry_corderos)
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