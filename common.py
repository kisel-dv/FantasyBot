"""
Модуль, в котором находятся некоторые общие функции, используемые в нескольких файлах
"""
import urllib.request
import imgkit
import logging
import os
import json
import pandas as pd
from bs4 import BeautifulSoup
from datetime import date
from typing import Tuple, Dict, Union

from configFootballLinks import CHAMP_LINKS
from config import WKHTMLTOIMAGE_PATH


IMGKIT_CONFIG = imgkit.config(wkhtmltoimage=WKHTMLTOIMAGE_PATH)

# дикта, используемая для конвертации даты
MONTHS = {'дек': 12, 'янв': 1, 'фев': 2,
          'мар': 3, 'апр': 4, 'мая': 5,
          'июн': 6, 'июл': 7, 'авг': 8,
          'сен': 9, 'окт': 10, 'ноя': 11
          }

# маппинг дня недели в сокращенное кириллическое представление
WEEKDAY_CYRILLIC = {0: 'ПН', 1: 'ВТ', 2: 'СР', 3: 'ЧТ', 4: 'ПТ', 5: 'СБ', 6: 'ВС'}
REQUEST_HEADERS = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}


# функция для конвертации даты из кириллицы в date формат,
# ожидается, что на вход мы получаем дату в формате day month[ time]
def rus_date_convert(d: str) -> date:
    # проверка - либо на вход дано пустое значение, либо на вход дано время без даты - в таком случае выдаем "сегодня"
    if d == '' or d[2] == ':':
        return date.today()
    # отсекаем время
    day, month = d.split()[:2]
    day = int(day)
    # проверка начальных символов месяца в соответствии с ключами дикты
    month = MONTHS[month[:3]]
    year = date.today().year
    try:
        res = date(year, month, day)
        return res
    except ValueError:
        logging.error('Некорректный формат даты: {}'.format(d))
        return date.today()


# генерирует надпись для первой картинки из выкладываемых для каждого чемпионата
def get_champ_stats_caption(champ: str, deadline: str, deadline_date: date) -> str:
    weekday = WEEKDAY_CYRILLIC[deadline_date.weekday()]
    emoji = CHAMP_LINKS[champ]['emoji']
    caption = '{}{}\nДедлайн: {} ({})'.format(emoji, champ, deadline, weekday)
    return caption


# функция для обработки каждой страницы, возвращает пару (текст страницы, soup объект)
def request_text_soup(link: str, **kwargs) -> Tuple[str, BeautifulSoup]:
    req = urllib.request.urlopen(urllib.request.Request(link, headers=REQUEST_HEADERS))
    if link != req.geturl():
        logging.error('При обработке ссылки произошла переадресация на другой адрес')
        text = ''
    else:
        text = req.read().decode('utf-8')
        if 'func' in kwargs:
            text = kwargs['func'](text)
    return text, BeautifulSoup(text, 'html.parser')


# функция для сохранения картинок
def save_pic(s, directory: str, pic_name: str, flag: str) -> Union[str, None]:
    if s is None:
        return None
    options = {'encoding': "UTF-8"}
    if flag == 'marathon':
        # дополнительные настройки для сохранения картинкой - размеры в пикселях
        options.update({'width': str(450 + int(s.ctx[(0, 3)][0][:-2].split()[-1])),
                        'height': str(24 * s.data.shape[0] + 36)})
    html = s.render()
    if not os.path.isdir(directory):
        os.makedirs(directory)
    path = directory + pic_name + ".png"
    imgkit.from_string(html, path, config=IMGKIT_CONFIG, options=options)
    logging.info('{}: картинка сохранена'.format(pic_name))
    return path


# функция для сохранения стилизированных данных в формате таблиц
def save_stats_to_excel(writer: pd.ExcelWriter, champ: str, marathon, calendar) -> None:
    workbook = writer.book
    writer.sheets[champ] = workbook.create_sheet(champ)
    # настройка ширины столбцов (первых 6, потому что используются только они)
    for col in 'ABCDEF':
        writer.sheets[champ].column_dimensions[col].width = 30
    # записываем матожидания
    if marathon is not None:
        marathon.to_excel(writer, sheet_name=champ, startrow=0, startcol=0, index=False)
    # с отступом в 5 строк записываем календарь
    if calendar is not None:
        calendar.to_excel(writer, sheet_name=champ, startrow=calendar.data.shape[0] + 5, startcol=0)
    logging.info('{}: информация в excel обновлена'.format(champ))
    return


def save_json(j: dict, path: str) -> None:
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(j, f)


def save_dfs_to_xlsx(dfs: Dict[str, pd.DataFrame], file_path: str) -> None:
    writer = pd.ExcelWriter(file_path, engine='xlsxwriter')
    for sheet_name, df in dfs.items():  # loop through `dict` of dataframes
        df.to_excel(writer, sheet_name=sheet_name, index=False)  # send df to writer
        worksheet = writer.sheets[sheet_name]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width
    writer.save()

