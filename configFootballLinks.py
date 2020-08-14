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
    'Беларусь': ('https://www.marathonbet.ru/su/betting/Football/Belarus/Vysshaya+League',
                 'https://by.tribuna.com/fantasy/football/team/points/2213674.html',
                 'https://www.sports.ru/premier-league-belarus/',
                 '🇧🇾'),
    'Англия': ('https://www.marathonbet.ru/su/popular/Football/England/Premier+League+-+21520',
               'https://www.sports.ru/fantasy/football/team/2121292.html',
               'https://www.sports.ru/epl/',
               '🏴󠁧󠁢󠁥󠁮󠁧󠁿'),
    'Испания': ('https://www.marathonbet.ru/su/popular/Football/Spain/Primera+Division+-+8736',
                'https://www.sports.ru/fantasy/football/team/2152865.html',
                'https://www.sports.ru/la-liga/',
                '🇪🇸'),
    'Россия': ('https://www.marathonbet.ru/su/popular/Football/Russia/Premier+League+-+22433',
               'https://www.sports.ru/fantasy/football/team/2220482.html',
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
                'https://www.sports.ru/fantasy/football/team/2230412.html',
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
    'Лига Чемпионов': ('https://www.marathonbet.ru/su/popular/Football/Clubs.+International/UEFA+Champions+League+-+21255',
                       'https://www.sports.ru/fantasy/football/team/2205029.html',
                       '',
                       '🇪🇺'),
    'Лига Европы': ('https://www.marathonbet.ru/su/popular/Football/Clubs.+International/UEFA+Europa+League+-+21366',
                    'https://www.sports.ru/fantasy/football/team/2206981.html',
                    '',
                    '🇪🇺')
}

# преобразование в словарь словарей
for key in CHAMP_LINKS:
    k = ('marathon', 'sportsFantasy', 'sports', 'emoji')
    CHAMP_LINKS[key] = dict(zip(k, CHAMP_LINKS[key]))

# количество матчей, начиная с которой мы можем использовать статистику из таблицы лиги
MATCHES_ENOUGH_TO_USE_TABLE_STATS = 5

XBET_CHAMP_NAMES = {'Корея': 'Футбол - Чемпионат Южной Кореи. 2020. Победитель',
                    'Беларусь': 'Футбол - Чемпионат Беларуси. Высшая лига. 2020. Победитель',
                    'Россия': 'Футбол - Чемпионат России. Премьер-лига. 2020/21. Победитель'}

XBET_LONG_BETS = {'Корея': 'https://1xstavka.ru/line/long/Football/1969006-South-Korea-Winner/',
                  'Беларусь': 'https://1xstavka.ru/line/long/Football/2078497-Belarus-Winner/',
                  'Россия': 'https://1xstavka.ru/line/long/Football/1752709-Russia-Winner/'}

# 1xbet -> sports.ru
# todo: поменять этот маппинг на маппинг исправлений, где эти имена разные
XBET_TO_SPORTS_TEAM_MAP = {
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
    },
    'Россия': {
        'Зенит': 'Зенит',
        'Краснодар': 'Локомотив',
        'Локомотив': 'Краснодар',
        'ЦСКА': 'ЦСКА',
        'Спартак': 'Спартак',
        'Динамо Москва': 'Динамо',
        'Ростов': 'Ростов',
        'Рубин': 'Рубин',
        'Сочи': 'Сочи',
        'Урал': 'Урал',
        'Ротор': 'Ротор',
        'Химки': 'Химки',
        'Уфа': 'Уфа',
        'Арсенал Тула': 'Арсенал Тула',
        'Тамбов': 'Тамбов',
        'Ахмат': 'Ахмат',
        'Грозный': 'Ахмат',
        'Волгоград': 'Ротор'
    }
}
