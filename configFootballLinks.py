# количество матчей, начиная с которой мы можем использовать статистику из таблицы лиги
MATCHES_ENOUGH_TO_USE_TABLE_STATS = 5

"""
словарь со строением вида:
название чемпионата -> (ссылка на раздел на марафоне,
                        ссылка на фентези-команду на спортсе,
                        ссылка на чемпионат на спортсе,
                        эмоджи для отображения сообщения в телеграм-сообщении в канале)
"""
CHAMP_LINKS_FIELDS = ('marathon', 'sportsFantasy', 'sports', 'emoji')
CHAMP_LINKS = {
    'Корея': ('https://www.marathonbet.ru/su/betting/Football/Korea+Republic/K+League+1+-+6459526',
              'https://www.sports.ru/fantasy/football/team/points/2218267.html',
              'https://www.sports.ru/k-league-classic/',
              '🇰🇷'),
    'Беларусь': ('https://www.marathonbet.ru/su/betting/Football/Belarus/Vysshaya+League',
                 'https://by.tribuna.com/fantasy/football/team/points/2213674.html',
                 'https://www.sports.ru/premier-league-belarus/',
                 '🇧🇾'),
    'Англия': ('https://www.marathonbet.ru/su/popular/Football/England/Premier+League+-+21520',
               'https://www.sports.ru/fantasy/football/team/points/2239274.html',
               'https://www.sports.ru/epl/',
               '🏴󠁧󠁢󠁥󠁮󠁧󠁿'),
    'Испания': ('https://www.marathonbet.ru/su/popular/Football/Spain/Primera+Division+-+8736',
                'https://www.sports.ru/fantasy/football/team/points/2239275.html',
                'https://www.sports.ru/la-liga/',
                '🇪🇸'),
    'Россия': ('https://www.marathonbet.ru/su/popular/Football/Russia/Premier+League+-+22433',
               'https://www.sports.ru/fantasy/football/team/points/2220482.html',
               'https://www.sports.ru/rfpl/',
               '🇷🇺'),
    'Италия': ('https://www.marathonbet.ru/su/popular/Football/Italy/Serie+A+-+22434',
               'https://www.sports.ru/fantasy/football/team/points/2254077.html',
               'https://www.sports.ru/seria-a/',
               '🇮🇹'),
    'Германия': ('https://www.marathonbet.ru/su/popular/Football/Germany/Bundesliga+-+22436',
                 'https://www.sports.ru/fantasy/football/team/points/2242370.html',
                 'https://www.sports.ru/bundesliga/',
                 '🇩🇪'),
    'Франция': ('https://www.marathonbet.ru/su/popular/Football/France/Ligue+1+-+21533',
                'https://www.sports.ru/fantasy/football/team/points/2230412.html',
                'https://www.sports.ru/ligue-1/',
                '🇫🇷'),
    'Нидерланды': ('https://www.marathonbet.ru/su/popular/Football/Netherlands/Eredivisie+-+38090',
                   'https://www.sports.ru/fantasy/football/team/points/2240487.html',
                   'https://www.sports.ru/eredivisie/',
                   '🇳🇱'),
    'Португалия': ('https://www.marathonbet.ru/su/popular/Football/Portugal/Primeira+Liga+-+43058',
                   'https://www.sports.ru/fantasy/football/team/points/2254079.html',
                   'https://www.sports.ru/primeira-liga/',
                   '🇵🇹'),
    'Чемпионшип': ('https://www.marathonbet.ru/su/popular/Football/England/Championship+-+22807',
                   'https://www.sports.ru/fantasy/football/team/points/2239277.html',
                   'https://www.sports.ru/championship/',
                   '🏴󠁧󠁢󠁥󠁮󠁧󠁿'),
    'Турция': ('https://www.marathonbet.ru/su/popular/Football/Turkey/Super+Lig+-+46180',
               'https://www.sports.ru/fantasy/football/team/points/2243675.html',
               'https://www.sports.ru/super-lig/',
               '🇹🇷'),
    'Лига Чемпионов': ('https://www.marathonbet.ru/su/popular/Football/Clubs.+International/UEFA+Champions+League+-+21255',
                       'https://www.sports.ru/fantasy/football/team/points/2205029.html',
                       '',
                       '🇪🇺'),
    'Лига Европы': ('https://www.marathonbet.ru/su/popular/Football/Clubs.+International/UEFA+Europa+League+-+21366',
                    'https://www.sports.ru/fantasy/football/team/points/2206981.html',
                    '',
                    '🇪🇺')
}


