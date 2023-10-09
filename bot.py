from telebot import TeleBot
from telebot.types import (
    Message,
    BotCommand,
    BotCommandScopeAllPrivateChats,
    MenuButtonCommands
)

from App.Database.database import DB
from App.Config.config import *
from App.Utils.markups import *

# Import Models
from App.Database.users import User

# Import Components
from App.Components.main_menu import MainMenu

# Another packages
import json

# Define bot
bot = TeleBot(BOT_TOKEN)


# Set basic commands (start, about, help)
basic_commands = [
    BotCommand("start", "🤖 Start botttttt"),
    BotCommand("about", "❓ About the bot"),
    BotCommand("help", "📚 Help")
]
bot.set_my_commands(basic_commands, scope = BotCommandScopeAllPrivateChats() )
bot.set_chat_menu_button(menu_button=MenuButtonCommands(type="commands"))


# WebApp messages handler
@bot.message_handler(content_types="web_app_data")
def answer_web_app_data(msg):
    userid = msg.from_user.id
    try:
        response = json.loads(msg.web_app_data.data)
        # clear keyboard
        bot.send_message(msg.from_user.id, 'Success! Data received: \n\n' + str(response), reply_markup=ReplyKeyboardRemove())

        action = response.get('action')

        if action == 'main_menu':
            MainMenu(bot=bot, userid=userid)

    except Exception as e:
        print("#Error", e)
        # get line of error
        import traceback
        traceback.print_exc()

        response = msg.web_app_data.data
        bot.send_message(msg.from_user.id, 'Error, but data: \n\n' + response)


# /test command
@bot.message_handler(commands=['test'])
def teste(msg):
    userid = msg.chat.id
    bot.send_message(userid, 'Test')


# Any message
@bot.message_handler(func= lambda m: True)
def receber(msg: Message):
    userid = msg.from_user.id
        
    if msg.text == "/about":
        bot.send_message(userid, "About the bot")
        msg_about = "This bot is template a bot that uses the WebApp feature (Mini App).\n\n"
        msg_about += "Source code: "
        bot.send_message(userid, msg_about)
        return
    
    elif msg.text == "/help":
        bot.send_message(userid, "Help")
        msg_help = "Commands:\n"
        msg_help += "/start - Start the bot\n"
        msg_help += "/about - About the bot\n"
        msg_help += "/help - Help\n"
        bot.send_message(userid, msg_help)
        return

    MainMenu(bot=bot, userid=userid)

    # # Verify if user exists
    # if db.verify_user(userid) == False:
    #     db.add_user(userid, user.first_name, user.username, user.language_code.split('-')[0] )


# CALLBACKS
@bot.callback_query_handler(func=lambda call: call.data.startswith('*') == False)
def callback(call):
    userid = call.from_user.id
    data = call.data

    options = {
        'hello': lambda: bot.answer_callback_query(call.id, f'Olá {call.from_user.first_name}'),
    }

    if data in options:
        options[data]() # Executes the function in the dict

bot.infinity_polling()