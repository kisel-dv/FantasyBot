from configBot import TOKEN, CHANNEL_ID, PROXY_LIST
import telebot
from telebot.types import InputMediaPhoto
from contextlib import ExitStack
import logging
import socket

CURRENT_PROXY = 0
bot = telebot.TeleBot(TOKEN)
telebot.apihelper.proxy = {'https': PROXY_LIST[CURRENT_PROXY]}


def safety_send_group(channel_id, media):
    global CURRENT_PROXY
    for i in range(3):
        try:
            bot.send_media_group(channel_id, media)
            logging.info('Статистика по чемпионату отправлена в канал')
            return
        except:
            logging.warning(
                'Ошибка при попытке отправки сообщения в канал, прокси {}, попытка {}'.format(CURRENT_PROXY, i + 1))
            continue
    CURRENT_PROXY += 1
    if CURRENT_PROXY == len(PROXY_LIST):
        logging.error('Все прокси перепробованы, но запостить сообщение не вышло :(')
        raise Exception
    else:
        telebot.apihelper.proxy = {'https': PROXY_LIST[CURRENT_PROXY]}
        safety_send_group(channel_id, media)


def posting_to_channel(caption, *files, **kwargs):
    channel_id = CHANNEL_ID if kwargs.get('channel_id') is None else kwargs['channel_id']
    with ExitStack() as stack:
        pics = [stack.enter_context(open(fp, 'rb')) for fp in files]
        media = []
        for i in range(len(pics)):
            media.append(InputMediaPhoto(pics[i], caption) if i == 0 else InputMediaPhoto(pics[i]))
        safety_send_group(channel_id, media)


def check_proxy():
    global CURRENT_PROXY
    try:
        bot.send_message(CHANNEL_ID, 'Прокси {} работает'.format(CURRENT_PROXY))
    except:
        logging.warning('Ошибка при попытке отправки сообщения в канал')
        CURRENT_PROXY += 1
        if CURRENT_PROXY == len(PROXY_LIST):
            logging.error('Все прокси перепробованы, но запостить сообщение не вышло :(')
            raise Exception
        else:
            telebot.apihelper.proxy = {'https': PROXY_LIST[CURRENT_PROXY]}
            check_proxy()


# для проверки работы текущей прокси
if __name__ == '__main__':
    check_proxy()
