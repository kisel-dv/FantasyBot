import re
import time
import pandas as pd
import seaborn as sns
import logging
from datetime import datetime
from common import rus_date_convert, request_text_soup, save_pic

# выделение ссылок для каждого матча из доступной линии
prefixMarathon = 'https://www.marathonbet.ru/su/betting/'

# задание констант, описывающих маржу букмекера - для конвертации коэффициентов в вероятность
margeMarathon = 0.05
multiplierMarathon = 1/(1 + margeMarathon)


# функция для подсчета вероятности клиншитов и матожиданий забитых голов
def score_cleansheet_expected(team, match_soup):
    # коэффициенты по событиям типа "первая/вторая команда забьет больше x.5 голов"
    goals_over_prices = match_soup.find_all('span', attrs={'data-prt': 'CP', 'data-selection-key': re.compile(
        r'\d*@Total_Goals_\(' + team + r'_Team\)\d?\.Over_\d\.5')})
    # обработка
    score = 0
    addition = 0
    for goal_price in goals_over_prices:
        goals = goal_price.get('data-selection-key')[-3:]
        if goals != '1.5' and score == 0:
            score += float(goals) - 1.5
        addition = multiplierMarathon / float(goal_price.text)
        score += addition
    # коэффициенты по событиям типа "первая/вторая команда забьет/не забьет"
    cs_prices = match_soup.find_all('span', attrs={'data-prt': 'CP', 'data-selection-key': re.compile(
        r'\d*@' + team + r'_Team_To_Score\.(yes|no)')})
    cs = 0.01
    addition_0 = 1  # больше 0.5 голов
    # обработка
    for cs_price in cs_prices:
        outcome = cs_price.get('data-selection-key')[-2:]
        c = multiplierMarathon / float(cs_price.text)
        if outcome == 'no':
            cs = c
        else:
            addition_0 = c
    # прибавка, чтобы аппроксимировать маленькие коэффициенты, которых нет в линии (на большое количество забитых мячей)
    score += addition_0 + addition / 2
    return score, cs


def marathon_processing(current_champ, current_champ_links, deadline_date, match_num):
    # фиксирование времени по каждому чемпионату, логирование обработки каждого чемпионата
    champ_start_time = time.time()
    # запрос страницы с матчами по текущему чемпионату
    _, marathon_soup = request_text_soup(current_champ_links['marathon'])
    # выделение ссылки на каждый матч,
    # выделение домашней и гостевой команд, сохранение в массив словарей по каждой игре
    matches = []
    for elem in marathon_soup.find_all('div', class_='bg coupon-row'):
        # проверка даты матча
        match_date_text = elem.find('td', class_='date').text.strip()
        match_date = rus_date_convert(match_date_text)
        # обрабатываем только те матчи, которые проходят не раньше дня дедлайна по чемпионату
        if match_date >= deadline_date:
            home_team, guest_team = elem.get('data-event-name').split(' - ')
            matches.append({'link': elem.get('data-event-path'),
                            'home': home_team.strip(),
                            'guest': guest_team.strip()})
    # срез только тех матчей, которые принадлежат ближайшему туру
    match_links = matches[:match_num]
    # подсчет матожидания голов и вероятности клиншита для каждого матча - занесение всей статистики в дикту
    week_stats = {'team': [], 'cleansheet': [], 'goals': []}
    for match in match_links:
        match_link = prefixMarathon + match['link']
        _, match_soup = request_text_soup(match_link)
        expected_score_home, cs_prob_away = score_cleansheet_expected('First', match_soup)
        expected_score_away, cs_prob_home = score_cleansheet_expected('Second', match_soup)
        # расширяем дикту
        week_stats['team'].extend([match['home'], match['guest']])
        week_stats['cleansheet'].extend([cs_prob_home, cs_prob_away])
        week_stats['goals'].extend([expected_score_home, expected_score_away])

    df = pd.DataFrame(week_stats)
    # суммирование покомандно - для ситуаций, где у какой-либо команды в одном туре будет несколько матчей
    df = df.groupby(df['team']).sum()
    df = df.sort_values(by=['goals', 'cleansheet'], ascending=[0, 0])
    # установка стиля (раскраска)
    cm = sns.diverging_palette(25, 130, as_cmap=True)
    s = df.style.background_gradient(cmap=cm).set_properties(subset=['cleansheet', 'goals'],
                                                             **{'width': '40px', 'text-align': 'center'}).format(
        {'cleansheet': '{:,.2f}',
         'goals': '{:,.1f}'})
    # сохранение style объекта картинкой на диск
    directory = ("pics/" + str(datetime.now().date()) + "/")
    options = {'encoding': "UTF-8", 'width': "350", 'height': str(26 * (df.shape[0] + 2))}
    path = save_pic(s, directory, current_champ, options)

    # логирование информации о скорости обработки каждого турнира
    logging.info('Линия букмекера для "{}" обработана, время обработки: {}s'.format(current_champ, round(
        time.time() - champ_start_time, 3)))
    return path
