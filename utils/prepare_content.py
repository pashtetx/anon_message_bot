from db.models import User
from datetime import datetime


def prepare_response_text(text: str, sender: User, is_subscribe: bool = False) -> str:
    
    username = "@" + sender.username if sender.username \
        else f"{sender.first_name if sender.first_name else ''} {sender.last_name if sender.last_name else ''}"
    
    response = (
        f"❤ Вам пришло сообщение от {f'{username}' if is_subscribe else 'Анонимного пользователя'}:\n\n",
        f"<b>{text}</b>"
    )

    return "".join(response)

def prepare_start_text(current_user: User):
    
    response = (
        f"Привет, это бот для анонимных валентинок, чтобы отправлять сообщения анонимно. 💌\n\n",
        f"- ❓ Чтобы получать анонимные сообщения, нужно сгенерировать ссылку /link и с помощью этой ссылки люди будут писать вам анонимные сообщения.\n",
        f"- 🔔 В боте есть возможность подписки с помощью подписки можно смотреть кто отправил сообщение.\n\n",
        f"✨ Подписка: {'Есть' if current_user.subscribed else 'Нету'}\n",
        f"{'Подписка истёчет в: {expire}'.format(expire=current_user.expire_in.strftime(format='%d.%m, %Y')) if current_user.subscribed else ''}"
        f"Это бета версия бота! Некоторые функции не работают."
    )

    return "".join(response)