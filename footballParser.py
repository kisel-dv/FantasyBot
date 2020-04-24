"""
Единая точка входа - отсюда для каждого чемпионата вызываются marathonProcessing и calendarProcessing функции
"""
import marathon
import calendarSports
from common import rusdate_convert, request_text_soup, champLinks
import time
import re
from datetime import date

daysBeforeDeadlineLimit = 5

# логирование информации о времени обработки
startTime = time.time()

for currentChamp, currentChampLinks in champLinks.items():
    # фиксирование времени по каждому чемпионату
    champStartTime = time.time()
    # логирование обработки каждого чемпионата
    print('Обработка чемпионата "' + currentChamp + '"...')
    # запрос страницы фентези команды на спортс ру
    sportsFantasyText, sportsFantasySoup = request_text_soup(currentChampLinks['sportsFantasy'])
    # вычисление даты дедлайна - пока что время дедлайна не используется
    deadline = re.findall(r'Дедлайн</th>\n<td>([^<]*)[^\d]*(\d{2}:\d{2})', sportsFantasyText)[0]
    deadlineDate = rusdate_convert(deadline[0])
    if currentChamp == 'Беларусь':
        deadlineDate = date.today()
    # если дедлайн в прошлом или более чем через 5 дней, мы пропускаем обработку чемпионата
    if -1 < (deadlineDate - date.today()).days > daysBeforeDeadlineLimit:
        print('До дедлайна больше 5 дней, чемпионат пропускается...')
    else:
        # вычисление количества матчей в туре с помощью страницы фентези команды на спортс ру
        matchTable = sportsFantasySoup.find('table', class_="stat-table with-places")
        # в некоторых случаях данной таблицы вообще не будет на странице, например, когда дата следующего тура неясна
        matchNum = len(matchTable.find_all('tr')) - 1 if matchTable else 0
        if matchNum > 0:
            marathon.marathon_processing(currentChamp, currentChampLinks, deadlineDate, matchNum)
            calendarSports.calendar_processing(currentChamp, currentChampLinks)

    # логирование информации о скорости обработки каждого турнира
    print('Чемпионат "' + currentChamp + '" обработан, время обработки: ' +
          str(round(time.time() - champStartTime, 3)) + "s")
    print('_' * 90)

# логирование информации о полном времени
print('Тур обработан, время обработки: ' + str(round(time.time() - startTime, 3)) + "s")
