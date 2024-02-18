from telebot import TeleBot
from telebot.types import Message, MessageEntity, CallbackQuery
from telebot import REPLY_MARKUP_TYPES
from typing import List

class CustomBot(TeleBot):
    def __init__(self, token):
        super().__init__(token)

    def edit_message(
        self, 
        chat_id: int | str, 
        text: str, 
        message_id: int | None = None,
        parse_mode: str | None = None, 
        entities: List[MessageEntity] | None = None, 
        disable_web_page_preview: bool | None = None, 
        disable_notification: bool | None = None, 
        protect_content: bool | None = None, 
        reply_to_message_id: int | None = None, 
        allow_sending_without_reply: bool | None = None, 
        reply_markup: REPLY_MARKUP_TYPES | None = None, 
        timeout: int | None = None, 
        message_thread_id: int | None = None
    ) -> Message:

        # Try to edit message, if it fails, send a new message
        try:
            return self.edit_message_text(
                chat_id = chat_id,
                message_id = message_id,
                text = text,
                parse_mode = parse_mode,
                entities = entities,
                disable_web_page_preview = disable_web_page_preview,
                reply_markup = reply_markup,
            )
        except Exception as e:
            # print('*Error:', e)
            print(' => edit_message_text failed, sending new message')
            # print(' *message_id', message_id)
            return self.send_message(
                chat_id = chat_id,
                text = text,
                parse_mode = parse_mode,
                entities = entities,
                disable_web_page_preview = disable_web_page_preview,
                disable_notification = disable_notification,
                reply_to_message_id = reply_to_message_id,
                allow_sending_without_reply = allow_sending_without_reply,
                reply_markup = reply_markup,
                timeout = timeout,
                message_thread_id = message_thread_id
            )

    def edit_message_from_callback(
        self, 
        chat_id: int | str, 
        text: str, 
        call: CallbackQuery,
        parse_mode: str | None = None, 
        entities: List[MessageEntity] | None = None, 
        disable_web_page_preview: bool | None = None, 
        disable_notification: bool | None = None, 
        protect_content: bool | None = None, 
        reply_to_message_id: int | None = None, 
        allow_sending_without_reply: bool | None = None, 
        reply_markup: REPLY_MARKUP_TYPES | None = None, 
        timeout: int | None = None, 
        message_thread_id: int | None = None
    ) -> Message:
        return self.edit_message(
            chat_id = chat_id,
            message_id = call.message.id if call else None,
            text = text,
            parse_mode = parse_mode,
            entities = entities,
            disable_web_page_preview = disable_web_page_preview,
            disable_notification = disable_notification,
            protect_content = protect_content,
            reply_to_message_id = reply_to_message_id,
            allow_sending_without_reply = allow_sending_without_reply,
            reply_markup = reply_markup,
            timeout = timeout,
            message_thread_id = message_thread_id

        )
