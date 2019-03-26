import logging
from telegram import *
from telegram.ext import *
from bot_admin import *
from bot_db import db
from bot_token import token

#Users' ID
hsnavarro_user_id = '505299455'
arnon_user_id = '375166827'
de_castro_user_id = '445765305'

#For testing
#de_castro_user_id = hsnavarro_user_id
#arnon_user_id = hsnavarro_user_id

updater = Updater(token=token)

#Acess dispatcher
dispatcher = updater.dispatcher

#Logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

#Create db (use on sqlite3)
# sqlite3 bot.db "create table ranking (id integer primary key, lowername text, name text, score integer)"

ADMIN = [hsnavarro_user_id]

def isSubSequence(pattern, text, n, m):
    if n == 0: return True
    if m == 0: return False
    if pattern[n-1] == text[m-1]: return isSubSequence(pattern, text, n-1, m-1)
    return isSubSequence(pattern, text, n, m-1)

#Filter
class FilterCan(BaseFilter):
    def filter(self, message):
        return 'posso' in message.text.lower()

class FilterProve(BaseFilter):
    def filter(self, message):
        return 'prova' in message.text.lower()

#class FilterCant(BaseFilter):
#    def filter(self, message):
#        m = len(message.text)
#        n = len("não posso")
#        return isSubSequence("não posso", message.text, n, m)
#

class FilterCant(BaseFilter):
    def filter(self, message):
        return 'não posso' in message.text.lower()

#Function to start the bot
def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, 
                     text="Sou o Helper, o que você precisa?")

#Function echo
def echo(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text=update.message.text)

#Emojis 🙁 😁 🙃 #

#Function isOk 
#There's a bug in here 
def isOk(bot, update):
    custom_keyboard = [[
        InlineKeyboardButton("Sim", callback_data="1"),
        InlineKeyboardButton("Não", callback_data="2"),
        InlineKeyboardButton("Talvez", callback_data="3")
    ]]
    reply_markup = InlineKeyboardMarkup(custom_keyboard)
    bot.send_message(chat_id=update.message.chat_id,
            text='Você está bem?', reply_markup=reply_markup)

#Function caps
def caps(bot, update, args):
    if len(args) < 1:
        bot.send_message(chat_id=update.message.chat_id, 
                         text="Comando incorreto.\nUso: /caps <frase>")
    text_caps = ' '.join(args).upper()
    bot.send_message(chat_id=update.message.chat_id, text=text_caps)

#Inline Caps
#def inline_caps(update, bot):
#    query = update.inline_query.query
#    if not query:
#        return
#    results = list()
#    results.append(
#        InlineQueryResultArticle(
#            id=query.upper(),
#            title='Caps',
#            input_message_content=InputTextMessageContent(query.upper())
#        )
#    )
#    bot.answer_inline_query(update.inline_query.id, results)

def personal_good_message(bot, update, user_id, name):
    #For testing
    #user_id = 0
    ############

    switcher = {
            int(hsnavarro_user_id) : "Mais uma vez?\n",
            int(de_castro_user_id) : "Esse garoto vai longe!\n",
            int(arnon_user_id): "Arnonon!\n",
            }
    msg = switcher.get(user_id, str(name) + '!')
    bot.send_message(chat_id=update.message.chat_id, text=msg)


def personal_bad_message(bot, update, user_id, name):
    #For testing
    #user_id = 0
    ###########

    switcher = {
            int(hsnavarro_user_id) : "Jamais esperaria isso de você!\n",
            int(de_castro_user_id) : "Por que eu não estou surpreso?\n",
            int(arnon_user_id): "Arnon... Melhor parar com isso...\n",
    }
    msg = switcher.get(user_id, str(name) + '...')
    bot.send_message(chat_id=update.message.chat_id, text=msg)

#Trigger the bot to decrease the users' rank :(
def triggerneg(bot, update):
    user_id = update.effective_user.id
    name = update.effective_user.first_name
    ranking = db['ranking']
    if not ranking.find_one(lowername=name.lower()):
        bot.send_message(chat_id=update.message.chat_id, 
                         text="Se estivesse no ranking, perderia ponto...")
    else:
        personal_bad_message(bot, update, user_id, name)
        bot.send_message(chat_id=update.message.chat_id, text="Perdeu ponto!")
        change_ranking_db(update, name, -10, 0)

#Trigger the bot to increase the users' rank :)
def triggerpos(bot, update):
    user_id = update.effective_user.id 
    name = update.effective_user.first_name
    ranking = db['ranking']
    if not ranking.find_one(lowername=name.lower()):
        bot.send_message(chat_id=update.message.chat_id,
                         text="Se estivesse no ranking, ganharia ponto...")
    else:
        personal_good_message(bot, update, user_id, name)
        bot.send_message(chat_id=update.message.chat_id, text="Ganhou ponto!")
        change_ranking_db(update, name, 10, 0) 

