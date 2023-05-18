from functools import wraps
from telegram import ChatAction
from firebase_admin import db
from datetime import datetime


def ultimo_registro_diario(campo_id):
    """
    Devuelve toda la informacion diaria de un campo
    """
    d = {}
    _diaria_data = db.reference(f"campo/{campo_id}/diaria/").get()
    if _diaria_data:
        for k, v in _diaria_data.items():
            valor = 0
            try:
                valor = int(v)
            except:
                pass 
            d[k] = valor
    return d

def ultimo_registro_produccion(campo_id):
    """
    Retorna el ultimo registro del campo al
    momento de la solicitud
    """
    d = {}
    response = db.reference(f'campo/{campo_id}/historico').\
                order_by_key().\
                limit_to_last(1).\
                get()
    if response:
        for k, v in response.items():
            v.update({'periodo': datetime.strptime(k, '%Y-%m-%d').strftime('%Y-%m-%d')})
            d = v 
    return d


def get_info_campo(user_id):
    """
    Devuelve los id de los usuarios de telegram 
    registrados en firebase
    """
    r = {}
    _user_data = db.reference(f"user/{user_id['id']}").get()
    if _user_data:
        campo_id = _user_data.get('campo_id', None)
        if campo_id:
            info_diaria_campo = ultimo_registro_diario(campo_id)
            info_historica_campo = ultimo_registro_produccion(campo_id)
            r.update(info_historica_campo)
            r.update(info_diaria_campo)
            if info_diaria_campo and not info_historica_campo:
                #Agregar el periodo
                r.update({'periodo':datetime.now().strftime('%Y-%m-%d')})
    return r


def get_firebase_uid():
    """
    Devuelve los id de los usuarios de telegram 
    registrados en firebase
    """
    _user_data = db.reference("user").get()
    return list(map(int, _user_data.keys()))


def send_typing_action(func):
    """Sends typing action while processing func command."""
    @wraps(func)
    def command_func(cls, update, context, *args, **kwargs):
        context.bot.send_chat_action(chat_id=update.effective_message.chat_id, action=ChatAction.TYPING)
        return func(cls, update, context,  *args, **kwargs)
    return command_func


def restricted(func):
    """Restrict usage of func to allowed users only and replies if necessary"""
    @wraps(func)
    def wrapped(cls, update, context, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in get_firebase_uid(): 
            print("WARNING: Unauthorized access denied for {}.".format(user_id))
            update.message.reply_text('User disallowed.')
            return  # quit function
        return func(cls, update, context,  *args, **kwargs)
    return wrapped