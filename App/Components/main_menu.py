from telebot import TeleBot
from App.Components.__component import BaseComponent
from App.Components.other_menu import OtherMenu
from ..Utils.markups import *

class MainMenu(BaseComponent):

    def __init__(self, bot: TeleBot, userid):
        super().__init__(bot, userid)
        self.bot = bot
        self.userid = userid

        self.start()

    def start(self):
        self.bot.send_message(self.userid, "*MAIN MENU\!*", parse_mode='MarkdownV2', reply_markup=generate_inline([
            [['Hello', '*hello']]
        ]))
        self.bot.register_callback_query_handler(self.handle, lambda call: call.data == '*hello')

    def handle(self, callback):
        self.bot.answer_callback_query(callback.id, "Hello!")
        self.bot.send_message(self.userid, "Hello!")
        OtherMenu(self.bot, self.userid)