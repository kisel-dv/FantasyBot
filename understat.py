import json
import re
import time
import pandas as pd
from datetime import datetime, timedelta
from dateutil import parser
import html
import numpy as np

from common import request_text_soup, save_xlsx


UNDERSTAT_PATH = r'C:/Users/Dmitry/GoogleDrive/test.xlsx'
REL_HIST_DAYS = 31


def pull_understat_json(link, table_name):
    main_text, _ = request_text_soup(link)
    players_data_dirty = re.findall(table_name + r"([^;]*);", main_text)[0]
    players_data_json = re.findall(r"JSON.parse\('([^']*)'\)", players_data_dirty)[0]
    json_encoded = html.unescape(
        players_data_json.encode('utf8').decode('unicode_escape'))
    res = json.loads(json_encoded)
    return res


def pull_understat(leagues, seasons):
    dfs = {}
    for league in leagues:
        for year in seasons:
            print("Collecting {}/{}...".format(league, year))
            # собираем результирующую таблицу за сезон для игроков
            champ_link = "https://understat.com/league/{}/{}".format(league, year)
            # обработка таблицы с андерстата
            players_raw = pull_understat_json(champ_link, r'playersData')
            stats = pd.DataFrame(players_raw)
            # выделение текущей команды игрока, если за текущий сезон он заигран более, чем за 1
            stats['team_title'] = stats['team_title'].apply(lambda x: x.split(',')[0])
            # приведение признаков к нумерическим
            cols = stats.columns.drop(['id', 'player_name', 'position', 'team_title'])
            stats[cols] = stats[cols].apply(pd.to_numeric, errors='coerce')
            # установка id в виде индекса для упрощенных джойнов далее
            season_stats = stats.set_index(stats.id)

            # выделяем айдишники игроков - загружаем историю матчей для каждого из них
            history = []
            player_ids = list(stats['id'])
            t = time.time()
            for player_id in player_ids:
                player_link = "https://understat.com/player/" + player_id
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
            player_stats['matches_relevant'] = 1

            # выборка из актуальной статистики (обычно - последний месяц)
            relevant_filter = player_stats['date'] > datetime.today() - timedelta(days=REL_HIST_DAYS)
            relevant_stats = player_stats[relevant_filter].groupby(
                ['player_id']).sum(numeric_only=True).drop(['h_goals', 'a_goals'], axis=1)
            relevant_pos = player_stats[relevant_filter].groupby(
                ['player_id']).agg({'position': lambda x: ' '.join(x[::-1].unique())})

            # анализируем отдельно статистику с последнего матча, в котором участвовал данный игрок
            last_stats = player_stats.groupby(['player_id']).first(numeric_only=True).drop(['h_goals', 'a_goals'],
                                                                                           axis=1)
            last_pos = player_stats.groupby(['player_id']).first()[['position']]

            # анализируем позицию игрока по ходу сезона - формально в статистике за сезон и так есть позиция
            # season_pos = playerStats.groupby(['player_id']).agg({'position': lambda x: ' '.join(x.unique())}).rename(
            #     {'position': 'position_season'}, axis=1)
            # season = stats.join(season_pos)
            relevant_stats = relevant_stats.join(relevant_pos)
            last_stats = last_stats.join(last_pos)
            full_stats = season_stats.join(relevant_stats, rsuffix='_relevant').join(last_stats, rsuffix='_latest')

            dfs['{}-{}'.format(league, year)] = full_stats
            # :TODO ДОБАВИТЬ КОЛИЧЕСТВО МАТЧЕЙ КОМАНДЫ ЗА ПОСЛЕДНИЙ МЕСЯЦ (МБ И ЗА СЕЗОН)

    # сохранение таблиц по всем чемпионатам в виде отдельных листов в один xlsx файл
    save_xlsx(dfs, UNDERSTAT_PATH)


if __name__ == '__main__':
    # understatLeagues = ["RFPL", "EPL", "La_Liga", "Bundesliga", "Serie_A", "Ligue_1"]
    understatLeagues = ["RFPL"]
    understatSeasons = ["2020"]
    pull_understat(understatLeagues, understatSeasons)
