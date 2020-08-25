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
               'https://www.sports.ru/fantasy/football/team/points/2121292.html',
               'https://www.sports.ru/epl/',
               '🏴󠁧󠁢󠁥󠁮󠁧󠁿'),
    'Испания': ('https://www.marathonbet.ru/su/popular/Football/Spain/Primera+Division+-+8736',
                'https://www.sports.ru/fantasy/football/team/points/2152865.html',
                'https://www.sports.ru/la-liga/',
                '🇪🇸'),
    'Россия': ('https://www.marathonbet.ru/su/popular/Football/Russia/Premier+League+-+22433',
               'https://www.sports.ru/fantasy/football/team/points/2220482.html',
               'https://www.sports.ru/rfpl/',
               '🇷🇺'),
    'Италия': ('https://www.marathonbet.ru/su/popular/Football/Italy/Serie+A+-+22434',
               'https://www.sports.ru/fantasy/football/team/points/2167027.html',
               'https://www.sports.ru/seria-a/',
               '🇮🇹'),
    'Германия': ('https://www.marathonbet.ru/su/betting/Football/Germany/Bundesliga+-+22436',
                 'https://www.sports.ru/fantasy/football/team/points/2125988.html',
                 'https://www.sports.ru/bundesliga/',
                 '🇩🇪'),
    'Франция': ('https://www.marathonbet.ru/su/popular/Football/France/Ligue+1+-+21533',
                'https://www.sports.ru/fantasy/football/team/points/2230412.html',
                'https://www.sports.ru/ligue-1/',
                '🇫🇷'),
    'Нидерланды': ('',
                   'https://www.sports.ru/fantasy/football/team/points/2107940.html',
                   'https://www.sports.ru/eredivisie/',
                   '🇳🇱'),
    'Португалия': ('https://www.marathonbet.ru/su/popular/Football/Portugal/Primeira+Liga+-+43058',
                   'https://www.sports.ru/fantasy/football/team/points/2123584.html',
                   'https://www.sports.ru/liga-zon-sagres/',
                   '🇵🇹'),
    'Чемпионшип': ('https://www.marathonbet.ru/su/popular/Football/England/Championship+-+22807',
                   'https://www.sports.ru/fantasy/football/team/points/2107941.html',
                   'https://www.sports.ru/championship/',
                   '🏴󠁧󠁢󠁥󠁮󠁧󠁿'),
    'Турция': ('https://www.marathonbet.ru/su/betting/Football/Turkey/Super+Lig+-+46180',
               'https://www.sports.ru/fantasy/football/team/points/2154331.html',
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
                              }),
                    'Беларусь': ('Футбол - Чемпионат Беларуси. Высшая лига. 2020. Победитель',
                                 'https://1xstavka.ru/line/long/Football/2078497-Belarus-Winner/',
                                 {
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
                                 }),
                    'Россия': ('Футбол - Чемпионат России. Премьер-лига. 2020/21. Победитель',
                               'https://1xstavka.ru/line/long/Football/1752709-Russia-Winner/',
                               {
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
                               }),
                    'Франция': ('Футбол - Чемпионат Франции. Первая лига. 2020/21. Победитель',
                                'https://1xstavka.ru/line/long/Football/1756209-France-Winner/',
                                {
                                    'ПСЖ': 'ПСЖ',
                                    'Лион': 'Лион',
                                    'Олимпик Марсель': 'Марсель',
                                    'Монако': 'Монако',
                                    'Лилль': 'Лилль',
                                    'Монпелье': 'Монпелье',
                                    'Ренн': 'Ренн',
                                    'Ницца': 'Ницца',
                                    'Реймс': 'Реймс',
                                    'Нант': 'Нант',
                                    'Страсбург': 'Страсбур',
                                    'Сент-Этьен': 'Сент-Этьен',
                                    'Бордо': 'Бордо',
                                    'Ланс': 'Ланс',
                                    'Дижон': 'Дижон',
                                    'Анже': 'Анжер',
                                    'Лорьян': 'Лорьян',
                                    'Стад Брестуа 29': 'Брест',
                                    'Ним Олимпик': 'Ним',
                                    'Мец': 'Метц'
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
                   'Санта-Клара': 'Санта Клара'}

# fantasy-h2h.ru
H2H_LINKS = {'Россия': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/179',
             'Франция': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/180',
             'Германия': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/161',
             'Испания': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/162',
             'Англия': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/159',
             'Италия': 'https://fantasy-h2h.ru/analytics/fantasy_players_statistics/164'}
