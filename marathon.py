import re
import time
import pandas as pd
import seaborn as sns
import logging

from common import rus_date_convert, request_text_soup

PREFIX_MARATHON = 'https://www.marathonbet.ru/su/betting/'

# задание констант, описывающих маржу букмекера - для конвертации коэффициентов в вероятность
MARGIN_MARATHON = 0.01
MULTIPLIER_MARATHON = 1/(1 + MARGIN_MARATHON)


# функция для подсчета вероятности клиншитов и матожиданий забитых голов
def score_cleansheet_expected(team, match_soup):
    # коэффициенты по событиям типа "первая/вторая команда забьет больше x.5 голов"
    goals_over_prices = match_soup.find_all('span', attrs={'data-prt': 'CP',
                                                           'data-selection-key': re.compile(r'\d*@Total_Goals_\(' +
                                                                                            team +
                                                                                            r'_Team\)\d?\.Over_\d\.5')})
    # обработка
    score = 0
    addition = 0
    for goal_price in goals_over_prices:
        goals = goal_price.get('data-selection-key')[-3:]
        if goals != '1.5' and score == 0:
            # если в линии не было события вида тотал больше 1.5, считаем, что вероятность забить больше 1.5 равна 1
            score = float(goals) - 1.5
        addition = MULTIPLIER_MARATHON / float(goal_price.text)
        score += addition
    # коэффициенты по событиям типа "первая/вторая команда забьет/не забьет"
    cs_prices = match_soup.find_all('span', attrs={'data-prt': 'CP',
                                                   'data-selection-key': re.compile(r'\d*@' + team +
                                                                                    r'_Team_To_Score\.(yes|no)')})
    cs = 0.01
    addition_0 = 1  # больше 0.5 голов
    # обработка найденных по шаблону событий
    for cs_price in cs_prices:
        outcome = cs_price.get('data-selection-key')[-2:]
        c = MULTIPLIER_MARATHON / float(cs_price.text)
        # для события "команда не забьет" - записываем вероятность в сухой матч для соперника
        # для события "команда забьет" - получаем вероятность, которую нужно просуммировать с полученной ранее суммой
        # при этом, в линии может не существовать данных событий - в таком случае будут использованы дефолтные значения
        if outcome == 'no':
            cs = c
        else:
            addition_0 = c
    # прибавка, чтобы аппроксимировать маленькие коэффициенты, которых нет в линии (на большое количество забитых мячей)
    # данная прибавка взята как половина последней вероятности, которая была слагаемым суммы
    score += addition_0 + addition / 2
    return score, cs


def get_style_params(week_stats):
    color_df = pd.DataFrame(week_stats, index=None)
    # суммирование покомандно - для ситуаций, где у какой-либо команды в одном туре будет несколько матчей
    color_df = color_df.groupby(color_df['team'], as_index=False).sum()
    color_df = color_df.sort_values(by=['goals', 'cleansheet'], ascending=[0, 0])
    # установка стиля (раскраска)
    cm = sns.diverging_palette(25, 130, as_cmap=True)
    color_s = color_df.style.background_gradient(cmap=cm, subset=['cleansheet', 'goals'])
    # для обновления параметра ctx в дикте styler объекта s - так сказать, применения раскраски
    color_s.render()
    return color_s.ctx, color_s.index


def set_style(week_stats, color_scheme, team_order):
    # а теперь уже готовим датафрейм, который и пойдет на выход
    df = pd.DataFrame(week_stats, index=None)
    # округления для улучшения зрительного восприятия
    # df.cleansheet = df.cleansheet.round(2)
    # df.goals = df.goals.round(1)
    # группировка данных по командам + форматирование данных в каждой ячейке
    df = df.groupby(df['team'], as_index=False).agg(
        {'cleansheet': lambda x: '{:.2f}'.format(sum(x)) + (' ({})'.format(
            '+'.join(map(str, map(lambda y: round(y, 2), x)))) if len(x) > 1 else ''),
         'goals': lambda x: '{:.1f}'.format(sum(x)) + (' ({})'.format(
             '+'.join(map(str, map(lambda y: round(y, 1), x)))) if len(x) > 1 else ''),
         'opponent': lambda x: ' + '.join(x) if len(x) > 1 else x})
    # применяем индексы, полученные в ходе сортировки числовых данных
    df = df.loc[team_order]
    # прячем индекс, который не нужен на выходе
    s = df.style.hide_index()
    # и, наконец, подкрутка расцветки, а именно, взятие ее из обработанного датафрейма с числовыми данными
    s.ctx = color_scheme
    # редактирование тонкостей оформления в колонках
    s = s.set_properties(subset=['cleansheet', 'goals'], **{'width': '120px', 'text-align': 'center'})
    s = s.set_properties(subset=['team'], **{'width': '210px', 'text-align': 'center', 'font-weight': 'bold'})
    s = s.set_properties(subset=['opponent'],
                         **{'width': str(max(s.data.opponent.apply(len)) * 9) + 'px', 'text-align': 'left'})
    s.render()
    return s


def marathon_processing(current_champ, current_champ_links, deadline_date, match_num):
    # фиксирование времени по каждому чемпионату, логирование обработки каждого чемпионата
    champ_start_time = time.time()
    # запрос страницы с матчами по текущему чемпионату
    link = current_champ_links['marathon']
    if not link:
        logging.error('Пустая ссылка на марафон, несмотря на то, что дедлайн близко')
        return
    _, marathon_soup = request_text_soup(link)
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
    # срез только тех матчей, которые принадлежат ближайшему туру на основании метаданных тура
    match_links = matches[:match_num]
    # обработка возможных исключений
    if not match_links:
        logging.error('{}: На марафоне не обнаружено матчей'.format(current_champ))
        return
    if len(match_links) != match_num:
        logging.warning('{}: На марафоне обнаружено меньше матчей, чем ожидалось'.format(current_champ))

    # подсчет матожидания голов и вероятности клиншита для каждого матча - занесение всей статистики в дикту
    week_stats = {'team': [], 'cleansheet': [], 'goals': [], 'opponent': []}
    for match in match_links:
        match_link = PREFIX_MARATHON + match['link']
        _, match_soup = request_text_soup(match_link)
        expected_score_home, cs_prob_away = score_cleansheet_expected('First', match_soup)
        expected_score_away, cs_prob_home = score_cleansheet_expected('Second', match_soup)
        # расширяем дикту
        week_stats['team'].extend([match['home'], match['guest']])
        week_stats['cleansheet'].extend([cs_prob_home, cs_prob_away])
        week_stats['goals'].extend([expected_score_home, expected_score_away])
        week_stats['opponent'].extend([match['guest'] + '[д]', match['home'] + '[г]'])

    '''
    раскрашиваем и сортируем датафрейм, чтобы получить корректную раскраску, а потом, выцепив эту раскраску,
    применяем ее к датафрейму, основанному на тех же данных, но содержащий текстовые данные в колонках, чтобы
    можно было четче выделять спаренные матчи в игровом туре
    '''
    color_scheme, team_order = get_style_params(week_stats)
    s = set_style(week_stats, color_scheme, team_order)
    # логирование информации о скорости обработки каждого турнира
    logging.info('{}: линия марафон обработана, время обработки: {}s'.format(current_champ,
                                                                             round(time.time() - champ_start_time, 3)))
    return s
