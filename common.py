"""
Модуль, в котором находятся некоторые общие функции, используемые в нескольких файлах
"""
import urllib.request
from bs4 import BeautifulSoup
from datetime import date
import imgkit
import logging
import os

# дикта, используемая для конвертации даты
months = {'дек': 12, 'янв': 1, 'фев': 2,
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
    month = months[month[:3]]
    year = date.today().year
    try:
        res = date(year, month, day)
        return res
    except ValueError:
        logging.error('Некорректный формат даты: {}'.format(d))
        return date.today()


# функция для обработки каждой страницы, возвращает пару (текст страницы, soup объект)
def request_text_soup(link):
    req = urllib.request.Request(link)
    text = urllib.request.urlopen(req).read().decode('utf-8')
    return text, BeautifulSoup(text, 'html.parser')


pathWkHtmlToImage = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'
imgkitConfig = imgkit.config(wkhtmltoimage=pathWkHtmlToImage)


# функция для сохранения картинок
def save_pic(s, directory, name, options):
    html = s.render()
    if not os.path.isdir(directory):
        os.makedirs(directory)
    imgkit.from_string(html, directory + name + ".png", config=imgkitConfig, options=options)
