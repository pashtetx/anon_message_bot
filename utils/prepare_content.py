from datetime import datetime


def prepare_response_text(text: str, sender, is_visible: bool = False) -> str:
    
    username = "@" + sender.username if sender.username \
        else f"{sender.first_name if sender.first_name else ''} {sender.last_name if sender.last_name else ''}"
    
    response = (
        f"❤ Вам пришло сообщение от {f'{username}' if is_visible else f'Анонимного пользователя ({sender.fake_username})'}:\n\n",
        f"<b>{text}</b>"
    )

    return "".join(response)

def prepare_start_text(current_user):
    
    response = (
        f"Привет, это бот для анонимных валентинок, чтобы отправлять сообщения анонимно. 💌\n\n",
        f"- ❓ Чтобы получать анонимные сообщения, нужно сгенерировать ссылку /link и с помощью этой ссылки люди будут писать вам анонимные сообщения.\n\n",
        f"-  🎲  В боте есть возможность отправить сообщение рандомным пользователям /random \n\n",
        f"-  🏆  Чтобы получать сообщения поставьте свою ссылку в профиль телеграм/инстаграм/дискорд\n\n ",
        f"Твое анонимное имя: <b>{current_user.fake_username}</b>\n",
        f"-  🎭  Чтобы изменить анонимное имя /username (name)\n\n"
        f"📦 <i>Тех. поддержка: @migainis</i>",
    )

    return "".join(response)
