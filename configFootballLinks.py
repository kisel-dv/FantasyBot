"""
словарь со строением вида:
название чемпионата -> (ссылка на раздел на марафоне,
                        ссылка на фентези-команду на спортсе,
                        ссылка на чемпионат на спортсе,
                        эмоджи для отображения сообщения в телеграм-сообщении в канале)
"""
CHAMP_LINKS = {
    'Корея': ('https://www.marathonbet.ru/su/betting/Football/Korea+Republic/K+League+1+-+6459526',
              'https://www.sports.ru/fantasy/football/team/2218267.html',
              'https://www.sports.ru/k-league-classic/',
              '🇰🇷'),
    # 'Беларусь': ('https://www.marathonbet.ru/su/betting/Football/Belarus/Vysshaya+League',
    #              'https://by.tribuna.com/fantasy/football/team/points/2213674.html',
    #              'https://www.sports.ru/premier-league-belarus/',
    #              '🇧🇾'),
    'Англия': ('https://www.marathonbet.ru/su/popular/Football/England/Premier+League+-+21520',
               'https://www.sports.ru/fantasy/football/team/2121292.html',
               'https://www.sports.ru/epl/',
               '🏴󠁧󠁢󠁥󠁮󠁧󠁿'),
    'Испания': ('https://www.marathonbet.ru/su/popular/Football/Spain/Primera+Division+-+8736',
                'https://www.sports.ru/fantasy/football/team/2152865.html',
                'https://www.sports.ru/la-liga/',
                '🇪🇸'),
    'Россия': ('https://www.marathonbet.ru/su/popular/Football/Russia/Premier+League+-+22433',
               'https://www.sports.ru/fantasy/football/team/2089663.html',
               'https://www.sports.ru/rfpl/',
               '🇷🇺'),
    'Италия': ('https://www.marathonbet.ru/su/popular/Football/Italy/Serie+A+-+22434',
               'https://www.sports.ru/fantasy/football/team/2167027.html',
               'https://www.sports.ru/seria-a/',
               '🇮🇹'),
    'Германия': ('https://www.marathonbet.ru/su/betting/Football/Germany/Bundesliga+-+22436',
                 'https://www.sports.ru/fantasy/football/team/2125988.html',
                 'https://www.sports.ru/bundesliga/',
                 '🇩🇪'),
    'Франция': ('',
                'https://www.sports.ru/fantasy/football/team/2112406.html',
                'https://www.sports.ru/ligue-1/',
                '🇫🇷'),
    'Нидерланды': ('',
                   'https://www.sports.ru/fantasy/football/team/2107940.html',
                   'https://www.sports.ru/eredivisie/',
                   '🇳🇱'),
    'Португалия': ('https://www.marathonbet.ru/su/popular/Football/Portugal/Primeira+Liga+-+43058',
                   'https://www.sports.ru/fantasy/football/team/2123584.html',
                   'https://www.sports.ru/liga-zon-sagres/',
                   '🇵🇹'),
    'Чемпионшип': ('https://www.marathonbet.ru/su/popular/Football/England/Championship+-+22807',
                   'https://www.sports.ru/fantasy/football/team/2107941.html',
                   'https://www.sports.ru/championship/',
                   '🏴󠁧󠁢󠁥󠁮󠁧󠁿'),
    'Турция': ('https://www.marathonbet.ru/su/betting/Football/Turkey/Super+Lig+-+46180',
               'https://www.sports.ru/fantasy/football/team/2154331.html',
               'https://www.sports.ru/super-lig/',
               '🇹🇷'),
    'Лига Чемпионов': ('',
                       'https://www.sports.ru/fantasy/football/team/2205029.html',
                       '',
                       '🇪🇺'),
    'Лига Европы': ('',
                    'https://www.sports.ru/fantasy/football/team/2206981.html',
                    '',
                    '🇪🇺')
}


# маппинг названий команд на 1xbet -> sports.ru
xbetToSportsMap = {
    'Корея': {
        'Чонбук Моторс': 'Чонбук Хендай Моторс',
        'Ульсан Хёндэ': 'Ульсан Хендай',
        'Тэгу': 'Тэгу',
        'Сувон Самсунг Блувингз': 'Сувон Самсунг Блювингс',
        'Соннам Ильва Чунма': 'Соннам',
        'Сеул': 'Сеул',
        'Сангджу Сангму Феникс': 'Санчжу Санму',
        'Похан Стилерс': 'Пхохан Стилерс',
        'Пусан Ай Парк': 'Пусан Ай Парк',
        'Кванджу': 'Кванчжу',
        'Гангвон': 'Канвон',
        'Инчхон Юнайтед': 'Инчхон Юнайтед'
    },
    'Беларусь': {
        'БАТЭ': 'БАТЭ',
        'Шахтёр Солигорск': 'Шахтер Солигорск',
        'Динамо Брест': 'Динамо Брест',
        'Торпедо БелАз': 'Торпедо-БелАЗ',
        'Слуцк': 'Слуцк',
        'Динамо Минск': 'Динамо Минск',
        'Ислочь': 'Ислочь',
        'Неман': 'Неман',
        'Витебск': 'Витебск',
        'Энергетик БГУ': 'Энергетик-БГУ',
        'Городея': 'Городея',
        'Минск': 'Минск',
        'Славия Мозырь': 'Славия Мозырь',
        'Рух Брест': 'Рух Брест',
        'Смолевичи-СТИ': 'Смолевичи',
        'Белшина': 'Белшина'
    }
}


# преобразование в словарь словарей
for key in CHAMP_LINKS:
    k = ('marathon', 'sportsFantasy', 'sports', 'emoji')
    CHAMP_LINKS[key] = dict(zip(k, CHAMP_LINKS[key]))
    if key in xbetToSportsMap:
        CHAMP_LINKS[key]['1x_sports_map'] = xbetToSportsMap[key]
