from App.custom_bot import CustomBot
from telebot.types import CallbackQuery, Message
from App.Components.BaseComponent import BaseComponent
from App.Utils import Markup
import json

class MainMenu(BaseComponent):

    def __init__(self, bot: CustomBot, userid, call: CallbackQuery = None, startFrom = None) -> None:
        super().__init__(bot, userid, call, startFrom)
        self.bot = bot
        self.userid = userid

    def start(self):
        markup = Markup.generate_inline([
            [['Name', '_name']],
            [['Age', '_age']],
            [['Not filtered', '_not_filtered']],
            [['Hello', 'hello']],
        ])

        texto = "What do you want to change?"
        self.bot.send_message(
            self.userid, texto, parse_mode='Markdown', reply_markup=markup
        )

        def filter(call: CallbackQuery):
            return call.data in ['_name', '_age']

        # self.bot.once_callback_query_handler(self.userid, self.handle, custom_filter=filter)
        self.bot.add_callback_or_step_handler(self.userid, self.handle, False, custom_filter=filter)


    def handle(self, callback: CallbackQuery):
        markup = Markup.generate_inline([[['Cancelar', '_cancel']]])
        filter = lambda call: call.data == '_cancel'

        if callback.data == '_name':
            msg = self.bot.send_message(self.userid, "What is your new name?", reply_markup=markup)
            # self.bot.register_next_step_or_callback_handler(self.userid, self.handle_name)
            self.bot.add_callback_or_step_handler(self.userid, self.handle_name, custom_filter=filter)

        elif callback.data == '_age':
            msg = self.bot.send_message(self.userid, "What is your new age?", reply_markup=markup)
            self.bot.register_next_step_handler(msg, self.handle_age)

        elif callback.data == '_not_filtered':
            self.bot.send_message(self.userid, "Not filtered option!")


    def handle_name(self, message: Message | CallbackQuery = None):
        if isinstance(message, CallbackQuery) and message.data == '_cancel':
            self.bot.send_message(self.userid, "Operation canceled!")
            return
        
        elif isinstance(message, Message):
            self.name_change = message.text

        markup = Markup.generate_inline([
            [['Yes', '_yes'], ['No', '_no']]
        ])
        texto = f"Name changed to: {self.name_change} \n\n Confirm?"
        self.bot.send_message(self.userid, texto, reply_markup=markup)
        # self.bot.register_callback_query_handler(
        #     self.handle_name_confirm, lambda call: call.data in ['_yes', '_no']
        # )
        
        # self.bot.once_callback_query_handler(self.userid, self.handle_name_confirm, func=lambda call: call.data in ['_yes', '_no'])
        self.bot.add_callback_or_step_handler(self.userid, self.handle_name_confirm, respond_at_message=False, send_alert=True, custom_filter=lambda call: call.data in ['_yes', '_no'])


    def handle_name_confirm(self, call: CallbackQuery):
        if call.data == '_yes':
            self.bot.send_message(self.userid, "Name confirmed!")
        elif call.data == '_no':
            self.bot.send_message(self.userid, "Name not confirmed!")
        else:
            self.bot.send_message(self.userid, "Invalid option!")
            return self.handle_name()

        

    def handle_age(self, message: Message):
        if message:
            self.age_change = message.text

        markup = Markup.generate_inline([
            [['Yes', '_yes'], ['No', '_no']]
        ])
        texto = f"Age changed to: {self.age_change} \n\n Confirm?"

        self.bot.send_message(self.userid, texto, reply_markup=markup)
        self.bot.once_callback_query_handler(self.userid, self.handle_age_confirm)


    def handle_age_confirm(self, callback: CallbackQuery):
        if callback.data == '_yes':
            self.bot.send_message(self.userid, "Age confirmed!")
        elif callback.data == '_no':
            self.bot.send_message(self.userid, "Age not confirmed!")
        else:
            self.bot.answer_callback_query(callback.id, "Invalid option!", show_alert=True)
            return self.handle_age()

