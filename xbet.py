from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import logging
import json

from configFootballLinks import XBET_TO_SPORTS_TEAM_MAP, XBET_CHAMP_NAMES, XBET_LONG_BETS, \
    MATCHES_ENOUGH_TO_USE_TABLE_STATS
from common import request_text_soup

# путь к драйверу chrome
chromeDriver = r'C:\chromedriver'
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument('headless')  # для открытия headless-браузера
START_LINK = 'https://1xstavka.ru/line/Football/'


# функция, тянущая с 1xbet коэффициенты на чемпиона первенства
def pull_champ_winner_probs(current_champ, matchweek):
    if matchweek > MATCHES_ENOUGH_TO_USE_TABLE_STATS:
        logging.info('{}: сыграно достаточно матчей, чтобы использовать табличную статистику'.format(
            current_champ))
        return {}
    time_start = time.time()
    link = find_xbet_link(current_champ)
    if link is None:
        logging.error('{}: ссылка на 1xbet данные не найдена'.format(current_champ))
        return {}
    browser = webdriver.Chrome(executable_path=chromeDriver, options=chromeOptions)
    browser.get(link)
    try:
        page_html = browser.page_source
        soup = BeautifulSoup(page_html, 'html.parser')
        bets = soup.find('div', class_=re.compile('bets betCols[12]')).find_all('div')
        cs = {}
        for bet in bets:
            spans = bet.find_all('span')
            if spans:
                bet_text = spans[0].text.split(' - ')
                team = bet_text[0]
                res = bet_text[1]
                if res[:2] == 'Да':
                    try:
                        team = XBET_TO_SPORTS_TEAM_MAP[current_champ][team]
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
    if current_champ not in XBET_LONG_BETS:
        logging.info('{}: в конфиг-файле отсутствует 1xbet-ссылка на данный чемпионат'.format(current_champ))
        return
    link = XBET_LONG_BETS[current_champ]
    _, soup = request_text_soup(link)
    json_events = soup.find('script', type="application/ld+json")
    if json_events is None:
        logging.warning('{}: нет событий по ссылке из конфиг-файла'.format(current_champ))
        return
    json_events_text = json_events.text
    list_line = json.loads(json_events_text)
    for link_meta in list_line:
        if link_meta['name'] == XBET_CHAMP_NAMES[current_champ]:
            target_link = link_meta['url']
            logging.info('{}: ссылка на линию на чемпиона получена'.format(current_champ))
            return target_link
    logging.warning('{}: нет подходящего события'.format(current_champ))
    return
