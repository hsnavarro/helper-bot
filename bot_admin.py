from functools import wraps
from telegram import *
from telegram.ext import *
from bot_db import db

ADMIN = [505299455]

def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in ADMIN:
           print("Acesso Negado")
           return
        return func(bot, update, *args, **kwargs)
    return wrapped
