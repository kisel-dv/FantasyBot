from config import TOKEN, CHANNEL_ID, PROXY_LIST, SELF_CHAT_ID
import telebot
from telebot.types import InputMediaPhoto
from contextlib import ExitStack
import logging
import time


def safety_send_group(channel_id, media, proxy):
    bot = telebot.TeleBot(TOKEN)
    if proxy is not None:
        telebot.apihelper.proxy = {'https': proxy}
    for i in range(5):
        try:
            bot.send_media_group(channel_id, media)
            logging.info('Статистика по чемпионату отправлена в канал')
            return
        except:
            logging.warning(
                'Ошибка при попытке отправки сообщения в канал, попытка {}'.format(i + 1))
            time.sleep(1)
            continue
    logging.error('Запостить сообщение не вышло :(')
    raise Exception


def check_proxy():
    bot = telebot.TeleBot(TOKEN)
    for current_proxy in range(len(PROXY_LIST)):
        telebot.apihelper.proxy = {'https': PROXY_LIST[current_proxy]}
        for i in range(3):
            try:
                bot.send_message(SELF_CHAT_ID, 'Прокси {} работает'.format(current_proxy))
                logging.info('Прокси {} работает'.format(current_proxy))
                PROXY_LIST[0], PROXY_LIST[current_proxy] = PROXY_LIST[current_proxy], PROXY_LIST[0]
                return PROXY_LIST[0]
            except:
                logging.warning(
                    'Ошибка при попытке отправки сообщения в канал, прокси {}, попытка {}'.format(current_proxy, i + 1))
                time.sleep(1)
                continue
    logging.error('Все прокси перепробованы, но запостить сообщение не вышло :(')
    raise Exception


# kwargs Для channel_id/proxy
def posting_to_channel(caption, *files, **kwargs):
    channel_id = CHANNEL_ID if kwargs.get('channel_id') is None else kwargs['channel_id']
    with ExitStack() as stack:
        pics = [stack.enter_context(open(fp, 'rb')) for fp in files]
        media = []
        for i in range(len(pics)):
            media.append(InputMediaPhoto(pics[i], caption) if i == 0 else InputMediaPhoto(pics[i]))
        working_proxy = check_proxy()
        safety_send_group(channel_id, media, working_proxy)
    return


# для проверки работы текущей прокси
if __name__ == '__main__':
    posting_to_channel('test', r'pics/2020-04-30/calendars/Беларусь.png', r'pics/2020-04-30/Беларусь.png')
    posting_to_channel('test', r'pics/2020-04-30/calendars/Беларусь.png', r'pics/2020-04-30/Беларусь.png')
