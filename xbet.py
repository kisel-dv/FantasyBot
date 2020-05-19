from selenium import webdriver
from bs4 import BeautifulSoup
import time
import re
import logging

from configFootballLinks import CHAMP_LINKS

# путь к драйверу chrome
chromeDriver = r'C:\chromedriver'
chromeOptions = webdriver.ChromeOptions()
chromeOptions.add_argument('headless')  # для открытия headless-браузера
START_LINK = 'https://1xstavka.ru/line/Football/'


# функция, тянущая с 1xbet коэффициенты на чемпиона первенства
def champ_winner_probs(current_champ):
    browser = webdriver.Chrome(executable_path=chromeDriver, options=chromeOptions)
    if not CHAMP_LINKS[current_champ].get('1x_winner'):
        return {}
    link = CHAMP_LINKS[current_champ]['1x_winner']
    browser.get(link)
    time_start = time.time()
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
                        team = CHAMP_LINKS[current_champ]['1x_sports_map'][team]
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


# парсер для вытягивания ссылки на букмекерскую линию на победителя чемпионата
def find_xbet_links():
    browser = webdriver.Chrome(executable_path=chromeDriver, options=chromeOptions)
    try:
        for current_champ in ['Корея', 'Беларусь']:
            # если данный чемпионат не входит в список релевантных, то пропустить его
            if CHAMP_LINKS[current_champ].get('match_num') is None:
                continue
            browser.get(START_LINK)
            # нахождение поискового окна и кнопки поиска, очистка формы
            search_form = browser.find_element_by_class_name('sport-search__input')
            button = browser.find_element_by_class_name('sport-search__btn')
            search_form.clear()
            # ввод текущего чемпионата в посиковое окно
            search_form.send_keys(current_champ)
            button.click()
            browser.implicitly_wait(2)
            # нахождение кнопки поиска во всплывшем окне и клик
            button = browser.find_element_by_class_name('search-popup__button')
            button.click()
            browser.implicitly_wait(2)
            # количество результатов поиска
            search_count = browser.find_element_by_class_name('search-popup__title')
            count = int(search_count.find_element_by_tag_name('span').text)
            if count == 0:
                continue
            # DEBUG print
            searched_text = browser.find_element_by_class_name('search-popup__input')
            print(search_count.text, searched_text.get_attribute('value'))
            # взятие всех результатов поиска и проверка каждого из них на предмет соответствия целевому чемпионату
            search_result = browser.find_elements_by_class_name('search-popup-event')
            target_link = None
            for res_elem in search_result:
                link = res_elem.get_attribute('href')
                html_elem = res_elem.get_attribute('innerHTML')
                soup = BeautifulSoup(html_elem, 'html.parser')
                league = soup.find('div', class_='search-popup-event__league')
                if league is not None:
                    league_name = league.text
                    # TODO: переписать, неправильно работает в общем случае
                    if 'Футбол' in league_name and current_champ in league_name and 'Победитель' in league_name:
                        target_link = link
                        break
            print(target_link)
            CHAMP_LINKS[current_champ]['1x_winner'] = target_link
            logging.info('{}: cсылка на 1xbet линию на чемпиона получена'.format(current_champ))
    finally:
        browser.close()
        browser.quit()
    return
