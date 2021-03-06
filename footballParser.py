"""
Единая точка входа - отсюда для каждого чемпионата вызываются marathon_processing и calendar_processing функции
"""
import pandas as pd
import time
import logging
from datetime import date
from typing import List, Union

import calendarSports
import common
import tgbot
import marathon
from configFootballLinks import CHAMP_LINKS
from config import MARATHON_DIR, CALENDAR_DIR, TG_CHANNELS, EXCEL_PATHS


# на сколько дней нужно смотреть вперед в поиске дедлайнов
DAYS_BEFORE_DEADLINE = 3


# функция для обработки страницы чьей-либо фентези команды на спортс.ру - на вход подается ссылка на команду
# на выходе получаем представление даты дедлайна в двух видах: текстовом и datetime + количество матчей в туре
def pull_champ_meta(current_champ: str) -> Union[list, None]:
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
    if match_table:
        match_num = len(match_table.find_all('tr')) - 1
        max_date = match_table.find_all('tr')[-1].td.text
        day, month = map(int, max_date.split('|')[0].split('.'))
        year = date.today().year
        max_date = date(year, month, day)
    else:
        match_num = 0
        max_date = None

    if deadline_date < date.today():
        logging.info('{}: Нет даты дедлайна, чемпионат пропускается...'.format(current_champ))
        return
    elif (deadline_date - date.today()).days > DAYS_BEFORE_DEADLINE:
        logging.info('{}: До дедлайна({}) больше {} дней, чемпионат пропускается...'.format(current_champ,
                                                                                            deadline_date,
                                                                                            DAYS_BEFORE_DEADLINE))
        return
    elif match_num == 0:
        logging.warning('{}: На спортс.ру не указаны матчи на ближайший тур'.format(current_champ))
        return
    logging.info('{}: Метаданные обработаны'.format(current_champ))
    return [deadline_date, max_date, deadline_text, match_week, match_num]


# 'prod' / 'test'
def run_stats_update(mode: str = 'prod', champs: List[str] = None) -> None:
    # иницализация excelWriter, mode='w' для полной перезаписи файла
    excel_path = EXCEL_PATHS.get(mode)
    channel_id = TG_CHANNELS.get(mode)
    writer = pd.ExcelWriter(excel_path, engine='openpyxl', mode='w')
    # логирование информации о времени обработки
    start_time = time.time()
    logging.info('*' * 90)
    logging.info('*' * 37 + 'Начало обработки' + '*' * 37)
    target_champs = CHAMP_LINKS.keys() if champs is None else [x for x in champs if x in CHAMP_LINKS]
    for current_champ in target_champs:
        # фиксирование времени по каждому чемпионату
        champ_start_time = time.time()
        logging.info('-' * 90)
        logging.info('{}: старт обработки чемпионата...'.format(current_champ))
        # обработка метаданных со спортс.ру
        current_champ_links = CHAMP_LINKS[current_champ]
        meta = pull_champ_meta(current_champ)
        if meta is None:
            continue
        deadline_date, max_date, deadline_text, matchweek, match_num_meta = meta
        # обработка и сохранение картинкой календаря со спортс.ру, определение количества матчей в ближайшем туре
        styled_calendar, match_num, postponed_matches = calendarSports.calendar_processing(current_champ, current_champ_links, matchweek) or (None, match_num_meta, None)
        path_calendar = common.save_pic(styled_calendar, CALENDAR_DIR, current_champ, 'calendar')
        # обработка и сохранение картинкой информации с Марафона
        styled_marathon = marathon.marathon_processing(current_champ, current_champ_links, deadline_date, max_date, match_num)
        path_marathon = common.save_pic(styled_marathon, MARATHON_DIR, current_champ, 'marathon')
        # добавление подписи и выгрузка в телеграм-канал
        post_caption = common.get_champ_stats_caption(current_champ, deadline_text, deadline_date, postponed_matches)
        tgbot.posting_to_channel(channel_id, post_caption, path_marathon, path_calendar)
        # апдейт страницы в таблице
        common.save_stats_to_excel(writer, current_champ, styled_marathon, styled_calendar)

        # логирование информации о скорости обработки каждого турнира
        logging.info('{}: чемпионат обработан, время обработки: {}s'.format(current_champ,
                                                                            round(time.time() - champ_start_time, 3)))
    # если хотя бы одна страница была создана(хотя бы один чемпионат обработан), то перезаписываем таблицу на диске
    logging.info('-' * 90)
    if len(writer.sheets):
        writer.save()
    # логирование информации о полном времени
    logging.info('Тур обработан, время обработки: {}s'.format(round(time.time() - start_time, 3)))
    logging.info('_' * 90)


if __name__ == '__main__':
    logging.basicConfig(filename='log/{}.log'.format(date.today()),
                        level=logging.INFO,
                        format=u'[%(asctime)s]  %(filename)-20s[LINE:%(lineno)d] #%(levelname)-8s  %(message)s')
    #run_stats_update('test', champs=['Испания'])
    run_stats_update('prod')
