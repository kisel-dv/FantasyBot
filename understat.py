import json
import re
import time
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser
import html
import os

from common import request_text_soup, save_xlsx


UNDERSTAT_PATH = r'C:/Users/Dmitry/GoogleDrive/test.xlsx'
MAPPING_PATH = r'C:/Users/Dmitry/PycharmProjects/FantasyBot/data/understat-h2h.xlsx'
UNRESOLVED_MAPPING_PATH = r'data/understat-h2h missing.xlsx'

REL_HIST_DAYS = 31
UNDERSTAT_PLAYER_PREFIX = 'https://understat.com/player/'


COMMON_COLUMNS = ['games', 'time', 'goals', 'assists',
                  'xG', 'xA',
                  'shots', 'key_passes']

EXCEPT_COLUMNS = ['games_latest']

POSTFIXES = ['', '_latest', '_relevant']

TARGET_COLUMNS = ['Имя', 'Клуб', 'Амплуа', '$', 'position_latest', 'position_relevant'] + \
                 [a + b for b in POSTFIXES for a in COMMON_COLUMNS if a + b not in EXCEPT_COLUMNS]


UNDERSTAT_LEAGUES = {'Россия': 'RFPL',
                     'Англия': 'EPL',
                     'Испания': 'La_Liga',
                     'Германия': 'Bundesliga',
                     'Италия': 'Serie_A',
                     'Франция': 'Ligue_1'}

#UNDERSTAT_LEAGUES = {'Россия': 'RFPL'}
UNDERSTAT_SEASONS = ["2020"]


def pull_understat_json(link, table_name):
    main_text, _ = request_text_soup(link)
    players_data_dirty = re.findall(table_name + r"([^;]*);", main_text)[0]
    players_data_json = re.findall(r"JSON.parse\('([^']*)'\)", players_data_dirty)[0]
    json_encoded = html.unescape(
        players_data_json.encode('utf8').decode('unicode_escape'))
    res = json.loads(json_encoded)
    return res


def update_mapping_h2h():
    if not os.path.isfile(UNRESOLVED_MAPPING_PATH):
        # TODO логирование
        return
    missing = pd.read_excel(UNRESOLVED_MAPPING_PATH)
    if not missing.shape[0]:
        return

    # деление фрейма на часть, где соотношение установлено и где нет
    unresolved = missing[missing['sports'].isnull()]
    resolved = missing[missing['sports'].notnull()]
    # подгрузка уже существующего отображения
    if os.path.isfile(MAPPING_PATH):
        mapping = pd.read_excel(MAPPING_PATH)
    else:
        mapping = pd.DataFrame(columns=['understat', 'sports'])

    resolved = resolved[~resolved['understat'].isin(mapping['understat'])]
    # присоединение к существующему маппингу новых элементов
    mapping = mapping.append(resolved)
    # сохранение обновленных файлов - дополненного маппинга и сокращенного списка неразрешенных соотеошений
    save_xlsx({'': mapping}, MAPPING_PATH)
    save_xlsx({'': unresolved}, UNRESOLVED_MAPPING_PATH)
    return


def update_understat_missing(missing_ids):
    # преобразование в ссылку на игрока
    missing_links = map(lambda x: UNDERSTAT_PLAYER_PREFIX + x, missing_ids)
    # если файл с неразрешенными игроками уже существовал, то фильтруем по нему дубликаты
    if os.path.isfile(UNRESOLVED_MAPPING_PATH):
        missing_old = pd.read_excel(UNRESOLVED_MAPPING_PATH)
        old = list(missing_old['understat'])
        missing_links = old + [i for i in missing_links if i not in old]
    # создаем новый фрейм и заполняем его новым полным списком незамапленных игроков
    missing = pd.DataFrame()
    missing['understat'] = missing_links
    missing['sports'] = ''
    save_xlsx({'': missing}, UNRESOLVED_MAPPING_PATH)
    return


