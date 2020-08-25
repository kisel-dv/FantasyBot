import time
import pandas as pd
import logging
from typing import Tuple, Dict, List, Callable

from common import request_text_soup
from xbet import pull_champ_winner_probs
from calendarMetrics import difficulty_probs, difficulty_table

SIDE_MAP = {'В гостях': '(г)',
            'Дома': '(д)'}

DIFF_FUNCS = {'table': difficulty_table,
              'champion': difficulty_probs}


SPORTS_TABLE_COLS = ['games', 'won', 'draw', 'lost', 'g_scored', 'g_against', 'points']
GAMES_IN_CALENDAR = 5


def table_processing(current_champ: str, champ_link: str) -> Tuple[Dict[str, str],
                                                                   Dict[str, float]]:
    table_link = champ_link + 'table/'
    # получаем страницу с таблицей обрабатываемого чемпионата
    _, table_soup = request_text_soup(table_link)
    # выделение таблицы со страницы
    table_body = table_soup.find('tbody')
    team_body_list = table_body.find_all('tr')

    team_links = {}
    stats = {}
    # для каждой команды из таблицы сохраним ссылку на профиль команды, все численные атрибуты
    for team in team_body_list:
        team_name = team.find('a', class_='name').get('title')
        team_links[team_name] = team.find('a', class_='name').get('href')
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
    return team_links, stats


# безопасное взятие первых n матчей
def get_first_matches(matches: List[str], n: int) -> List[str]:
    m = len(matches)
    # добавит пустые строчки, если количество оставшихся в календаре матчей меньше n
    return [matches[x] for x in range(m)] + ['' for _ in range(n - m)]


# TODO: реворк обработки календаря чтобы лучше ловить спарки
def get_champ_calendar(current_champ: str, current_champ_link: str, team_links: Dict[str, str]) -> pd.DataFrame:
    champ_calendar_dict = {}
    for team, team_link in team_links.items():
        team_link = team_link + 'calendar/'
        # запрос страницы с календарем для каждой команды
        ''' (в теории можно обрабатывать через календарь соревнования)
        (НО - на спортс в таком случае не обязательна сортировка по дате 
        - используется сортировка по ФОРМАЛЬНОМУ туру)'''
        _, calendar_team_soup = request_text_soup(team_link)
        # выцепление самой таблицы с календарем матчей
        calendar_team_body = calendar_team_soup.find('tbody')
        # получение списка матчей
        match_team_list = calendar_team_body.find_all('tr')

        events = []
        competitions = []
        results = []
        for match in match_team_list:
            # убираем из рассмотрения матчи с пометкой "перенесен" вместо даты
            if 'перенесен' in str(match):
                continue
            date = match.find('a').text.split('|')[0].strip()
            opponent = match.find_all('div')[1].text.strip()
            side = SIDE_MAP[match.find('td', class_='alRight padR20').text]
            events.append(date + ' ' + opponent + side)
            results.append(match.find('a', class_='score').text.strip())
            competitions.append(match.div.a.get('href'))

        # выделение календаря будущих игр - их мы находим по наличию ссылки на превью вместо счета
        future_index = results.index('превью') if 'превью' in results else len(results)
        # берем из списка будущих игр только те, которые будут проходить в интересующем нас чемпионате
        # для проверки используем ссылку на чемпионат из нашего маппинга, сравнивая ее со ссылкой на
        # чемпионат, который соответствует обрабатываемой игре
        future_team_calendar_champ = [events[idx]
                                      for idx, elem in enumerate(competitions)
                                      if current_champ_link in elem and idx >= future_index]
        # взятие ближайших N игр для каждой команды
        champ_calendar_dict[team] = dict(zip([str(i) for i in range(GAMES_IN_CALENDAR)],
                                             get_first_matches(future_team_calendar_champ, GAMES_IN_CALENDAR)))
    # транспонирование таблицы
    champ_calendar = pd.DataFrame(champ_calendar_dict).transpose()
    logging.info('{}: календарь чемпионата собран'.format(current_champ))
    return champ_calendar


# цвет в зависимости от пороговых значений сложности
def get_color(x: float) -> str:
    if x < -0.8:
        color = 'background-color: #CC0000'
    elif (x >= -0.8) and (x <= -0.3):
        color = 'background-color: #FD7702'
    elif (x >= -0.3) and (x <= 0.4):
        color = 'background-color: #FFFF19'
    elif (x >= 0.4) and (x <= 1):
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
            diff = 0
        else:
            side_match = op[-3:]
            # первые 10 символов - дата в формете dd.mm.yyyy, последние 3 - сторона в формате (д)/(г)
            op = op[10:-3].strip()
            diff = diff_func(value.index[i], op, side_match, stats_data)
        par.append(get_color(diff))
    return par


def styling_calendar(calendar: pd.DataFrame, mode: str, stats_data: Dict[str, float]):
    diff_func = DIFF_FUNCS[mode]
    calendar_colored = calendar.style.apply(lambda x: coloring_calendar(x, diff_func, stats_data))
    return calendar_colored


# основная функция обработки в этом модуле
def calendar_processing(current_champ: str, current_champ_links: Dict[str, str], matchweek: int):
    # логирование информации о времени обработки каждого чемпионата
    champ_start_time = time.time()
    current_champ_link = current_champ_links['sports']
    if not current_champ_link:
        logging.warning('{}: Пустая ссылка на календарь, обработка календаря пропускается...'.format(current_champ))
        return
    # обработка таблицы: table stats - dict anyway
    team_links, table_stats = table_processing(current_champ, current_champ_link)
    # обработка букмекерской линии на победителя чемпионата: champion_probs - dict anyway
    champion_probs = pull_champ_winner_probs(current_champ, matchweek)
    # обработка календаря
    champ_calendar = get_champ_calendar(current_champ, current_champ_link, team_links)

    # бывают случаи, когда 1хбет дает не полную линию - не для всех команд
    if len(champion_probs) != len(table_stats):
        logging.warning('{}: Линия на победителя чемпионата неполная'.format(current_champ))
        champion_probs = {}
    # оформление и сохранение (если tableStats и championProbs пустые, то без оформления)
    if champion_probs:
        champ_calendar = styling_calendar(champ_calendar, 'champion', champion_probs)
    elif table_stats:
        champ_calendar = styling_calendar(champ_calendar, 'table', table_stats)
    else:
        champ_calendar = champ_calendar.style

    # логирование времени обработки каждого чемпионата
    logging.info('{}: календарь чемпионата обработан за время: {}s'.format(current_champ,
                                                                           round(time.time() - champ_start_time, 3)))
    return champ_calendar
