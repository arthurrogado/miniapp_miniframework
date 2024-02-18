from telebot import TeleBot
from telebot.types import CallbackQuery
from App.Components.__component import BaseComponent
from App.Components.other_menu import OtherMenu
from ..Utils.markups import *

class MainMenu(BaseComponent):

    def __init__(self, bot: TeleBot, userid, call: CallbackQuery = None, startFrom = None) -> None:
        super().__init__(bot, userid, call, startFrom)
        self.bot = bot
        self.userid = userid
        # self.start() # can be omitted because it's called in the parent class (BaseComponent)

    def start(self):
        self.bot.send_message(self.userid, "*MAIN MENU\!*", parse_mode='MarkdownV2', reply_markup=generate_inline([
            [['Hello', '*hello']],
            [['Start from here', 'start_from_here']]
        ]))
        # Set callback query handler to custom markup that has a specific call_data and is not registered in main bot
        self.set_callback_query_handler(self.handle, '*hello')

    def handle(self, callback):
        self.bot.answer_callback_query(callback.id, "Hello!")
        self.bot.send_message(self.userid, "Hello!")
        OtherMenu(self.bot, self.userid)

    def start_from_here(self):
        self.bot.send_message(self.userid, "Hello from here! Not from start!")