def pull_understat():
    dfs = {}
    # TODO проверка на существование файла, логирование, если его нет
    h2h_m = pd.read_excel(MAPPING_PATH)
    # вычленение непосредственно айдишника
    h2h_m['understat'] = h2h_m['understat'].apply(lambda x: x.split('/')[-1])
    h2h_m['sports'] = h2h_m['sports'].apply(lambda x: x.split('/')[-2])
    # сборка маппинга из understat в sports айди
    h2h_m = dict(zip(h2h_m['understat'], h2h_m['sports']))

    missing_ids = []

    for current_champ, understat_name in UNDERSTAT_LEAGUES.items():
        if current_champ not in ['Россия', 'Франция']:
            continue
        for year in UNDERSTAT_SEASONS:
            # TODO КЭШИРОВАНИЕ - КАК МИНИМУМ, КАЛЕНДАРЯ, КОТИРОВОК НА ЧЕМПИОНСТВО, АНДЕРСТАТ ДАННЫХ
            print("Collecting {}/{}...".format(understat_name, year))
            # собираем результирующую таблицу за сезон для игроков
            champ_link = "https://understat.com/league/{}/{}".format(understat_name, year)
            # обработка таблицы с андерстата
            players_raw = pull_understat_json(champ_link, r'playersData')
            stats = pd.DataFrame(players_raw)
            # выделение текущей команды игрока, если за текущий сезон он заигран более, чем за 1
            stats['team_title'] = stats['team_title'].apply(lambda x: x.split(',')[0])
            # приведение признаков к численным
            cols = stats.columns.drop(['id', 'player_name', 'position', 'team_title'])
            stats[cols] = stats[cols].apply(pd.to_numeric, errors='coerce')
            stats['time'] = stats['time']/stats['games']
            # установка id в виде индекса для упрощенных джойнов далее
            season_stats = stats.set_index(stats.id)

            # выделяем айдишники игроков - загружаем историю матчей для каждого из них
            history = []
            player_ids = list(stats['id'])
            t = time.time()
            for player_id in player_ids:
                player_link = UNDERSTAT_PLAYER_PREFIX + player_id
                # загружаем его личную статистику из таблицы с андерстата
                stat = pull_understat_json(player_link, r'matchesData	')
                # добавляем в каждую игру из истории id игрока
                for s in stat:
                    s.update({'player_id': player_id})
                # расширяем лист с индивидуальной статистикой по каждому матчу матчами данного игрока
                history.extend(stat)
            print(time.time() - t)
            # переходим к таблицам
            player_stats = pd.DataFrame(history)
            # фильтруем все, что не относится к рассматриваемому сезону
            player_stats = player_stats[player_stats['season'] == year]

            # конвертируем все числовые поля
            cols = player_stats.columns.drop(
                ['position', 'h_team', 'a_team', 'date', 'id', 'season', 'roster_id', 'player_id'])
            player_stats[cols] = player_stats[cols].apply(pd.to_numeric, errors='coerce')
            player_stats['xGxA_relevant'] = player_stats['xG'] + player_stats['xA']
            player_stats['date'] = player_stats['date'].apply(parser.parse)
            # проставляем константную 1, чтобы потом удобно получать количество игр суммой
            player_stats['games'] = 1

            # выборка из актуальной статистики (обычно - последний месяц)
            relevant_filter = player_stats['date'] > datetime.today() - timedelta(days=REL_HIST_DAYS)
            relevant_stats = player_stats[relevant_filter].groupby(
                ['player_id']).sum(numeric_only=True).drop(['h_goals', 'a_goals'], axis=1)
            relevant_stats['time'] = relevant_stats['time']/relevant_stats['games']
            relevant_pos = player_stats[relevant_filter].groupby(
                ['player_id']).agg({'position': lambda x: ' '.join(x[::-1].unique())})
            relevant_stats = relevant_stats.join(relevant_pos)

            # анализируем отдельно статистику с последнего матча, в котором участвовал данный игрок
            last_stats = player_stats.groupby(['player_id']).first(numeric_only=True).drop(['h_goals', 'a_goals'],
                                                                                           axis=1)
            last_pos = player_stats.groupby(['player_id']).first()[['position']]
            last_stats = last_stats.join(last_pos)

            # TODO ДОБАВИТЬ КОЛИЧЕСТВО МАТЧЕЙ КОМАНДЫ ЗА ПОСЛЕДНИЙ МЕСЯЦ (МБ И ЗА СЕЗОН)
            # анализируем позицию игрока по ходу сезона - формально в статистике за сезон и так есть позиция
            # season_pos = playerStats.groupby(['player_id']).agg({'position': lambda x: ' '.join(x.unique())}).rename(
            #     {'position': 'position_season'}, axis=1)
            # season = stats.join(season_pos)

            # соединяем все имеющиеся данные
            full_stats = season_stats.join(relevant_stats, rsuffix='_relevant').join(last_stats, rsuffix='_latest')
            # добавление связи с h2h данными - через маппинг ссылок на игроков
            full_stats['sports_id'] = full_stats['id'].apply(lambda x: h2h_m.get(x))

            # TODO ДЖОЙН В ДРУГУЮ СТОРОНУ?
            # и подтягиваем метаинформацию с h2h - позицию, цену
            players_meta = pd.read_excel(r'C:/Users/Dmitry/PycharmProjects/FantasyBot/data/h2h/{}.xlsx'.format(
                current_champ))
            full_stats = full_stats.merge(players_meta, left_on='sports_id', right_on='sports_id', how='left')

            # добавляем таблицу в словарь на последующее сохранение
            dfs['{}-{}'.format(understat_name, year)] = full_stats[TARGET_COLUMNS].round(2)

            # запись understat-id, которые не вышло отобразить в sports-id
            missing_ids.extend(list(full_stats[full_stats['sports_id'].isnull()]['id']))

    # сохранение таблиц по всем чемпионатам в виде отдельных листов в один xlsx файл
    # TODO СТАЙЛИНГ ПО ЦЕЛЕВЫМ ПРИЗНАКАМ
    save_xlsx(dfs, UNDERSTAT_PATH)
    # обновление таблицы с неотображенными understat-id
    update_understat_missing(missing_ids)


if __name__ == '__main__':
    # TODO СВЯЗАТЬ С ОБНОВЛЕНИЕМ Н2Н?
    # обновление маппингов перед запуском апдейта understat статистики
    update_mapping_h2h()
    # обновление статистики
    pull_understat()
