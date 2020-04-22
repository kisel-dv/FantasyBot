import urllib.request
import re
import time
import pandas as pd
import imgkit
import numpy as np
import datetime
import os
from bs4 import BeautifulSoup

# первая прикидка оценить сложность календаря - юзает всего лишь среднее количество забитых и пропущенных мячей
def difficulty_avg(t1, t2, side):
    side_eff = 0.4 * ((side == '(д)') - (side == '(г)'))
    if t2 == 'Маритиму':
        t2 = 'Маритиму Мадейра'
    if t2 == 'Санта-Клара':
        t2 = 'Санта Клара'
    if (t1 in teams) and (t2 in teams):
        diff = (table_dict['avg_g_scored'][t1] - table_dict['avg_g_against'][t1]) - (
                table_dict['avg_g_scored'][t2] - table_dict['avg_g_against'][t2])
        diff = side_eff + round(diff, 2)
        return diff
    else:
        print("Error with match ", t1, " - ", t2, ": unknown club")
        return 0


def highlight_cells(value):
    par = []
    for i, op in enumerate(value):
        side = op[-3:]
        op = re.sub(r'\d{2}.\d{2}.\d{4}', '', op[:-3]).strip()
        diff = difficulty_avg(value.index[i], op, side)
        if diff < -0.8:
            par.append('background-color: #CC0000')
        elif (diff >= -0.8) and (diff <= -0.3):
            par.append('background-color: #CC6600')
        elif (diff >= -0.3) and (diff <= 0.4):
            par.append('background-color: #FFFF19')
        elif (diff >= 0.4) and (diff <= 1):
            par.append('background-color: #88CC00')
        else:
            par.append('background-color: #009900')
    return par


# сокращение "В гостях" или "Дома" до простых "(д)" и "(г)"
def side_map(side):
    return '(' + side.split(' ')[-1][0].lower() + ')'


# определение ссылок на таблицы всех чемпионатов - служит как точка входа,
# из таблицы вытаскиваются в тч ссылки на команды
champSportsLinks = (
    ["https://www.sports.ru/epl/table/", "Англия. Премьер-лига", "Англия"],
    ["https://www.sports.ru/la-liga/table/", "Испания. Ла Лига", "Испания"],
    ["https://www.sports.ru/rfpl/table/", "Россия. Премьер-лига", "Россия"],
    ["https://www.sports.ru/seria-a/table/", "Италия. Серия А", "Италия"],
    ["https://www.sports.ru/bundesliga/table/", "Германия. Бундеслига", "Германия"],
    ["https://www.sports.ru/ligue-1/table/", "Франция. Лига 1", "Франция"],
    ["https://www.sports.ru/eredivisie/table/", "Нидерланды. Высшая лига", "Нидерланды"],
    ["https://www.sports.ru/liga-zon-sagres/table/", "Португалия. Высшая лига", "Португалия"],
    ["https://www.sports.ru/championship/table/", "Англия. Чемпионшип", "Чемпионшип"],
    ["https://www.sports.ru/super-lig/table/", "Турция. Высшая лига", "Турция"]
)

# дома-в гостях - нужно будет парсить отдельно, как различные параметры потом учитывать
# https://www.sports.ru/epl/table/?s=7380&pl=home&sub=table
# https://www.sports.ru/epl/table/?s=7380&pl=guest&sub=table
# https://www.sports.ru/epl/table/?s=7380&sub=form -> форма
# https://www.sports.ru/epl/table/?s=7380&pl=home&sub=form -> форма дома/в гостях

startTime = time.time()