def ranking(bot, update):
    
    ranking = db['ranking']
    result = list(ranking.all(order_by='-score'))
    
    if len(result) == 0:
        bot.send_message(chat_id=update.message.chat_id, text="Ranking Vazio!")
    else:
        msg = "*Ranking da Iniciativa*\n"
        for user in result:
            msg += user['name'] + ': ' + str(user['score']) + '\n'

        bot.send_message(chat_id=update.message.chat_id, 
                         text=msg, 
                         parse_mode=ParseMode.MARKDOWN)


def add_person_rank_db(update, name):
    ranking = db['ranking']
    ranking.insert(dict(lowername=name.lower(), name=name, score=1000))
    update.message.reply_text("Pessoa adicionada com sucesso")

def rem_person_rank_db(update, name):
    ranking = db['ranking']
    ranking.delete(lowername=name.lower())
    update.message.reply_text("Pessoa removida com sucesso")

def change_ranking_db(update, name, value, message):
    if value == 0: return

    ranking = db['ranking']

    #ranking.insert_ignore(dict(lowername=name.lower(), name=name, score=1000),
    #                           ['lowername'])
    if not ranking.find_one(lowername=name.lower()): 
        update.message.reply_text("Pessoa não está no ranking")
    else:
        user = ranking.find_one(lowername=name.lower())
        user['score'] += value
        ranking.update(user, ['id'])
        if message == 1:
                update.message.reply_text("Ranking alterado com sucesso")

@restricted
def add_person(bot, update, args):
    if len(args) < 1:
        update.effective_message.reply_text(
                "Commando incorreto\nUso: /add_person <nome>")
        return
    
    name = ' '.join(args)
    ranking = db['ranking']
    if ranking.find_one(lowername=name.lower()):
        bot.send_message(chat_id=update.message.chat_id,
                         text="Pessoa já está no ranking!")
    else: 
        add_person_rank_db(update, name)

@restricted
def rem_person(bot, update, args): 
    if len(args) < 1:
        update.effective_message.reply_text(
                "Commando incorreto\nUso: /rem_person <nome>")
        return
    
    name = ' '.join(args)
    ranking = db['ranking']
    if ranking.find_one(lowername=name.lower()): 
        rem_person_rank_db(update, name)
    else:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Pessoa não está no ranking!")
    
@restricted
def ranking_change(bot, update, args):
    if len(args) < 2:
        update.effective_message.reply_text(
                "Comando incorreto\nUso: /change_ranking <nome> <pontos>")
        return

    name = ' '.join(args[:-1])
    delta = int(args[-1])
    change_ranking_db(update, name, delta, 1)

def unknown(bot, update):
    bot.send_message(chat_id=update.message.chat_id, 
                     text="Comando não reconhecido.")

@restricted
def reset(bot, update):
    ranking = db['ranking']
    if len(ranking) == 0:
        bot.send_message(chat_id=update.message.chat_id,
                         text="Ranking já está vazio")
    else:
        ranking = list(ranking.all())
        for user in ranking:
            ranking.delete(lowername=name.lower())
        bot.send_message(chat_id=update.message.chat_id,
                         text="Ranking foi resetado")
################################################################

#JobQueue (perform tasks periodically)
#Message every minute
# def callback_minute(bot):
#     bot.send_message(chat_id='505299455', text='Me dá atenção!')

#Message with delay
# def callback_30(bot):
#     bot.send_message(chat_id='505299455', text='teste')

# updater.job_queue.run_repeating(callback_minute, interval=60)
# updater.job_queue.run_once(callback_30, 30)

#job_minute.enabled = False  # Temporarily disable this job
#job_minute.schedule_removal()  # Remove this job completely

################################################################


#Initialize filters
filter_prova = FilterProve()
filter_nposso = FilterCant()
filter_posso = FilterCan()

#Add Handlers
#dispatcher.add_handler(MessageHandler(Filters.text, echo))
#dispatcher.add_handler(InlineQueryHandler(inline_caps))
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('fine', isOk))
dispatcher.add_handler(CommandHandler('caps', caps, pass_args=True))
dispatcher.add_handler(CommandHandler('ranking', ranking))
dispatcher.add_handler(CommandHandler('change_ranking', 
                                       ranking_change, 
                                       pass_args=True))
dispatcher.add_handler(CommandHandler('add_person', 
                                       add_person,
                                       pass_args=True))
dispatcher.add_handler(CommandHandler('rem_person', 
                                       rem_person, 
                                       pass_args=True))
dispatcher.add_handler(CommandHandler('reset', reset))
dispatcher.add_handler(MessageHandler(filter_prova | filter_nposso, 
                                      triggerneg))
dispatcher.add_handler(MessageHandler(filter_posso & ~filter_nposso, 
                                      triggerpos))
dispatcher.add_handler(MessageHandler(Filters.command, unknown))

#Start bot
print("Bot rodando...")
updater.start_polling()
