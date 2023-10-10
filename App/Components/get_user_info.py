from telebot import TeleBot
from App.Components.__component import BaseComponent
from App.Database.users import User
from App.Utils.constants import URL_HOME
from App.Utils.markups import markup_webapp_button

class GetUserInfo(BaseComponent):
    def __init__(self, bot: TeleBot, userid) -> None:
        super().__init__(bot)
        self.userid = userid
        self.start()

    def start(self):
        self.bot.send_message(self.userid, "⌛️ Getting your information!")
        # get the user info from the database
        result = User(self.bot).get_user(self.userid)
        # create a keyboard button that opens webapp and pass user info in url parameters
        # and passes drawings data in url parameters
        markup = markup_webapp_button("👀 Click here to open mini app", URL_HOME, {'user_info': str(result)})
        if result:
            self.bot.send_message(self.userid, f"✅ Here are your information!", reply_markup=markup)
        else:
            self.bot.send_message(self.userid, "❌ You don't have any information!")

        self.goMainMenu(self.userid)
