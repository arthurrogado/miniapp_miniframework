from telebot import TeleBot
from telebot.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeDefault, MenuButtonCommands

bot = TeleBot("6350523990:AAEYzidOg8VTIO3-oHnP-txv6KPoRPSBMDg")

comandos_comuns = [
    BotCommand("start", "🤖 Inicia o botttt"),
    BotCommand("ajuda", "❓ Mostra a ajuda"),
    BotCommand("conhecer_bots", "🤖 Conhecer outros bots"),
    BotCommand("doacao", "💰 Ajudar desenvolvedor pobre 😢"),
]
bot.set_my_commands(comandos_comuns, scope = BotCommandScopeAllPrivateChats() )
bot.set_chat_menu_button(menu_button=MenuButtonCommands(type="commands"))

print(bot.get_my_commands(scope=BotCommandScopeDefault()))

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Hello!")

bot.infinity_polling()