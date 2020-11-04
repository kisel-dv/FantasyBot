import time
import pandas as pd
import logging
from typing import Dict, List, Callable
import datetime

from common import request_text_soup
from xbet import pull_champ_winner_probs
from calendarMetrics import difficulty_probs, difficulty_table
from configFootballLinks import MATCHES_ENOUGH_TO_USE_TABLE_STATS

SIDE_MAP = {'В гостях': '(г)',
            'Дома': '(д)'}

DIFF_FUNCS = {'table': difficulty_table,
              'champion': difficulty_probs}


SPORTS_TABLE_COLS = ['games', 'won', 'draw', 'lost', 'g_scored', 'g_against', 'points']
GAMES_IN_CALENDAR = 5


def table_processing(current_champ: str, champ_link: str) -> Dict[str, float]:
    table_link = champ_link + 'table/'
    # получаем страницу с таблицей обрабатываемого чемпионата
    _, table_soup = request_text_soup(table_link)
    # выделение таблицы со страницы
    table_body = table_soup.find('tbody')
    team_body_list = table_body.find_all('tr')

    #team_links = {}
    stats = {}
    # для каждой команды из таблицы сохраним ссылку на профиль команды, все численные атрибуты
    for team in team_body_list:
        team_name = team.find('a', class_='name').get('title')
        #team_links[team_name] = team.find('a', class_='name').get('href')
        # если тур больше данной константы - обрабатываем численную статистику из таблицы - в противном случае будет {}
        team_numbers = team.find_all('td', class_=None)
        for j, n in enumerate(team_numbers):
            # для каждой команды обрабатываем каждое число-статистику из таблицы
            team_numbers[j] = int(n.text)
        team_stats = dict(zip(SPORTS_TABLE_COLS, team_numbers))
        team_stats['avg_g_scored'] = team_stats['g_scored'] / team_stats['games'] if team_stats['games'] else 0
        team_stats['avg_g_against'] = team_stats['g_against'] / team_stats['games'] if team_stats['games'] else 0
        stats[team_name] = team_stats['avg_g_scored'] - team_stats['avg_g_against']
    logging.info('{}: таблица чемпионата обработана'.format(current_champ))
    return stats


def match_proc(match):
    fields = list(map(lambda x: x.text.strip(), match.find_all('a')))
    # формально на первом месте может стоять либо дата с временем(тогда мы выцепляем дату),
    # либо первая команда - ее мы не изменим
    fields[0] = fields[0].split('|')[0]
    return fields


def week_proc(week, week_number):
    ms = list(map(lambda x: match_proc(x) + [week_number], week))
    # фильтрация перенесенных игр - если вместо даты/времени указано "перенесен", там не будет a элемента, будет span
    return list(filter(lambda x: len(x) == 5, ms))


# учитывает ситуации, когда матч перенесен вперед, т.е. туры матчей: 1-1-2-2-2-1
# возможные ситуации, которые не учтены:
# 1) матч перенесен назад: 2-1-1-1-2-2: БОЛЕЕ ТОГО, ЭТО ЛОМАЕТ АЛГОРИТМ
# 2) матч перенесен назад, идет к туру 1, но мы этого не найдем 1-1-1-2-2-2 (подразумевается деление 1-1-1-2 и 2-2)
# 3) перенесенная игра не завершает тур, а открывает его
def proc_matchweek(arr):
    max_week = 0
    for i, elem in enumerate(arr):
        if elem[-1] > max_week:
            max_week = elem[-1]
        if elem[-1] < max_week:
            arr[i][-1] = max_week
    return arr


