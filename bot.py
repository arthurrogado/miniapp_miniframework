"""Entry point do bot Telegram.

Responsabilidades:
- Configura e inicia o CustomBot (pyTelegramBotAPI)
- Registra handlers (start, callbacks, inline, webapp)
- Roteamento dinâmico via automatic_run()
- Rate limiting em todos os entry points
- (Opcional) Inicializa Pyrogram admin_bot via admin_runtime

Iniciar: python bot.py
"""

import importlib
import json
import math
import traceback

from telebot.types import (
    Message,
    BotCommand,
    BotCommandScopeAllPrivateChats,
    MenuButtonCommands,
    CallbackQuery,
    InlineQuery,
)
from telebot.apihelper import ApiTelegramException

from App.custom_bot import CustomBot
from App.Config import BOT_TOKEN, ADMINS_IDS
from App.Utils import Markup
from App.Core.Exceptions import SilentException
from App.Core.RateLimit import rate_limit
from App.Core.Messages import Messages

# Import Components
from App.Components.main_menu import MainMenu
from App.Components.Queries import Queries

# ─── (Opcional) Pyrogram admin_bot ───────────────────────────────────
# Descomente para habilitar o bot secundário (Pyrogram) para operações
# pesadas como upload de vídeos, backups, etc.
#
# from App.Config import USE_PYROGRAM
# if USE_PYROGRAM:
#     from admin_runtime import init_admin_bot, submit_coro
#     from App.Config.secrets import API_ID, API_HASH, ADMIN_BOT_TOKEN
#     admin_client = init_admin_bot(API_ID, API_HASH, ADMIN_BOT_TOKEN)
# else:
#     admin_client = None
admin_client = None


# ─── Bot principal ───────────────────────────────────────────────────

bot = CustomBot(BOT_TOKEN)

basic_commands = [
    BotCommand("start", "🤖 Start bot"),
    BotCommand("about", "❓ About the bot"),
    BotCommand("help", "📚 Help"),
]
bot.set_my_commands(basic_commands, scope=BotCommandScopeAllPrivateChats())
bot.set_chat_menu_button(menu_button=MenuButtonCommands(type="commands"))


# ─── Module cache para importação dinâmica ───────────────────────────
module_cache = {}


# ─── WebApp ──────────────────────────────────────────────────────────

@bot.message_handler(content_types="web_app_data")
def answer_web_app_data(msg):
    userid = msg.from_user.id
    try:
        response = json.loads(msg.web_app_data.data)
        bot.send_message(userid, 'Success! Data received:\n\n' + str(response), reply_markup=Markup.clear_markup())

        action = response.get('action')
        if action == 'main_menu':
            MainMenu(bot=bot, userid=userid)

    except Exception as e:
        print("#Error", e)
        traceback.print_exc()
        response = msg.web_app_data.data
        bot.send_message(userid, 'Error, but data:\n\n' + response)


# ─── Roteador dinâmico ──────────────────────────────────────────────

def automatic_run(data_text: str, chat_id: int, call: CallbackQuery = None):
    """Roteador dinâmico de componentes.

    Convenção de callback/deep-link:
        Classe__metodo__arg1__arg2
        Subpastas usam _ no caminho: Pasta_Classe__metodo__arg

    Callbacks com prefixo _ são privados (tratados localmente pelo componente).

    Features:
        - Rate limiting automático
        - Cache de módulos importados
        - Injeção de admin_bot quando o componente aceitar
        - Limpeza de handlers antes de cada execução
        - SilentException para guards (permission, etc.)
    """
    kind = "callback" if call else "command"
    tracker = rate_limit.begin(chat_id, kind, data_text)

    try:
        # Cancelamento genérico
        if data_text.lower() in ["cancel", "cancelar"]:
            if call:
                bot.answer_callback_query(call.id, Messages.OP_CANCELLED, show_alert=False)
            else:
                bot.send_message(chat_id, Messages.OP_CANCELLED + ".")
            return

        # Rate limit check (antes de importar/instanciar componentes)
        if not tracker.allowed:
            wait_s = int(max(1, math.ceil(tracker.retry_after_s)))
            msg_text = f"⏳ Too many requests. Wait {wait_s}s and try again."
            if call:
                bot.answer_callback_query(call.id, msg_text, show_alert=True)
            else:
                bot.send_message(chat_id, msg_text)
            tracker.log_blocked()
            return

        class_path, method_name, *params = data_text.split("__")
        class_name = class_path.split("_")[-1]
        module_path_str = ".".join(class_path.split("_"))
        method_name = method_name or "async_init"

        # Cache de módulos
        module = module_cache.get(module_path_str)
        if not module:
            try:
                module = importlib.import_module(f"App.Components.{module_path_str}.{module_path_str}")
            except ModuleNotFoundError:
                module = importlib.import_module(f"App.Components.{module_path_str}")
            module_cache[module_path_str] = module

        class_ = getattr(module, class_name)

        # Injeção de admin_bot se o construtor aceitar
        try:
            from inspect import signature
            sig = signature(class_.__init__)
            if 'admin_bot' in sig.parameters and admin_client:
                instance = class_(bot, chat_id, call, admin_bot=admin_client)
            else:
                instance = class_(bot, chat_id, call)
        except Exception:
            instance = class_(bot, chat_id, call)

        # Limpar handlers antigos ANTES de executar
        bot.clear_registered_callback_handlers_by_chat_id(chat_id)
        bot.clear_step_handler_by_chat_id(chat_id)

        method = getattr(instance, method_name)
        method(*params)

        tracker.finish_ok()

    except SilentException:
        # Guard já enviou mensagem ao usuário — não exibir erro genérico
        tracker.finish_ok()

    except Exception as e:
        tracker.finish_error(e)
        text_erro = f"\n    *** Unexpected error: {e}\n File: {e.__traceback__.tb_frame.f_code.co_filename}\n Line: {e.__traceback__.tb_lineno}\n{traceback.format_exc()}"
        print(text_erro)
        if call:
            bot.answer_callback_query(call.id, Messages.GENERIC_ERROR)
            return
        bot.send_message(chat_id, Messages.GENERIC_ERROR)
        raise e


