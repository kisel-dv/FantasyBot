import time
import pandas as pd
import imgkit
import datetime
import os
from common import request_text_soup
from common import champLinks

# чемпионаты, которые мы хотим обработать
targetChamps = ['Беларусь']


# функция для вычисления сложности календаря
def difficulty_avg(t1, t2, side_match):
    side_eff = 0.4 * ((side_match == '(д)') - (side_match == '(г)'))
    if t2 == 'Маритиму':
        t2 = 'Маритиму Мадейра'
    if t2 == 'Санта-Клара':
        t2 = 'Санта Клара'
    if (t1 in teamLinks.keys()) and (t2 in teamLinks.keys()):
        diff = (table_dict['avg_g_scored'][t1] - table_dict['avg_g_against'][t1]) - (
                table_dict['avg_g_scored'][t2] - table_dict['avg_g_against'][t2])
        diff = side_eff + round(diff, 2)
        return diff
    else:
        print("Error with match ", t1, " - ", t2, ": unknown club")
        return 0


# функция для стайлинга - раскраски таблицы
def highlight_cells(value):
    par = []
    for i, op in enumerate(value):
        side_match = op[-3:]
        # первые 10 символов - дата в формете dd.mm.yyyy, последние 3 - сторона в формате (д)/(г)
        op = op[10:-3].strip()
        diff = difficulty_avg(value.index[i], op, side_match)
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


# фиксирование времени начала обработки
startTime = time.time()

for currentChamp in targetChamps:
    startChampTime = time.time()
    print('Обработка чемпионата "' + currentChamp + '"...')
    currentChampLink = champLinks[currentChamp]['sportsLink']
    currentTableLink = currentChampLink + 'table/'
    # получаем страницу с таблицей обрабатываемого чемпионата
    _, tableSportsSoup = request_text_soup(currentTableLink)
    # выделение таблицы со страницы
    tableBody = tableSportsSoup.tbody
    teamBodyList = tableBody.find_all('tr')
    # колонки футбольных таблиц на sports.ru - численные атрибуты каждой команды
    tableColumns = ["games", "won", "draw", "lost", "g_scored", "g_against", "points"]
    table_dict = {}
    teamLinks = {}
    # для каждой команды из таблицы сохраним ссылку на профиль команды, все численные атрибуты
    for team in teamBodyList:
        teamName = team.find('a', class_='name').get('title')
        teamLinks[teamName] = team.find('a', class_='name').get('href')
        teamNumbers = team.find_all('td', class_=None)
        for j, n in enumerate(teamNumbers):
            teamNumbers[j] = int(n.text)
        table_dict[teamName] = dict(zip(tableColumns, teamNumbers))
        table_dict[teamName]['avg_g_scored'] = table_dict[teamName]["g_scored"] / table_dict[teamName]["games"]
        table_dict[teamName]['avg_g_against'] = table_dict[teamName]["g_against"] / table_dict[teamName]["games"]
    # транспонируем этот словарь, чтобы иметь доступ в другом порядке
    # (вместо team_name -> games -> 5 получаем games -> team_name -> 5)
    table_dict = dict(pd.DataFrame(table_dict).transpose())

    # обработка календаря для каждой команды
    champCalendarDict = {}
    for team, teamLink in teamLinks.items():
        teamLink = teamLink + 'calendar'
        teamName = team
        # запрос страницы с календарем для каждой команды
        ''' (в теории можно обрабатывать через календарь соревнования)
        (НО - на спортс в таком случае не обязательна сортировка по дате 
        - используется сортировка по ФОРМАЛЬНОМУ туру)'''
        _,  calendarTeamSportsSoup = request_text_soup(teamLink)
        # выцепление самой таблицы с календарем матчей
        calendarTeamSportsBody = calendarTeamSportsSoup.find('tbody')
        # получение списка матчей
        matchTeamList = calendarTeamSportsBody.find_all('tr')

        date = []
        competition = []
        opponent = []
        side = []
        result = []
        for match in matchTeamList:
            # убираем из рассмотрения матчи с пометкой "перенесен" вместо даты
            if 'перенесен' not in str(match):
                date.append(match.find('a').text.split('|')[0].strip())
                competition.append(match.div.a.get('href'))
                opponent.append(match.find_all('div')[1].text.strip())
                side.append(side_map(match.find('td', class_="alRight padR20").text))
                result.append(match.find('a', class_='score').text.strip())

        # формирование календаря в формате лист в листе
        teamCalendar = [[date[i] + ' ' + opponent[i] + side[i],
                         competition[i]] for i in range(0, len(opponent))]
        # взятие только релевантного календаря - под релевантностью понимаем наличие ссылки на превью вместо счета
        # так мы определяем будущие игры
        relevantTeamCalendar = teamCalendar[result.index('превью'):]
        # берем из списка будущих игр только те, которые будут проходить в интересующем нас чемпионате
        # для проверки используем ссылку на чемпионат из нашего маппинга, сравнивая ее со ссылкой на
        # чемпионат, который соответствует обрабатываемой игре
        relevantTeamCalendarTarget = list(filter(lambda x: currentChampLink in x[1], relevantTeamCalendar))
        # взятие ближайших 5 игр для каждой команды
        champCalendarDict[teamName] = dict(zip(['1', '2', '3', '4', '5'],
                                               [relevantTeamCalendarTarget[x][0] for x in range(5)]))
    # транспонирование таблицы
    champCalendar = pd.DataFrame(champCalendarDict).transpose()
    # оформление и сохранение
    champCalendarStyle = champCalendar.style.apply(highlight_cells)
    html = champCalendarStyle.render()
    path_wkthmltoimage = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
    config = imgkit.config(wkhtmltoimage=path_wkthmltoimage)
    options = {'encoding': "UTF-8"}
    # создание директории при отсутствии оной
    directory = ("pics/" + str(datetime.datetime.now().date()) + "/calendars/")
    if not os.path.isdir(directory):
        os.makedirs(directory)
    imgkit.from_string(html, directory + currentChamp + ".png", config=config, options=options)

    # логгирование времени обработки каждого чемпионата
    print('"' + currentChamp + '" обработан, время обработки: ' + str(round(time.time() - startChampTime, 3)) + "s")

# логгирование времени всех запрошенных чемпионатов
print('Календари собраны, время обработки: ' + str(round(time.time() - startTime, 3)) + "s")