def get_champ_calendar(current_champ_link: str, matchweek: int, teams: List[str]) -> pd.DataFrame:
    calendar_link = current_champ_link + 'calendar/'
    text, soup = request_text_soup(calendar_link)

    months = soup.find('div', class_='months')
    links = dict(map(lambda x: (x.text, x['href']), months.find_all('a')))

    full_matches = []
    # TODO:можно оптимизировать - обрабатывать, начиная с текущего месяца, иначе пропускать
    # обрабатывать условные 3 месяца, не больше
    for month, link in links.items():
        text, soup = request_text_soup(link)
        # номера всех туров на странице
        week_numbers = list(map(lambda x: int(x.text.split(' ')[0]), soup.find_all('h3')))
        # матчи с каждого тура на странице
        weeks_with_matches = soup.find_all('table', class_="stat-table")
        matches = list(map(lambda x: x.find_all('tr')[1:], weeks_with_matches))
        # обработка каждого матча + последним элементом крепим номер тура
        matches_by_week = map(week_proc, matches, week_numbers)
        # избавление от вложенности
        full_matches.extend([m for w in matches_by_week for m in w])

    sorted_matches = sorted(full_matches, key=lambda x: datetime.datetime.strptime(x[0], '%d.%m.%Y'))
    # получение номера фентези-тура из номера тура (рассматриваем и учитываем спарки)
    true_matches = proc_matchweek(sorted_matches)
    d = {}
    for current_week in range(matchweek, matchweek + 5):
        d[current_week] = {key: '' for key in teams}
        current_week_matches = filter(lambda x: x[-1] == current_week, true_matches)
        for match in current_week_matches:
            home_team = match[1]
            away_team = match[3]
            for team in [home_team, away_team]:
                if d[current_week][team]:
                    d[current_week][team] += ' + '
            d[current_week][home_team] += away_team + '(д)'
            d[current_week][away_team] += home_team + '(г)'
    return pd.DataFrame(d)


# цвет в зависимости от пороговых значений сложности
def get_color(x: float) -> str:
    # TODO: убрать в константу
    if x == -100:
        color = 'background-color: #000000'
    elif x == 100:
        color = 'background-color: #e985ff'
    elif x < -0.8:
        color = 'background-color: #CC0000'
    elif -0.8 <= x < -0.3:
        color = 'background-color: #FD7702'
    elif -0.3 <= x < 0.4:
        color = 'background-color: #FFFF19'
    elif 0.4 <= x < 1:
        color = 'background-color: #88CC00'
    else:
        color = 'background-color: #009900'
    return color


def coloring_calendar(value: pd.Series,
                      diff_func: Callable[[str, str, str, Dict[str, float]], float],
                      stats_data: Dict[str, float]) -> List[str]:
    par = []
    # из-за предобработки придет либо пустая строка, либо строка в формате 'dd.mm.yyyy <opponent>(s)', s - side
    for i, op in enumerate(value):
        if op == '':
            diff = -100
        elif '+' in op:
            diff = 100
        else:
            side_match = op[-3:]
            # последние 3 - сторона в формате (д)/(г)
            op = op[:-3].strip()
            diff = diff_func(value.index[i], op, side_match, stats_data)
        par.append(get_color(diff))
    return par


def styling_calendar(calendar: pd.DataFrame, mode: str, stats_data: Dict[str, float]):
    diff_func = DIFF_FUNCS[mode]
    calendar_colored = calendar.style.apply(lambda x: coloring_calendar(x, diff_func, stats_data))
    max_len = (calendar_colored.data.applymap(len).max().max()) * 9
    calendar_colored = calendar_colored.set_properties(subset=calendar_colored.columns,
                         **{'width': str(max_len) + 'px', 'text-align': 'left'})
    return calendar_colored


# основная функция обработки в этом модуле
def calendar_processing(current_champ: str, current_champ_links: Dict[str, str], matchweek: int):
    if current_champ == 'Корея':
        logging.error('{}: чемпионат не обрабатывается из-за дележки на две таблицы'.format(current_champ))
        return
    # логирование информации о времени обработки каждого чемпионата
    champ_start_time = time.time()
    current_champ_link = current_champ_links['sports']
    if not current_champ_link:
        logging.warning('{}: Пустая ссылка на календарь, обработка календаря пропускается...'.format(current_champ))
        return
    # обработка таблицы: table stats - dict anyway
    table_stats = table_processing(current_champ, current_champ_link)
    # обработка букмекерской линии на победителя чемпионата: champion_probs - dict anyway
    team_number = len(table_stats)
    # TODO:xbet fix
    champion_probs = {}
    #champion_probs = pull_champ_winner_probs(current_champ, matchweek, team_number)
    # обработка календаря
    champ_calendar = get_champ_calendar(current_champ_link, matchweek, list(table_stats.keys()))

    # оформление и сохранение (если tableStats и championProbs пустые, то без оформления)
    if champion_probs:
        champ_calendar = styling_calendar(champ_calendar, 'champion', champion_probs)
    elif table_stats and matchweek >= MATCHES_ENOUGH_TO_USE_TABLE_STATS:
        champ_calendar = styling_calendar(champ_calendar, 'table', table_stats)
    else:
        champ_calendar = champ_calendar.style

    # логирование времени обработки каждого чемпионата
    logging.info('{}: календарь чемпионата обработан за время: {}s'.format(current_champ,
                                                                           round(time.time() - champ_start_time, 3)))
    return champ_calendar
