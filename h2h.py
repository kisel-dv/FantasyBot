import urllib.request
import json
from bs4 import BeautifulSoup
import pandas as pd
import os

from common import save_xlsx, request_text_soup

h2h_links = {'Россия': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/179',
             'Франция': '',
             'Германия': '',
             'Испания': '',
             'Англия': '',
             'Италия': ''}

suffix = "?filter%5Bamplua_id%5D=0&filter%5Bsport_team_id%5D=0&filter%5Bname%5D=&filter%5Bteam_keyword%5D=&filter%5Bpopularity_index%5D=&filter%5Blast_price%5D=0%3B3200&sort%5Bpoints%5D=desc&offset={}&ajax=1"
threshold = 100

H2H_COLUMNS = ['Амплуа', 'Клуб', 'Имя', '$', 'sports_id']


def update_h2h():
    for current_champ, current_link in h2h_links.items():
        if not current_link:
            continue
        link = current_link + suffix
        offset = 0

        # cycle to pull all data - in every update we are getting some numbers of players
        keys = []
        player_data = []
        while offset == 0 or len(all_players):
            _, soup = request_text_soup(link.format(offset), func=lambda x: json.loads(x)['data'])
            # getting keys
            if offset == 0:
                for t in soup.find_all('tr')[1].find_all('th'):
                    keys.append(t.text.strip())

            all_players = soup.find_all('tr')[2:]
            # if no update available with new offset - we just skip this step and next go out from cycle
            if len(all_players):
                # if any updates available - parse every available cell
                for player in all_players:
                    cells = player.find_all('td')
                    p = []
                    for i, t in enumerate(cells):
                        p.append(t.text.strip())
                    # link hack - "переобработка для последнего" - берем только айди, либо текстовый айди
                    p[-1] = t.find('a', title="Профиль игрока").get('href').strip().split('/')[-2]
                    player_data.append(p)

            offset = offset + threshold

        # создание датафрейма
        df = pd.DataFrame(dict(zip(keys, list(map(list, zip(*player_data))))))
        df = df.rename(columns={'': 'sports_id',
                                'А': 'Амплуа'})
        # чтобы убрать игроков, по которым нет полной информации - нет меты, нет ссылки на профиль
        df = df[df['$'] != '0']
        df['$'] = df['$'].apply(pd.to_numeric, errors='coerce')
        dfs = {current_champ: df[H2H_COLUMNS]}

        # todo: СДЕЛАТЬ НОРМАЛЬНОЕ СОХРАНЕНИЕ, ВЫНЕСТИ ПРОВЕРКУ ДИРЕКТОРИИ В КОММОН путь в конфиг, проверять папку на наличие. КСТАТИ ПАПКУ ЛОГОВ МЫ ТОЖЕ НЕ ПРОВЕРЯЕМ
        directory = r'data/h2h/'
        if not os.path.isdir(directory):
            os.makedirs(directory)
        path = directory + current_champ + ".xlsx"
        save_xlsx(dfs, path)


if __name__ == '__main__':
    update_h2h()
