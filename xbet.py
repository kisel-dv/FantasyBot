from selenium import webdriver
from configFootballLinks import CHAMP_LINKS
from bs4 import BeautifulSoup
import time
import re

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
    print('Линия букмекеров на победу в чемпионате собрана, время обработки: {}'.format(
        round(time.time() - time_start, 3)))
    return cs


# парсер для вытягивания ссылки на букмекерскую линию на победителя чемпионата
def find_xbet_links():
    browser = webdriver.Chrome(executable_path=chromeDriver, options=chromeOptions)
    try:
        for current_champ in ['Корея', 'Беларусь']:
            browser.get(START_LINK)
            search_form = browser.find_element_by_class_name('sport-search__input')
            button = browser.find_element_by_class_name('sport-search__btn')
            search_form.clear()
            search_form.send_keys(current_champ)
            button.click()
            browser.implicitly_wait(1)
            button = browser.find_element_by_class_name('search-popup__button')
            button.click()
            browser.implicitly_wait(1)
            search_count = browser.find_element_by_class_name('search-popup__title')
            count = int(search_count.find_element_by_tag_name('span').text)
            if count == 0:
                continue
            searched_text = browser.find_element_by_class_name('search-popup__input')
            print(search_count.text, searched_text.get_attribute('value'))
            search_result = browser.find_elements_by_class_name('search-popup-event')
            target_link = None
            for res_elem in search_result:
                link = res_elem.get_attribute('href')
                html_elem = res_elem.get_attribute('innerHTML')
                soup = BeautifulSoup(html_elem, 'html.parser')
                league = soup.find('div', class_='search-popup-event__league')
                if league is not None:
                    league_name = league.text
                    if 'Футбол' in league_name and current_champ in league_name and 'Победитель' in league_name:
                        target_link = link
                        break
            print(target_link)
            CHAMP_LINKS[current_champ]['1x_winner'] = target_link
    finally:
        browser.close()
        browser.quit()
    return


if __name__ == '__main__':
    find_xbet_links()
