import telebot
import logging
import time
from telebot.types import InputMediaPhoto
from contextlib import ExitStack
from typing import List

from config import TOKEN, PROXY_LIST, TG_CHANNELS


CONNECTION_ESTABLISHMENT_NUMBER = 3
SENDING_ATTEMPTS_NUMBER = 5


def check_proxy():
    bot = telebot.TeleBot(TOKEN)
    self_chat_id = TG_CHANNELS.get('self')
    for current_proxy in range(len(PROXY_LIST)):
        telebot.apihelper.proxy = {'https': PROXY_LIST[current_proxy]}
        for i in range(CONNECTION_ESTABLISHMENT_NUMBER):
            try:
                bot.send_message(self_chat_id, 'Прокси #{}'.format(current_proxy))
                logging.info('Установлено соединение с помощью прокси #{}, попытка {}'.format(current_proxy, i + 1))
                # чтобы работающая прокси была первой на следующую проверку
                PROXY_LIST[0], PROXY_LIST[current_proxy] = PROXY_LIST[current_proxy], PROXY_LIST[0]
                return PROXY_LIST[0]
            except Exception:
                time.sleep(1)
                continue
        logging.warning('Не удалось установить соединение с помощью прокси #{}'.format(current_proxy))
    logging.error('Все прокси перепробованы, но запостить сообщение не вышло :(')
    raise Exception


def safety_send_group(channel_id: str, media: List[InputMediaPhoto], proxy: bool = False) -> None:
    bot = telebot.TeleBot(TOKEN)
    if proxy:
        working_proxy = check_proxy()
        telebot.apihelper.proxy = {'https': working_proxy}
    for i in range(SENDING_ATTEMPTS_NUMBER):
        try:
            bot.send_media_group(channel_id, media)
            logging.info('Статистика по чемпионату отправлена в канал')
            return
        except Exception:
            logging.warning(
                'Ошибка при попытке отправки сообщения в канал, попытка {}'.format(i + 1))
            time.sleep(1)
            continue
    logging.error('Запостить сообщение не вышло :(')
    raise Exception


# kwargs Для channel_id/proxy
def posting_to_channel(channel_id: str, caption: str, *files) -> None:
    with ExitStack() as stack:
        pics = [stack.enter_context(open(fp, 'rb')) for fp in files if fp is not None]
        if not pics:
            logging.warning('Нет картинок для публикации')
            return
        media = []
        for i in range(len(pics)):
            media.append(InputMediaPhoto(pics[i], caption) if i == 0 else InputMediaPhoto(pics[i]))
        # теперь можно и без прокси
        safety_send_group(channel_id, media, proxy=False)
    return


def posting_info_message(channel_id: str, text: str = "") -> None:
    bot = telebot.TeleBot(TOKEN)
    bot.send_message(channel_id, text)
    return
