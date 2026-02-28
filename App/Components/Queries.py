from telebot import TeleBot
from telebot.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    InlineQueryResultPhoto,
    InlineQueryResultCachedPhoto
)

from App.Database import Users
import requests
import io
from PIL import Image
import datetime as dt

from App.Utils import Markup


class Queries():
    def __init__(self, bot: TeleBot, userid: int = None, query: str = None, chat_type: str = None) -> list:
        self.userid = userid
        self.query = query
        self.bot = bot
        self.chat_type = chat_type
        self.deep_link_base = f"https://t.me/{self.bot.get_me().username}?start="
        self.limit = 10
        self.default_thumbnail = "https://i.imgur.com/mbFdfhs.png"

    def get_results(self, offset: int, limit: int = 10):
        self.offset = offset
        self.limit = limit

        pesquisas = {
            'est: ': self.pesquisar_estatisticas,
            'o:': self.pesquisar_obras,
            'oi:': self.get_obra_por_id,
            't: ': self.pesquisar_em_temporada,
            'of:': self.pesquisar_obras_favoritas,
            'ea:': self.pesquisar_obras_em_alta,
            'g: ': self.pesquisar_obras_genero,
            'l: ': self.pesquisar_obras_lancamentos,
            'u: ': self.pesquisar_usuarios,
            'voucher: ': self.pesquisar_voucher,
            'temp: ': self.pesquisar_temporadas_obra
        }

        self.results = self.resultados_nao_encontrados()

        for key in pesquisas:
            if key in self.query or key.strip() == self.query.strip():
                self.results = pesquisas[key](self.query)
                break
        
        # self.results = self.results[:50] # limitar a 50 resultados
        return self.results[:self.limit]

    def get_size(self, url: str):
        # get thumbnail information (width and height)
        try:
            response = requests.get(url)
            img = Image.open(io.BytesIO(response.content))
            width, height = img.size
            return width, height
        except Exception as e:
            print(f"Error retrieving thumbnail information: {e}")
            return None, None
        
    def get_from(self, object, key):
        return str(object.get(key)) if object.get(key) is not None else ""
    

    def resultados_nao_encontrados(self, mensagem: str = 'Não encontrado'):
        return [
            InlineQueryResultArticle(
                id='1',
                title=mensagem,
                input_message_content=InputTextMessageContent(mensagem)
            )
        ]
    

    def get_text_link(self, text: str, url: str):
        return f"[{text}]({url})"
    

    def check_is_admin(self, msg: str = "Ops, não encontrado..."):
        if Usuarios().is_not_admin(self.userid):
            return self.resultados_nao_encontrados(msg)


    def article_episodio(self, episodio):
        texto = f"Episódio {episodio.get('ordem')} - {episodio.get('nome_obra')}" if self.chat_type == "sender" else f"🤖🎬 Assista agora ao {episodio.get('ordem')}º episódio da {episodio.get('ordem_temporada')}ª temporada de {episodio.get('nome_obra')}"

        return InlineQueryResultArticle(
            id=episodio.get('id'),
            title = f"Episódio {episodio.get('ordem')}",
            input_message_content=InputTextMessageContent(
                self.get_text_link(texto, self.deep_link_base + 'Obra__assistir_episodio__' + str(episodio.get('id'))),
                parse_mode='Markdown'
            ),
            description = f"Temporada {episodio.get('ordem_temporada')}\n{episodio.get('nome_obra')}",
            thumbnail_url=episodio.get('thumbnail', self.default_thumbnail)
        )
