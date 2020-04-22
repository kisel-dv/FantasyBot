import urllib.request
import re
import time
import pandas as pd
import seaborn as sns
import imgkit
import datetime
import os
from bs4 import BeautifulSoup

# чемпионаты, данные по которым необходимо собрать
targetChamps = ["Беларусь"]

# выделение ссылок для каждого матча из доступной линии
prefixMarathon = "https://www.marathonbet.ru/su/betting/"
champMarathonLinks = {
    "Беларусь": {'link': "https://www.marathonbet.ru/su/betting/Football/Belarus/Vysshaya+League",
                 'matchNum': 10,
                 'offset': 0}
}

# задание констант, описывающих маржу букмекера - для конвертации коэффициентов в вероятность
margeMarathon = 0.05
multiplierMarathon = 1/(1 + margeMarathon)


# функция для подсчета вероятности клиншитов и матожиданий забитых голов
def score_cleansheet_expected(team, match_soup):
    # коэффициенты по событиям типа "первая/вторая команда забьет больше x.5 голов"
    goals_over_coeffs = match_soup.find_all('span', attrs={'data-prt': 'CP', 'data-selection-key': re.compile(
        r'\d*@Total_Goals_\(' + team + r'_Team\)\d?\.Over_\d\.5')})
    # обработка
    score = 0
    addition = 0
    for coeff in goals_over_coeffs:
        goals = coeff.get('data-selection-key')[-3:]
        if goals != '1.5' and score == 0:
            score += float(goals) - 1.5
        addition = multiplierMarathon / float(coeff.text)
        score += addition
    # коэффициенты по событиям типа "первая/вторая команда забьет/не забьет"
    cs_coeffs = match_soup.find_all('span', attrs={'data-prt': 'CP', 'data-selection-key': re.compile(
        r'\d*@' + team + r'_Team_To_Score\.(yes|no)')})
    cs = 0.01
    addition_0 = 1  # больше 0.5 голов
    # обработка
    for coeff in cs_coeffs:
        outcome = coeff.get('data-selection-key')[-2:]
        c = multiplierMarathon / float(coeff.text)
        if outcome == 'no':
            cs = c
        else:
            addition_0 = c
    # прибавка, чтобы аппроксимировать маленькие коэффициенты, которых нет в линии (на большое количество забитых мячей)
    score += addition_0 + addition / 2
    return score, cs


# логирование информации о времени обработки
startTime = time.time()

for currentChamp in targetChamps:
    # фиксирование времени по каждому чемпионату, логирование обработки каждого чемпионата
    champStartTime = time.time()
    print("Обработка чемпионата \"" + currentChamp + "\"...")
    # выделение нужного чемпионата из маппинга
    champInfo = champMarathonLinks[currentChamp]
    # запрос страницы с матчами по текущему чемпионату
    champMainLink = champInfo['link']
    requestMainLink = urllib.request.Request(champMainLink)
    mainText = urllib.request.urlopen(requestMainLink).read().decode('utf-8')
    mainSoup = BeautifulSoup(mainText, 'html.parser')
    # выделение ссылки на каждый матч, выделение домашней и гостевой команд, сохранение в массив словарей по каждой игре
    matches = []
    for elem in mainSoup.find_all('div', class_='bg coupon-row'):
        homeTeam, guestTeam = elem.get('data-event-name').split(' - ')
        matches.append({'link': elem.get('data-event-path'),
                        'home': homeTeam.strip(),
                        'guest': guestTeam.strip()})
    matchLinks = matches[champInfo['offset']:champInfo['matchNum'] + champInfo['offset']]

    weekendStats = {'team': [], 'cleansheet': [], 'goals': []}
    for match in matches:
        matchLink = prefixMarathon + match['link']
        matchRequest = urllib.request.Request(matchLink)
        matchText = urllib.request.urlopen(matchRequest).read().decode('utf-8')
        matchSoup = BeautifulSoup(matchText, 'html.parser')
        goalsExpectedScoredHome, csProbAway = score_cleansheet_expected('First', matchSoup)
        goalsExpectedScoredAway, csProbHome = score_cleansheet_expected('Second', matchSoup)
        # расширяем дикту
        weekendStats['team'].extend([match['home'], match['guest']])
        weekendStats['cleansheet'].extend([csProbHome, csProbAway])
        weekendStats['goals'].extend([goalsExpectedScoredHome, goalsExpectedScoredAway])

    df = pd.DataFrame(weekendStats)
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
    html = s.render()
    path_wkthmltoimage = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
    # странная ошибка в строке снизу
    config = imgkit.config(wkhtmltoimage=path_wkthmltoimage)
    options = {'encoding': "UTF-8", 'width': "350", 'height': str(26 * (df.shape[0] + 2))}
    # создание директории с текущей датой в случае отсутствия оной
    directory = ("../pics/" + str(datetime.datetime.now().date()) + "/")
    if not os.path.isdir(directory):
        os.makedirs(directory)
    filename = directory + currentChamp
    # сохранение таблички и картинки по каждому чемпионату
    imgkit.from_string(html, filename + ".png", config=config, options=options)

    # логирование информации о скорости обработки каждого турнира
    print(currentChamp + " обработан, время обработки: " + str(round(time.time() - champStartTime, 3)) + "s")

# логирование информации о полном времени
print("Тур обработан, время обработки: " + str(round(time.time() - startTime, 3)) + "s")
