"""Classe base para todos os componentes do bot.

Todo componente de feature deve herdar BaseComponent. Fornece:
- Referência ao bot e userid
- Auto-envio de "typing" action
- PermissionMiddleware auto-instanciado
- cancel() com cleanup de handlers
- set_callback_query_handler() helper
"""

from telebot import TeleBot
from App.custom_bot import CustomBot
from telebot.types import CallbackQuery

from ..Utils import Markup
from ..Database.DB import DB
from ..Core.PermissionMiddleware import PermissionMiddleware


class BaseComponent():
    markup_cancel = Markup.generate_inline([[['❌ Cancel', '*cancel']]])

    def __init__(self, bot: CustomBot, userid, call: CallbackQuery = None, startFrom = None) -> None:
        self.bot = bot
        self.userid = userid
        self.call = call
        self.db = DB(self.bot)
        self.bot.send_chat_action(self.userid, 'typing')
        self.permission = PermissionMiddleware(self.bot, self.userid, self.call)

        if startFrom:
            startFrom(self)

    def cancel(self, call=None):
        """Cancela operação atual e limpa todos os handlers do chat."""
        if call:
            self.bot.answer_callback_query(call.id, '❌ Cancelled')
            self.bot.delete_message(call.message.chat.id, call.message.message_id)
            chat_id = call.message.chat.id
        else:
            chat_id = self.userid
        self.bot.clear_step_handler_by_chat_id(chat_id)
        self.bot.clear_registered_callback_handlers_by_chat_id(chat_id)

    def set_callback_query_handler(self, handler_function, call_data):
        """Registra handler de callback privado (prefixo _ no call_data)."""
        self.bot.register_callback_query_handler(handler_function, lambda call: call.data == call_data)