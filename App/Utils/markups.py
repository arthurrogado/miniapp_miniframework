from telebot.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

def generate_inline(buttons: list, sufix: str = ''):
    ### Example:
    # buttons = [ # scope
    #     [ # line
    #         ['Butto1', 'action1'], # button
    #         ['Butto2', 'action2'],
    #     ],
    #     [
    #         ['Butto3', 'action3'],
    #         ['Butto4', 'action4'],
    #         ['Butto5', 'action5']
    #     ]
    # ]
    # sufix: str = _id
    markup = InlineKeyboardMarkup()
    for line in buttons:
        markup.row(
            *[InlineKeyboardButton(text=button[0], callback_data=f'{button[1]}{sufix}') for button in line]
        )
    return markup

def generate_keyboard(buttons: list, **kwargs) -> ReplyKeyboardMarkup:
    ### Example:
    # buttons = [
    #     ['Button1', 'Button2'],
    #     ['Button3', 'Button4', 'Button5']
    # ]
    markup = ReplyKeyboardMarkup(**kwargs, one_time_keyboard=True)
    for line in buttons:
        markup.row(
            *[KeyboardButton(text=button) for button in line]
        )
    return markup

def clearKeyboard():
    return ReplyKeyboardRemove()