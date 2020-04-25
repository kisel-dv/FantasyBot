"""
Модуль, в котором находятся некоторые общие функции, используемые в нескольких файлах
"""
import urllib.request
from bs4 import BeautifulSoup
from datetime import date
import imgkit
import os

path_wk_html_to_image = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltoimage.exe'

'''
словарь со строением вида:
название чемпионата -> (ссылка на раздел на марафоне,
                        ссылка на фентези-команду на спортсе,
                        ссылка на чемпионат на спортсе)
'''
champLinks = {
    'Беларусь': ('https://www.marathonbet.ru/su/betting/Football/Belarus/Vysshaya+League',
                 'https://by.tribuna.com/fantasy/football/team/points/2213674.html',
                 'https://www.sports.ru/premier-league-belarus/'),
    'Англия': ('',
               'https://www.sports.ru/fantasy/football/team/2121292.html',
               'https://www.sports.ru/epl/'),
    'Испания': ('',
                'https://www.sports.ru/fantasy/football/team/2152865.html',
                'https://www.sports.ru/la-liga/'),
    'Россия': ('',
               'https://www.sports.ru/fantasy/football/team/2089663.html',
               'https://www.sports.ru/rfpl/'),
    'Италия': ('',
               'https://www.sports.ru/fantasy/football/team/2167027.html',
               'https://www.sports.ru/seria-a/'),
    'Германия': ('',
                 'https://www.sports.ru/fantasy/football/team/2125988.html',
                 'https://www.sports.ru/bundesliga/'),
    'Франция': ('',
                'https://www.sports.ru/fantasy/football/team/2112406.html',
                'https://www.sports.ru/ligue-1/'),
    'Нидерланды': ('',
                   'https://www.sports.ru/fantasy/football/team/2107940.html',
                   'https://www.sports.ru/eredivisie/'),
    'Португалия': ('',
                   'https://www.sports.ru/fantasy/football/team/2123584.html',
                   'https://www.sports.ru/liga-zon-sagres/'),
    'Чемпионшип': ('',
                   'https://www.sports.ru/fantasy/football/team/2107941.html',
                   'https://www.sports.ru/championship/'),
    'Турция': ('',
               'https://www.sports.ru/fantasy/football/team/2154331.html',
               'https://www.sports.ru/super-lig/'),
    'Лига Чемпионов': ('',
                       'https://www.sports.ru/fantasy/football/team/2205029.html',
                       ''),
    'Лига Европы': ('',
                    'https://www.sports.ru/fantasy/football/team/2206981.html',
                    '')
}
# преобразование в словарь словарей
for key in champLinks:
    k = ('marathon', 'sportsFantasy', 'sports')
    champLinks[key] = dict(zip(k, champLinks[key]))


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
        # в будущем добавить запись ошибки в лог
        print('ERROR - Некорректный формат даты: ' + d)
        return date.today()


# функция для обработки каждой страницы, возвращает пару (текст страницы, soup объект)
def request_text_soup(link):
    req = urllib.request.Request(link)
    text = urllib.request.urlopen(req).read().decode('utf-8')
    return text, BeautifulSoup(text, 'html.parser')


# функция для сохранения картинок
def save_pic(s, directory, name, options):
    html = s.render()
    config = imgkit.config(wkhtmltoimage=path_wk_html_to_image)
    if not os.path.isdir(directory):
        os.makedirs(directory)
    imgkit.from_string(html, directory + name + ".png", config=config, options=options)