# ─── Handlers ────────────────────────────────────────────────────────

@bot.message_handler(commands=['start'])
def start_parameter(msg: Message):
    userid = msg.from_user.id
    param = msg.text.split(" ")[1] if len(msg.text.split(" ")) > 1 else None
    if param:
        automatic_run(param, userid)
    else:
        MainMenu(bot, userid).start()


@bot.message_handler(func=lambda m: True)
def receber(msg: Message):
    userid = msg.from_user.id

    entities = msg.entities if msg.entities else []
    for entity in entities:
        if entity.type == "url":
            if f"t.me/{bot.get_me().username}?start=" in msg.text:
                automatic_run(msg.text.split("start=")[1], userid)
                return
        elif entity.type == "text_link":
            if f"t.me/{bot.get_me().username}?start=" in entity.url:
                automatic_run(entity.url.split("start=")[1], userid)
                return

    if msg.text == "/id":
        bot.send_message(userid, f"*Your ID:* `{userid}`", parse_mode="Markdown")
        return

    if msg.text.startswith("/") and not msg.text.startswith("/start"):
        automatic_run(msg.text[1:], userid)
        return

    try:
        MainMenu(bot, userid).start()
    except ApiTelegramException as e:
        if e.result_json['description'] == "Forbidden: bot was blocked by the user":
            print(f"User {userid} blocked the bot.")
        else:
            print(f"Error starting menu for user {userid}: {e}")


# ─── Callbacks ───────────────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: not call.data.startswith('_'))
def callback(call):
    """Callback global: encaminha callbacks públicos para automatic_run.

    Callbacks com prefixo _ são privados (tratados localmente por componentes).
    """
    userid = call.from_user.id
    data = call.data

    if data == "cancelar":
        bot.answer_callback_query(call.id, Messages.OP_CANCELLED, show_alert=True)
        return

    options = {
        'hello': lambda: bot.answer_callback_query(call.id, f'Hello {call.from_user.first_name}!'),
        'start_from_here': lambda: MainMenu(bot, userid, call, MainMenu.start_from_here),
    }

    if data in options:
        options[data]()
    else:
        automatic_run(data, userid, call)


# ─── Inline Queries ──────────────────────────────────────────────────

@bot.inline_handler(lambda query: True)
def inline_handler(query: InlineQuery):
    try:
        userid = query.from_user.id
        query_text = query.query or ""

        tracker = rate_limit.begin(userid, "inline", query_text)

        if not tracker.allowed:
            wait_s = int(max(1, math.ceil(tracker.retry_after_s)))
            try:
                bot.answer_inline_query(
                    query.id, [], cache_time=1, is_personal=True,
                    switch_pm_text=f"⏳ Too many requests. Wait {wait_s}s.",
                    switch_pm_parameter="rate_limit",
                )
            except Exception:
                pass
            tracker.log_blocked()
            return

        offset = int(query.offset) if query.offset else 0
        limit = 50

        db = Queries(bot, userid, query_text, query.chat_type)
        results = db.get_results(offset, limit)

        next_offset = str(offset + limit) if len(results) == limit else ''
        bot.answer_inline_query(query.id, results, next_offset=next_offset, cache_time=1)

        tracker.finish_ok()

    except ApiTelegramException as e:
        if "query is too old" in str(e.description):
            print(f"Timeout: inline query expired for user {userid}")
        else:
            print(f"API error in inline_handler: {e}")

    except Exception as e:
        traceback.print_exc()
        try:
            bot.answer_inline_query(query.id, [], cache_time=1, switch_pm_text="Error processing query.", switch_pm_parameter="error")
        except Exception:
            pass
        try:
            tracker.finish_error(e)
        except Exception:
            pass


# ─── Start ───────────────────────────────────────────────────────────

bot.infinity_polling(skip_pending=True)