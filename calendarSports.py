import time
import pandas as pd
import logging
from math import log

from common import request_text_soup
from xbet import pull_champ_winner_probs


# захардкоженные имена для нескольких клубов, для которых имена в разных местах на спортс.ру отличаются
typoMap = {'Маритиму': 'Маритиму Мадейра',
           'Санта-Клара': 'Санта Клара'}
# сокращение "В гостях" или "Дома" до простых "(д)" и "(г)"
sideMap = {'В гостях': '(г)',
           'Дома': '(д)'}


def table_processing(current_champ, champ_link):
    table_link = champ_link + 'table/'
    # получаем страницу с таблицей обрабатываемого чемпионата
    _, table_soup = request_text_soup(table_link)
    # выделение таблицы со страницы
    table_body = table_soup.find('tbody')
    team_body_list = table_body.find_all('tr')
    # колонки футбольных таблиц на sports.ru - численные атрибуты каждой команды
    table_columns = ['games', 'won', 'draw', 'lost', 'g_scored', 'g_against', 'points']
    team_links = {}
    stats = {}
    # для каждой команды из таблицы сохраним ссылку на профиль команды, все численные атрибуты
    for team in team_body_list:
        team_name = team.find('a', class_='name').get('title')
        team_links[team_name] = team.find('a', class_='name').get('href')
        # если тур больше данной константы - обрабатываем численную статистику из таблицы - в противном случае будет {}
        team_numbers = team.find_all('td', class_=None)
        for j, n in enumerate(team_numbers):
            team_numbers[j] = int(n.text)
        stats[team_name] = dict(zip(table_columns, team_numbers))
        stats[team_name]['avg_g_scored'] = stats[team_name]['g_scored'] / stats[team_name][
            'games'] if stats[team_name]['games'] else 0
        stats[team_name]['avg_g_against'] = stats[team_name]['g_against'] / stats[team_name][
            'games'] if stats[team_name]['games'] else 0
    # транспонируем этот словарь, чтобы иметь доступ в другом порядке
    # (вместо team_name -> games -> 5 получаем games -> team_name -> 5)
    # для случая, когда мы не хотим обрабатывать таблицу из-за малого количества туров, получим {}
    table_stats = dict(pd.DataFrame(stats).transpose())
    logging.info('{}: таблица чемпионата обработана'.format(current_champ))
    return team_links, table_stats


# безопасное взятие первых n матчей
def get_first_matches(matches, n):
    m = len(matches)
    # добавит пустые строчки, если количество оставшихся в календаре матчей меньше n
    return [matches[x] for x in range(m)] + ['' for _ in range(n - m)]


def get_champ_calendar(current_champ, current_champ_link, team_links):
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
            if 'перенесен' not in str(match):
                date = match.find('a').text.split('|')[0].strip()
                opponent = match.find_all('div')[1].text.strip()
                side = sideMap[match.find('td', class_='alRight padR20').text]
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
        # взятие ближайших 5 игр для каждой команды
        champ_calendar_dict[team] = dict(
            zip(['1', '2', '3', '4', '5'], get_first_matches(future_team_calendar_champ, 5)))
    # транспонирование таблицы
    champ_calendar = pd.DataFrame(champ_calendar_dict).transpose()
    return champ_calendar


# функция для вычисления сложности календаря на основе средней статистики за текущее первенство
def diff_table(t1, t2, side, stats_data):
    # поправка на место проведения игры - высчитана средняя в среднем для крупных европейских чемпионатов
    side_eff = 0.4 * ((side == '(д)') - (side == '(г)'))
    # захардкоженные имена для нескольких клубов, для которых имена в разных местах на спортс.ру отличаются
    if typoMap.get(t2):
        t2 = typoMap[t2]
    # tableStats - глобальный, для доступа к переменной из основной функции обработки
    try:
        diff = (stats_data['avg_g_scored'][t1] - stats_data['avg_g_against'][t1]) - (
                stats_data['avg_g_scored'][t2] - stats_data['avg_g_against'][t2])
        diff = side_eff + round(diff, 2)
        return diff
    except KeyError:
        # если нашлась новая проблема с разными названиями в разных местах на спортс ру
        logging.error('Неизвестный клуб, матч {} - {}'.format(t1, t2))
        return 0


# функция для вычисления сложности календаря на основе букмекерских котиовок на чемпиона
def difficulty_probs(t1, t2, side, stats_data):
    if side == '(г)':
        t1, t2 = t2, t1
    diff = 1.4 * (0.23 + 0.175*log(stats_data[t1]) - 0.148*log(stats_data[t2]))
    return ((side == '(д)') - (side == '(г)')) * diff


diff_funcs = {'table': diff_table,
              'champion': difficulty_probs}


# цвет в зависимости от пороговых значений сложности
def get_color(x):
    if x < -0.8:
        color = 'background-color: #CC0000'
    elif (x >= -0.8) and (x <= -0.3):
        color = 'background-color: #fd7702'
    elif (x >= -0.3) and (x <= 0.4):
        color = 'background-color: #FFFF19'
    elif (x >= 0.4) and (x <= 1):
        color = 'background-color: #88CC00'
    else:
        color = 'background-color: #009900'
    return color


def coloring_calendar(value, color_func, stats_data):
    par = []
    for i, op in enumerate(value):
        if op == '':
            diff = 0
        else:
            side_match = op[-3:]
            # первые 10 символов - дата в формете dd.mm.yyyy, последние 3 - сторона в формате (д)/(г)
            op = op[10:-3].strip()
            diff = color_func(value.index[i], op, side_match, stats_data)
        par.append(get_color(diff))
    return par


# функция для стайлинга - раскраски таблицы
def styling_calendar(calendar, mode, stats_data):
    color_func = diff_funcs[mode]
    calendar_colored = calendar.style.apply(lambda x: coloring_calendar(x, color_func, stats_data))
    return calendar_colored


# основная функция обработки в этом модуле
def calendar_processing(current_champ, current_champ_links, matchweek):
    # логирование информации о времени обработки каждого чемпионата
    champ_start_time = time.time()
    current_champ_link = current_champ_links['sports']
    if not current_champ_link:
        logging.warning(current_champ +
                        ': Для данного чемпионата календарь недоступен, обработка календаря пропускается...')
        return
    # обработка таблицы: table stats - dict anyway
    team_links, table_stats = table_processing(current_champ, current_champ_link)
    # обработка букмекерской линии на победителя чемпионата: champion_probs - dict anyway
    champion_probs = pull_champ_winner_probs(current_champ, matchweek)
    # обработка календаря
    champ_calendar = get_champ_calendar(current_champ, current_champ_link, team_links)

    # бывают случаи, когда 1хбет дает не полную линию - не для всех команд
    if len(champion_probs) != len(table_stats['games']):
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
    logging.info('{}: календарь чемпионата обработан, время обработки: {}s'.format(current_champ, round(
        time.time() - champ_start_time, 3)))
    return champ_calendar
