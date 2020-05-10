"""
Единая точка входа - отсюда для каждого чемпионата вызываются marathon_processing и calendar_processing функции
"""
import marathon
import calendarSports
from common import get_champ_stats_caption, save_pic, get_champ_meta, save_stats_excel
from configFootballLinks import CHAMP_LINKS
from config import OUTPUT_EXCEL_PATH, MARATHON_DIR, CALENDAR_DIR
import time
from datetime import date
import logging
import fantasyBot
import pandas as pd

logging.basicConfig(filename='log/{}.log'.format(date.today()), level=logging.INFO,
                    format=u'[%(asctime)s]  %(filename)-20s[LINE:%(lineno)d] #%(levelname)-8s  %(message)s')

daysBeforeDeadlineLimit = 3

if __name__ == '__main__':
    # иницализация excelWriter, mode='w' для полной перезаписи файла
    writer = pd.ExcelWriter(OUTPUT_EXCEL_PATH, engine='openpyxl', mode='w')

    # логирование информации о времени обработки
    startTime = time.time()
    logging.info('*' * 37 + 'Начало обработки' + '*' * 37)

    for currentChamp, currentChampLinks in CHAMP_LINKS.items():
        # фиксирование времени по каждому чемпионату
        champStartTime = time.time()
        # логирование обработки каждого чемпионата
        logging.info('Обработка чемпионата "{}"...'.format(currentChamp))
        deadlineText, deadlineDate, matchNum = get_champ_meta(currentChampLinks['sportsFantasy'])
        # дебаг фича
        # if currentChamp == 'Беларусь':
        #    deadlineDate = date.today()
        # если дедлайн в прошлом или более чем через 5 дней, мы пропускаем обработку чемпионата
        if deadlineDate < date.today():
            logging.info('Нет даты дедлайна, чемпионат пропускается...')
        elif -1 < (deadlineDate - date.today()).days > daysBeforeDeadlineLimit:
            logging.info('До дедлайна больше 5 дней, чемпионат пропускается...')
        elif matchNum > 0:
            # обработка и сохранение картинкой информации с Марафона
            styledMarathon = marathon.marathon_processing(currentChamp, currentChampLinks, deadlineDate, matchNum)
            pathMarathon = save_pic(styledMarathon, MARATHON_DIR, currentChamp, 'marathon')
            # обработка и сохранение картинкой календаря со спортс.ру
            styledCalendar = calendarSports.calendar_processing(currentChamp, currentChampLinks)
            pathCalendar = save_pic(styledCalendar, CALENDAR_DIR, currentChamp, 'calendar')
            # добавление подписи и выгрузка в телеграм-канал
            postCaption = get_champ_stats_caption(currentChamp, deadlineText, deadlineDate)
            fantasyBot.posting_to_channel(postCaption, pathMarathon, pathCalendar)
            save_stats_excel(writer, currentChamp, styledMarathon, styledCalendar)

        # логирование информации о скорости обработки каждого турнира
        logging.info('Чемпионат "{}" обработан, время обработки: {}s'.format(currentChamp,
                                                                             round(time.time() - champStartTime, 3)))
        logging.info('-' * 90)

    if len(writer.sheets):
        writer.save()

    # логирование информации о полном времени
    logging.info('Тур обработан, время обработки: {}s'.format(round(time.time() - startTime, 3)))
    logging.info('_' * 90)
