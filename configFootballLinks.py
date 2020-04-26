"""
словарь со строением вида:
название чемпионата -> (ссылка на раздел на марафоне,
                        ссылка на фентези-команду на спортсе,
                        ссылка на чемпионат на спортсе)
"""
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