"""
Единая точка входа - отсюда для каждого чемпионата вызываются marathon_processing и calendar_processing функции
"""
import marathon
import calendarSports
from common import get_champ_stats_caption, save_pic, save_stats_excel, request_text_soup, rus_date_convert
from configFootballLinks import CHAMP_LINKS
from config import OUTPUT_EXCEL_PATH, MARATHON_DIR, CALENDAR_DIR
import time
from datetime import date
import logging
import fantasyBot
import pandas as pd
from xbet import find_xbet_links
import re

logging.basicConfig(filename='log/{}.log'.format(date.today()), level=logging.INFO,
                    format=u'[%(asctime)s]  %(filename)-20s[LINE:%(lineno)d] #%(levelname)-8s  %(message)s')

daysBeforeDeadlineLimit = 4


# функция для обработки страницы чьей-либо фентези команды на спортс.ру - на вход подается ссылка на команду
# на выходе получаем представление даты дедлайна в двух видах: текстовом и datetime + количество матчей в туре
def update_champ_meta(current_champ):
    link = CHAMP_LINKS[current_champ]['sportsFantasy']
    if link:
        # запрос страницы фентези команды на спортс ру
        sports_fantasy_text, sports_fantasy_soup = request_text_soup(link)
        # вычисление даты дедлайна - пока что время дедлайна не используется
        # на спортс дата дедлайна в виде "15 Апр 18:00"
        deadline = re.findall(r'Дедлайн</th>\n<td>([^<]*)[^\d]*(\d{2}:\d{2})', sports_fantasy_text)[0]
        deadline_text = ' '.join(deadline)
        # конвертируем в datetime часть даты вида "15 Апр"
        deadline_date = rus_date_convert(deadline[0])
        match_week = re.findall(r'<td>тур ([\d]*)', sports_fantasy_text)[0]
        match_week = int(match_week)
        # вычисление количества матчей в туре с помощью страницы фентези команды на спортс ру
        match_table = sports_fantasy_soup.find('table', class_='stat-table with-places')
        # в некоторых случаях данной таблицы вообще не будет на странице, например, когда дата следующего тура неясна
        match_num = len(match_table.find_all('tr')) - 1 if match_table else 0
        if deadline_date < date.today():
            logging.info('{}: Нет даты дедлайна, чемпионат пропускается...'.format(current_champ))
        elif -1 < (deadline_date - date.today()).days > daysBeforeDeadlineLimit:
            logging.info('{}: До дедлайна больше {} дней, чемпионат пропускается...'.format(current_champ,
                                                                                            daysBeforeDeadlineLimit))
        elif match_num == 0:
            logging.warning(
                '{}: На спортс.ру не указаны матчи на ближайший тур, несмотря на то, что дедлайн близко'.format(
                    current_champ))
        else:
            CHAMP_LINKS[current_champ]['matchweek'] = match_week
            CHAMP_LINKS[current_champ]['deadline_text'] = deadline_text
            CHAMP_LINKS[current_champ]['deadline_date'] = deadline_date
            CHAMP_LINKS[current_champ]['match_num'] = match_num
            logging.info('{}: метаданные обработаны'.format(current_champ))
    return


# функция для извлечения из словаря CHAMP_LINKS сразу нескольких ключей
def get_meta(*args):
    return [CHAMP_LINKS[currentChamp].get(x) for x in args]


if __name__ == '__main__':
    # иницализация excelWriter, mode='w' для полной перезаписи файла
    writer = pd.ExcelWriter(OUTPUT_EXCEL_PATH, engine='openpyxl', mode='w')
    # логирование информации о времени обработки
    startTime = time.time()
    logging.info('*' * 37 + 'Начало обработки' + '*' * 37)
    for currentChamp in CHAMP_LINKS.keys():
        # функция, которая обновила данные в словаре: matchweek, deadline_text, deadline_date, match_num
        update_champ_meta(currentChamp)
    logging.info('-' * 90)
    # функция, добавляющая в словарь CHAMP_LINKS ссылки на линию 1 x bet на чемпиона для всех релевантных чемпионатов
    # по ключу 1x_winner
    find_xbet_links()
    logging.info('-' * 90)
    for currentChamp, currentChampLinks in CHAMP_LINKS.items():
        # фиксирование времени по каждому чемпионату
        champStartTime = time.time()
        deadlineDate, deadlineText, matchweek, matchNum = get_meta(
            'deadline_date', 'deadline_text', 'matchweek', 'match_num')
        if matchNum is None:
            continue
        # логирование обработки каждого чемпионата
        logging.info('{}: старт обработки чемпионата...'.format(currentChamp))
        # обработка и сохранение картинкой информации с Марафона
        styledMarathon = marathon.marathon_processing(currentChamp, currentChampLinks, deadlineDate, matchNum)
        pathMarathon = save_pic(styledMarathon, MARATHON_DIR, currentChamp, 'marathon')
        # обработка и сохранение картинкой календаря со спортс.ру
        styledCalendar = calendarSports.calendar_processing(currentChamp, currentChampLinks, matchweek)
        pathCalendar = save_pic(styledCalendar, CALENDAR_DIR, currentChamp, 'calendar')
        # добавление подписи и выгрузка в телеграм-канал
        postCaption = get_champ_stats_caption(currentChamp, deadlineText, deadlineDate)
        fantasyBot.posting_to_channel(postCaption, pathMarathon, pathCalendar)
        save_stats_excel(writer, currentChamp, styledMarathon, styledCalendar)

        # логирование информации о скорости обработки каждого турнира
        logging.info('{}: чемпионат обработан, время обработки: {}s'.format(currentChamp,
                                                                             round(time.time() - champStartTime, 3)))
        logging.info('-' * 90)

    if len(writer.sheets):
        writer.save()

    # логирование информации о полном времени
    logging.info('Тур обработан, время обработки: {}s'.format(round(time.time() - startTime, 3)))
    logging.info('_' * 90)
