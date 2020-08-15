"""
Модуль, в котором находятся некоторые общие функции, используемые в нескольких файлах
"""
import urllib.request
from bs4 import BeautifulSoup
from datetime import date, datetime
import imgkit
import logging
import os
import json
import pandas as pd

from configFootballLinks import CHAMP_LINKS

pathWkHtmlToImage = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
imgkitConfig = imgkit.config(wkhtmltoimage=pathWkHtmlToImage)

# дикта, используемая для конвертации даты
MONTHS = {'дек': 12, 'янв': 1, 'фев': 2,
          'мар': 3, 'апр': 4, 'мая': 5,
          'июн': 6, 'июл': 7, 'авг': 8,
          'сен': 9, 'окт': 10, 'ноя': 11
          }


# функция для конвертации даты из кириллицы в date формат
def rus_date_convert(d, t=''):
    # проверка - либо на вход дано пустое значение, либо на вход дано время без даты - в таком случае выдаем "сегодня"
    if d == '' or d[2] == ':':
        return date.today()
    # ожидается, что на вход мы получаем дату в формате day month[ time], отсекаем время
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


# маппинг дня недели в сокращенное кириллическое представление
WEEKDAY_CYRILLIC = {0: 'ПН', 1: 'ВТ', 2: 'СР', 3: 'ЧТ', 4: 'ПТ', 5: 'СБ', 6: 'ВС'}


# генерирует надпись для первой картинки из выкладываемых для каждого чемпионата
def get_champ_stats_caption(champ, deadline, deadline_date):
    weekday = WEEKDAY_CYRILLIC[datetime.weekday(deadline_date)]
    emoji = CHAMP_LINKS[champ]['emoji']
    caption = '{}{}\nДедлайн: {} ({})'.format(emoji, champ, deadline, weekday)
    return caption


# функция для обработки каждой страницы, возвращает пару (текст страницы, soup объект)
def request_text_soup(link):
    headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36"}
    req = urllib.request.urlopen(urllib.request.Request(link, headers=headers))
    if link == req.geturl():
        text = req.read().decode('utf-8')
    else:
        logging.error('При обработке ссылки произошла переадресация на другой адрес')
        text = ''
    return text, BeautifulSoup(text, 'html.parser')


# функция для сохранения картинок
def save_pic(s, directory, name, flag):
    if s is None:
        return None
    options = {'encoding': "UTF-8"}
    if flag == 'marathon':
        # дополнительные настройки для сохранения картинкой
        options.update({'width': str(450 + int(s.ctx[(0, 3)][0][:-2].split()[-1])),
                        'height': str(24 * s.data.shape[0] + 36)})
    html = s.render()
    if not os.path.isdir(directory):
        os.makedirs(directory)
    path = directory + name + ".png"
    imgkit.from_string(html, path, config=imgkitConfig, options=options)
    logging.info('{}: картинка сохранена'.format(name))
    return path


# функция для сохранения стилизированных данных в формате таблиц
def save_stats_excel(writer, champ, marathon, calendar):
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


def save_json(j, path):
    with open(path, 'w', encoding='UTF-8') as f:
        json.dump(j, f)


def save_xlsx(dfs, filepath):
    writer = pd.ExcelWriter(filepath, engine='xlsxwriter')
    for sheetname, df in dfs.items():  # loop through `dict` of dataframes
        df.to_excel(writer, sheet_name=sheetname, index=False)  # send df to writer
        worksheet = writer.sheets[sheetname]  # pull worksheet object
        for idx, col in enumerate(df):  # loop through all columns
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),  # len of largest item
                len(str(series.name))  # len of column name/header
            )) + 1  # adding a little extra space
            worksheet.set_column(idx, idx, max_len)  # set column width
    writer.save()

