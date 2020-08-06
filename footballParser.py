"""
Единая точка входа - отсюда для каждого чемпионата вызываются marathon_processing и calendar_processing функции
"""
import time
from datetime import date
import logging
import pandas as pd

import marathon
import calendarSports
import common
from configFootballLinks import CHAMP_LINKS
from config import MARATHON_DIR, CALENDAR_DIR, CHANNELS, EXCEL_PATHS
import fantasyBot


logging.basicConfig(filename='log/{}.log'.format(date.today()), level=logging.INFO,
                    format=u'[%(asctime)s]  %(filename)-20s[LINE:%(lineno)d] #%(levelname)-8s  %(message)s')

daysBeforeDeadlineLimit = 2


# функция для обработки страницы чьей-либо фентези команды на спортс.ру - на вход подается ссылка на команду
# на выходе получаем представление даты дедлайна в двух видах: текстовом и datetime + количество матчей в туре
def pull_champ_meta(current_champ):
    link = CHAMP_LINKS[current_champ]['sportsFantasy']
    if not link:
        logging.warning('{}: Отсутствует ссылка на метаданные')
        return
    # запрос страницы фентези команды на спортс ру
    _, sports_fantasy_soup = common.request_text_soup(link)
    # взятие элемента с дедлайном и номером тура
    target_elem = sports_fantasy_soup.find('div', class_='team-info-block')
    if target_elem is None:
        logging.error('{}: Ошибка в формате страницы на спортс.ру'.format(current_champ))
        return

    td = target_elem.find_all('td')
    if len(td) < 2:
        logging.error('{}: Ошибка в формате страницы на спортс.ру'.format(current_champ))
        return

    match_week = td[0].text.split()[1].strip('.')
    if not match_week.isdigit():
        logging.info('{}: Текущий сезон чемпионата завершен, чемпионат пропускается...'.format(current_champ))
        return

    match_week = int(match_week)
    # на спортс дата дедлайна в виде "15 Апр 18:00" - пока что время дедлайна не используется
    deadline_text = td[1].text
    # конвертируем в datetime часть даты вида "15 Апр"
    deadline_date = common.rus_date_convert(deadline_text.split('|')[0])

    # найдет все элементы с CSS тэгом "stat-table", последний - таблица с играми ближайшего тура
    match_table = sports_fantasy_soup.find_all('table', class_='stat-table')[-1]
    # вычисление количества матчей в туре с помощью страницы фентези команды на спортс ру
    # в некоторых случаях данной таблицы вообще не будет на странице, например, когда дата следующего тура неясна
    match_num = len(match_table.find_all('tr')) - 1 if match_table else 0

    if deadline_date < date.today():
        logging.info('{}: Нет даты дедлайна, чемпионат пропускается...'.format(current_champ))
        return
    elif -1 < (deadline_date - date.today()).days > daysBeforeDeadlineLimit:
        logging.info('{}: До дедлайна больше {} дней, чемпионат пропускается...'.format(current_champ,
                                                                                        daysBeforeDeadlineLimit))
        return
    elif match_num == 0:
        logging.warning(
            '{}: На спортс.ру не указаны матчи на ближайший тур, несмотря на то, что дедлайн близко, чемпионат пропускается...'.format(
                current_champ))
        return
    return [deadline_date, deadline_text, match_week, match_num]


# функция для извлечения из словаря CHAMP_LINKS сразу нескольких ключей
# def get_meta(current_champ, *args):
#    return [CHAMP_LINKS[current_champ].get(x) for x in args]


# 'prod' / 'test'
def run_stats_update(mode='prod'):
    # иницализация excelWriter, mode='w' для полной перезаписи файла
    excel_path = EXCEL_PATHS.get(mode)
    channel_id = CHANNELS.get(mode)
    writer = pd.ExcelWriter(excel_path, engine='openpyxl', mode='w')
    # логирование информации о времени обработки
    start_time = time.time()
    logging.info('*' * 90)
    logging.info('*' * 37 + 'Начало обработки' + '*' * 37)
    fantasyBot.posting_info_message(channel_id, 'Обновление коэффициентов...')
    for current_champ, current_champ_links in CHAMP_LINKS.items():
        # фиксирование времени по каждому чемпионату
        champ_start_time = time.time()
        logging.info('-' * 90)
        logging.info('{}: старт обработки чемпионата...'.format(current_champ))
        # обработка метаданных со спортс.ру
        meta = pull_champ_meta(current_champ)
        if meta is None:
            continue
        deadline_date, deadline_text, matchweek, match_num = meta
        # обработка и сохранение картинкой информации с Марафона
        styled_marathon = marathon.marathon_processing(current_champ, current_champ_links, deadline_date, match_num)
        path_marathon = common.save_pic(styled_marathon, MARATHON_DIR, current_champ, 'marathon')
        # обработка и сохранение картинкой календаря со спортс.ру
        styled_calendar = calendarSports.calendar_processing(current_champ, current_champ_links, matchweek)
        path_calendar = common.save_pic(styled_calendar, CALENDAR_DIR, current_champ, 'calendar')
        # добавление подписи и выгрузка в телеграм-канал
        post_caption = common.get_champ_stats_caption(current_champ, deadline_text, deadline_date)
        fantasyBot.posting_to_channel(channel_id, post_caption, path_marathon, path_calendar)
        # апдейт страницы в таблице
        common.save_stats_excel(writer, current_champ, styled_marathon, styled_calendar)

        # логирование информации о скорости обработки каждого турнира
        logging.info('{}: чемпионат обработан, время обработки: {}s'.format(current_champ,
                                                                            round(time.time() - champ_start_time, 3)))
    # если хотя бы одна страница была создана(хотя бы один чемпионат обработан), то перезаписываем таблицу на диске
    logging.info('-' * 90)
    if len(writer.sheets):
        writer.save()
    fantasyBot.posting_info_message(channel_id, 'Обновление завершено')
    # логирование информации о полном времени
    logging.info('Тур обработан, время обработки: {}s'.format(round(time.time() - start_time, 3)))
    logging.info('_' * 90)


if __name__ == '__main__':
    run_stats_update('prod')