for champLink, champName, sheetName in champSportsLinks:
    startChampTime = time.time()
    print("Collecting " + champName + '...')

    tableSportsRequest = urllib.request.Request(champLink)
    tableSportsFull = urllib.request.urlopen(tableSportsRequest)
    tableSportsText = tableSportsFull.read().decode('utf-8')
    tableSportsSoup = BeautifulSoup(tableSportsText, 'html.parser')
    tableBody = tableSportsSoup.tbody
    teamBodyList = tableBody.find_all('tr')

    tableColumns = ["games", "won", "draw", "lost", "g_scored", "g_against", "points"]
    table_dict = {}
    teamLinks = []

    for i, team in enumerate(teamBodyList):
        teamLinks.append(team.find('a', class_='name').get('href'))
        teamName = team.find('a', class_='name').get('title')
        teamNumbers = team.find_all('td', class_=None)
        for j, n in enumerate(teamNumbers):
            teamNumbers[j] = int(n.text)
        table_dict[teamName] = dict(zip(tableColumns, teamNumbers))
        table_dict[teamName]['avg_g_scored'] = table_dict[teamName]["g_scored"] / table_dict[teamName]["games"]
        table_dict[teamName]['avg_g_against'] = table_dict[teamName]["g_against"] / table_dict[teamName]["games"]

    teams = list(table_dict.keys())
    # транспонируем этот словарь, чтобы иметь доступ в другом порядке
    table_dict = dict(pd.DataFrame(table_dict).transpose())
    # дальше мы можем в теории поработать с этой таблицей, дабы оценить сложность каждой игры

    # обработка календаря для каждой команды
    champCalendarDict = {}
    for i, teamLink in enumerate(teamLinks):
        teamLink = teamLink + 'calendar'
        teamName = teams[i]

        calendarTeamSportsRequest = urllib.request.Request(teamLink)
        calendarTeamSportsText = urllib.request.urlopen(calendarTeamSportsRequest)
        calendarTeamSportsText = calendarTeamSportsText.read().decode('utf-8')
        calendarTeamSportsSoup = BeautifulSoup(calendarTeamSportsText, 'html.parser')
        # выцепление самой таблицы с матчами
        calendarTeamSportsBody = calendarTeamSportsSoup.find('tbody')
        matchTeamList = calendarTeamSportsBody.find_all('tr')

        date = []
        competition = []
        opponent = []
        side = []
        result = []

        for match in matchTeamList:
            if 'перенесен' not in str(match):
                date.append(match.find_all('a')[0].text.split('|')[0].strip())
                competition.append(match.find_all('div')[0].text)
                opponent.append(match.find_all('div')[1].text.strip())
                side.append(match.find('td', class_="alRight padR20").text)
                result.append(match.find('a', class_='score').text.strip())

        teamCalendar = [[date[i] + ' ' + opponent[i] + side_map(side[i]),
                         competition[i]] for i in range(0, len(opponent))]

        relevantTeamCalendar = np.array(teamCalendar[result.index('превью'):])

        # нахождение последнего элемента, где указан счет сыгранного матча - должно учитываться в "перенесен"
        # r = list(map(lambda x:':' in x, result))
        # relevantTeamCalendar = np.array(teamCalendar[len(r) - r[::-1].index(True):])

        relevantTeamChampCalendar = relevantTeamCalendar[np.where(relevantTeamCalendar[:, 1] == champName)]
        champCalendarDict[teamName] = dict(zip(['1', '2', '3', '4', '5'], relevantTeamChampCalendar[:5, 0]))

        # можно взять еще номер тура, переходя на страницу с игрой,
        # но тогда придется пулять 60 лишних реквестов на команду, что сильно повышает время обработки
        # link = re.findall("class=\"score\" href=\"([^\"]*)", calendarTeamSportsText)
        # week = []
        # for i,s in enumerate(link):
        #    if not "https://www.sports.ru" in s:
        #        link[i] = "https://www.sports.ru" + s
        #    if competition[i] == "Англия. Премьер-лига":
        #        nextmatch_req = urllib.request.Request(link[i])
        #        nextmatch_text = urllib.request.urlopen(nextmatch_req)
        #        nextmatch_text = nextmatch_text.read().decode('utf-8')
        #        week.append(re.findall("Англия. Премьер-лига - (\d* тур)", nextmatch_text)[0])
        #    else:
        #        week.append('')

    champCalendar = pd.DataFrame(champCalendarDict).transpose()
    champCalendarStyle = champCalendar.style.apply(highlight_cells)
    html = champCalendarStyle.render()
    path_wkthmltoimage = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
    config = imgkit.config(wkhtmltoimage=path_wkthmltoimage)
    options = {'encoding': "UTF-8"}
    # создание директории при отсутствии оной
    directory = ("pics/" + str(datetime.datetime.now().date()) + "/calendars/")
    if not os.path.isdir(directory):
        os.makedirs(directory)
    filename = directory + sheetName
    imgkit.from_string(html, filename + ".png", config=config, options=options)

    print(champName + " collected, processing time: " + str(round(time.time() - startChampTime, 3)) + "s")

print("Calendars collected, processing time: " + str(round(time.time() - startTime, 3)) + "s")
