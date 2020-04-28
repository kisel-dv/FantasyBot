"""
Единая точка входа - отсюда для каждого чемпионата вызываются marathon_processing и calendar_processing функции
"""
import marathon
import calendarSports
from common import rus_date_convert, request_text_soup, get_champ_stats_caption
from configFootballLinks import CHAMP_LINKS
import time
import re
from datetime import date
import logging
import fantasyBot

logging.basicConfig(filename='log/{}.log'.format(date.today()), level=logging.INFO,
                    format=u'[%(asctime)s]  %(filename)-20s[LINE:%(lineno)d] #%(levelname)-8s  %(message)s')

daysBeforeDeadlineLimit = 5

# логирование информации о времени обработки
startTime = time.time()
logging.info('*' * 37 + 'Начало обработки' + '*' * 37)

for currentChamp, currentChampLinks in CHAMP_LINKS.items():
    # фиксирование времени по каждому чемпионату
    champStartTime = time.time()
    # логирование обработки каждого чемпионата
    logging.info('Обработка чемпионата "{}"...'.format(currentChamp))

    # запрос страницы фентези команды на спортс ру
    sportsFantasyText, sportsFantasySoup = request_text_soup(currentChampLinks['sportsFantasy'])
    # вычисление даты дедлайна - пока что время дедлайна не используется
    deadline = re.findall(r'Дедлайн</th>\n<td>([^<]*)[^\d]*(\d{2}:\d{2})', sportsFantasyText)[0]
    deadlineText = ' '.join(deadline)
    deadlineDate = rus_date_convert(deadline[0])
    # дебаг фича
    # if currentChamp == 'Беларусь':
    #    deadlineDate = date.today()
    # если дедлайн в прошлом или более чем через 5 дней, мы пропускаем обработку чемпионата
    if -1 < (deadlineDate - date.today()).days > daysBeforeDeadlineLimit:
        logging.info('До дедлайна больше 5 дней, чемпионат пропускается...')
    else:
        # вычисление количества матчей в туре с помощью страницы фентези команды на спортс ру
        matchTable = sportsFantasySoup.find('table', class_='stat-table with-places')
        # в некоторых случаях данной таблицы вообще не будет на странице, например, когда дата следующего тура неясна
        matchNum = len(matchTable.find_all('tr')) - 1 if matchTable else 0
        if matchNum > 0:
            pathMarathon = marathon.marathon_processing(currentChamp, currentChampLinks, deadlineDate, matchNum)
            pathCalendar = calendarSports.calendar_processing(currentChamp, currentChampLinks)
            postCaption = get_champ_stats_caption(currentChamp, deadlineText, deadlineDate)
            fantasyBot.posting_to_channel(postCaption, pathMarathon, pathCalendar)

    # логирование информации о скорости обработки каждого турнира
    logging.info(
        'Чемпионат "{}" обработан, время обработки: {}s'.format(currentChamp, round(time.time() - champStartTime, 3)))
    logging.info('-' * 90)

# логирование информации о полном времени
logging.info('Тур обработан, время обработки: {}s'.format(round(time.time() - startTime, 3)))
logging.info('_' * 90)
