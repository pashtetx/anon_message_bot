from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder



def parse_buttons(text: str, button_separator = "#", text_url_separator = "-") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    buttons = text.replace(" ", "").split(button_separator)

    for button in buttons:

        button = button.split(text_url_separator)
        builder.button(text=button[0], url=button[1])
    
    builder.adjust(2)

    return builder.as_markup()