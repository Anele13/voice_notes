from functools import wraps
from telegram import ChatAction
from firebase_admin import db

def get_firebase_uid():
    """
    Devuelve los id de los usuarios de telegram 
    registrados en firebase
    """
    _user_data = db.reference(f"user").get()
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