from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import logging
import json

from configFootballLinks import CHAMP_LINKS, XBET_TO_SPORTS_TEAM_MAP, XBET_CHAMP_NAMES, XBET_LONG_BETS
from common import request_text_soup

# путь к драйверу chrome
chromeDriver = r'C:\chromedriver'
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument('headless')  # для открытия headless-браузера
START_LINK = 'https://1xstavka.ru/line/Football/'


# функция, тянущая с 1xbet коэффициенты на чемпиона первенства
def champ_winner_probs(current_champ):
    time_start = time.time()
    browser = webdriver.Chrome(executable_path=chromeDriver, options=chromeOptions)
    if not CHAMP_LINKS[current_champ].get('1x_winner'):
        return {}
    link = CHAMP_LINKS[current_champ]['1x_winner']
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
    logging.info('{}: Линия букмекеров на победу в чемпионате собрана, время обработки: {}s'.format(current_champ, round(
        time.time() - time_start, 3)))
    return cs


def find_xbet_links(test=False):
    logging.info('Выгрузка ссылок на линии победителей чемпионатов с 1xbet')
    for current_champ in CHAMP_LINKS:
        if current_champ in XBET_LONG_BETS:
            link = XBET_LONG_BETS[current_champ]
            _, soup = request_text_soup(link)
            json_events = soup.find('script', type="application/ld+json")
            if json_events is None:
                logging.warning('{}: нет событий по ссылке из конфиг-файла'.format(current_champ))
                continue
            json_events_text = json_events.text
            list_line = json.loads(json_events_text)
            for link_meta in list_line:
                if link_meta['name'] == XBET_CHAMP_NAMES[current_champ]:
                    target_link = link_meta['url']
                    CHAMP_LINKS[current_champ]['1x_winner'] = target_link
                    logging.info('{}: ссылка на линию на чемпиона получена'.format(current_champ))
                    break
            if CHAMP_LINKS[current_champ].get('1x_winner') is None:
                logging.warning('{}: нет подходящего события'.format(current_champ))
        else:
            logging.info('{}: в конфиг-файле отсутствует ссылка на чемпионат'.format(current_champ))
    return


if __name__ == '__main__':
    find_xbet_links(True)
    print(champ_winner_probs('Корея'))
    print(champ_winner_probs('Беларусь'))
    print(champ_winner_probs('Россия'))
