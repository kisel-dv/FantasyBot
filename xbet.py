import time
import re
import logging
import json
from selenium import webdriver
from bs4 import BeautifulSoup

from configFootballLinks import XBET_CHAMP_LINKS
from common import request_text_soup
from config import CHROME_DRIVER_PATH


CHROME_OPTIONS = webdriver.ChromeOptions()
CHROME_OPTIONS.add_argument('headless')  # для открытия headless-браузера

# количество матчей, начиная с которой мы можем использовать статистику из таблицы лиги
MATCHES_ENOUGH_TO_USE_TABLE_STATS = 5


# функция, тянущая с 1xbet коэффициенты на чемпиона первенства
def pull_champ_winner_probs(current_champ, matchweek):
    time_start = time.time()
    if matchweek > MATCHES_ENOUGH_TO_USE_TABLE_STATS:
        logging.info('{}: сыграно достаточно матчей для табличной статистики'.format(current_champ))
        return {}
    if current_champ not in XBET_CHAMP_LINKS:
        logging.info('{}: в конфиг-файле отсутствует 1xbet-ссылка на данный чемпионат'.format(current_champ))
        return {}
    link = find_xbet_link(current_champ)
    if link is None:
        logging.error('{}: ссылка на 1xbet данные не найдена'.format(current_champ))
        return {}
    browser = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH, options=CHROME_OPTIONS)
    browser.get(link)
    try:
        page_html = browser.page_source
        soup = BeautifulSoup(page_html, 'html.parser')
        bets = soup.find('div', class_=re.compile('bets betCols[12]')).find_all('div')
        cs = {}
        for bet in bets:
            spans = bet.find_all('span')
            if not spans:
                continue
            bet_text = spans[0].text.split(' - ')
            team = bet_text[0]
            res = bet_text[1]
            if res[:2] == 'Да':
                try:
                    team = XBET_CHAMP_LINKS[current_champ]['sports_map'][team]
                except KeyError:
                    print('Команда {} не найдена в маппинге в sports.ru имена'.format(team))
                    raise Exception
                coeff = float(spans[1].text)
                cs[team] = 1/coeff
    finally:
        browser.close()
        browser.quit()
    for k, v in cs.items():
        cs[k] = v/sum(cs.values())
    logging.info(
        '{}: Линия букмекеров на победу в чемпионате собрана, время обработки: {}s'.format(
            current_champ, round(time.time() - time_start, 3)))
    return cs


def find_xbet_link(current_champ):
    logging.info('{}: Выгрузка ссылки на линии победителей чемпионатов с 1xbet'.format(current_champ))
    link = XBET_CHAMP_LINKS[current_champ]['link']
    _, soup = request_text_soup(link)
    json_events = soup.find('script', type="application/ld+json")
    if json_events is None:
        logging.warning('{}: нет событий по ссылке из конфиг-файла'.format(current_champ))
        return
    json_events_text = json_events.text
    list_line = json.loads(json_events_text)

    for link_meta in list_line:
        if link_meta['name'] != XBET_CHAMP_LINKS[current_champ]['name']:
            continue
        target_link = link_meta['url']
        logging.info('{}: ссылка на линию на чемпиона получена'.format(current_champ))
        return target_link
    logging.warning('{}: нет подходящего события'.format(current_champ))
    return