XBET_CHAMP_LINKS_FIELDS = ('name', 'link', 'sports_map')
XBET_CHAMP_LINKS = {'Корея': ('Футбол - Чемпионат Южной Кореи. 2020. Победитель',
                              'https://1xstavka.ru/line/long/Football/1969006-South-Korea-Winner/',
                              {
                                  'Чонбук Моторс': 'Чонбук Хендай Моторс',
                                  'Ульсан Хёндэ': 'Ульсан Хендай',
                                  'Сувон Самсунг Блувингз': 'Сувон Самсунг Блювингс',
                                  'Соннам Ильва Чунма': 'Соннам',
                                  'Сангджу Сангму Феникс': 'Санчжу Санму',
                                  'Похан Стилерс': 'Пхохан Стилерс',
                                  'Кванджу': 'Кванчжу',
                                  'Гангвон': 'Канвон',
                              }),
                    'Беларусь': ('Футбол - Чемпионат Беларуси. Высшая лига. 2020. Победитель',
                                 'https://1xstavka.ru/line/long/Football/2078497-Belarus-Winner/',
                                 {
                                     'Шахтёр Солигорск': 'Шахтер Солигорск',
                                     'Торпедо БелАз': 'Торпедо-БелАЗ',
                                     'Энергетик БГУ': 'Энергетик-БГУ',
                                     'Смолевичи-СТИ': 'Смолевичи',
                                 }),
                    'Россия': ('Футбол - Чемпионат России. Премьер-лига. 2020/21. Победитель',
                               'https://1xstavka.ru/line/long/Football/1752709-Russia-Winner/',
                               {
                                   'Динамо Москва': 'Динамо',
                                   'Грозный': 'Ахмат',
                                   'Волгоград': 'Ротор'
                               }),
                    'Франция': ('Футбол - Чемпионат Франции. Первая лига. 2020/21. Победитель',
                                'https://1xstavka.ru/line/long/Football/1756209-France-Winner/',
                                {
                                    'Олимпик Марсель': 'Марсель',
                                    'Страсбург': 'Страсбур',
                                    'Анже': 'Анжер',
                                    'Стад Брестуа 29': 'Брест',
                                    'Ним Олимпик': 'Ним',
                                    'Мец': 'Метц'
                                }),
                    'Англия': ('Футбол - Чемпионат Англии. Премьер-лига. 2020/21. Победитель',
                               'https://1xstavka.ru/line/long/Football/819021-England-Winner/',
                               {
                                   'Тоттенхэм Хотспур': 'Тоттенхэм',
                                   'Лидс Юнайтед': 'Лидс',
                                   'Лестер Сити': 'Лестер',
                                   'Ньюкасл Юнайтед': 'Ньюкасл',
                                   'Вест Хэм Юнайтед': 'Вест Хэм',
                                   'Кристал Пэлэс': 'Кристал Пэлас',
                                   'Брайтон энд Хав Альбион': 'Брайтон',
                                   'Вест Бромвич Альбион': 'Вест Бромвич'
                               }),
                    'Испания': ('Футбол - Чемпионат Испании. Примера. 2020/21. Победитель',
                                'https://1xstavka.ru/line/long/Football/1753241-Spain-Winner/',
                                {
                                    'Атлетико Мадрид': 'Атлетико',
                                    'Атлетик Бильбао': 'Атлетик',
                                    'Реал Бетис': 'Бетис'
                                }),
                    'Чемпионшип': ('Футбол - Чемпионат Англии. Чемпионшип. 2020/21. Победитель',
                                   'https://1xstavka.ru/line/long/Football/819021-England-Winner/',
                                   {
                                       'Норвич Сити': 'Норвич',
                                       'Кардифф Сити': 'Кардифф',
                                       'Суонси Сити': 'Суонси',
                                       'Престон Норт Энд': 'Престон',
                                       'Блэкберн Роверс': 'Блэкберн',
                                       'Хаддерсфилд Таун': 'Хаддерсфилд',
                                       'Бирмингем Сити': 'Бирмингем',
                                       'Куинз Парк Рейнджерс': 'КПР',
                                       'Ковентри Сити': 'Ковентри',
                                       'Шеффилд Уинсдей': 'Шеффилд Уэнсдей',
                                       'Ротерхэм Юнайтед': 'Ротерхэм',
                                       'Уиком Уондерерс': 'Уиком'
                                   }),
                    'Турция': ('Футбол - Чемпионат Турции. Суперлига. 2020/21. Победитель',
                               'https://1xstavka.ru/line/long/Football/1752249-Turkey-Winner/',
                               {
                                   'Аланияспор': 'Аланьяспор',
                                   'Истанбул Башакшехир': 'Истанбул',
                                   'Йени Малатяспор': 'Ени Малатьяспор',
                                   'Газиантеп ББ': 'Газишехир Газиантеп',
                                   'Чайкур Ризеспор': 'Ризеспор',
                                   'ББ Эрзурум': 'Эрзурум ББ',
                                   'Фатих Карагумрук': 'Фатих Карагюмрюк'
                               }),
                    'Нидерланды': ('Футбол - Чемпионат Нидерландов. Эредивизи. 2020/21. Победитель',
                                   'https://1xstavka.ru/line/long/Football/2018748-Netherlands-Winner/',
                                   {
                                       'АЗ': 'АЗ Алкмар',
                                       'АДО Ден Хааг': 'Ден Хааг',
                                       'Спарта Роттердам': 'Спарта',
                                       'ВВВ-Венло': 'Венло',
                                       'Фортуна': 'Фортуна Ситтард',
                                       'Ваалвейк': 'Валвейк'
                                   }),
                    'Португалия': ('Футбол - Чемпионат Португалии. Премьер-лига. 2020/21. Победитель',
                                   'https://1xstavka.ru/line/long/Football/1777222-Portugal-Winner/',
                                   {
                                       'Витория Гимарайнш': 'Витория Гимараэш',
                                       'Боавишта Порту': 'Боавишта',
                                       'Риу-Аве': 'Риу Аве',
                                       'Маритимо': 'Маритиму Мадейра',
                                       'Насьонал Мадейра': 'Насьонал',
                                       'Пасуш Феррейра': 'Пасуш де Феррейра',
                                       'Фаренсе': 'Спортинг Фаренсе'
                                   }),
                    'Германия': ('Футбол - Чемпионат Германии. Бундеслига. 2020/21. Победитель',
                                 'https://1xstavka.ru/line/long/Football/819023-Germany-Winner/',
                                 {
                                     'Боруссия': 'Боруссия Д',
                                     'Боруссия Менхенгладбах': 'Боруссия М',
                                     'Айнтрахт Франкфурт': 'Айнтрахт Ф',
                                     'Шальке 04': 'Шальке',
                                     'Кёльн': 'Кельн',
                                     'Майнц 05': 'Майнц'
                                 }),
                    'Италия': ('Футбол - Чемпионат Италии. Серия А. 2020/21. Победитель',
                               'https://1xstavka.ru/line/long/Football/1756204-Italy-Winner/',
                               {
                                   'Специа': 'Специя'
                               })
                    }


# преобразование в словарь словарей
for key in CHAMP_LINKS:
    CHAMP_LINKS[key] = dict(zip(CHAMP_LINKS_FIELDS, CHAMP_LINKS[key]))

# преобразование в словарь словарей
for key in XBET_CHAMP_LINKS:
    XBET_CHAMP_LINKS[key] = dict(zip(XBET_CHAMP_LINKS_FIELDS, XBET_CHAMP_LINKS[key]))


# захардкоженные имена для нескольких клубов, для которых имена в разных местах на спортс.ру отличаются
# (профиль->таблица)
SPORTS_CLUB_MAP = {'Маритиму': 'Маритиму Мадейра',
                   'Санта-Клара': 'Санта Клара',
                   'Фаренсе': 'Спортинг Фаренсе'}

# fantasy-h2h.ru
H2H_LINKS = {'Россия': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/179',
             'Франция': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/180',
             'Германия': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/186',
             'Испания': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/182',
             'Англия': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/183',
             'Италия': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/189'}
