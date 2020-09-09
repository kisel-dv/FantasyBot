import logging
from math import log
from typing import Dict, Callable, Any

from configFootballLinks import SPORTS_CLUB_MAP

# среднее преимущество домашнего поля, основанное на исторической статистике
HOME_ADVANTAGE = 0.4


# функция для вычисления сложности календаря на основе средней статистики за текущее первенство
def difficulty_table(team1: str, team2: str, side: str, stats_data: Dict[str, float]) -> float:
    # поправка на место проведения игры - высчитана средняя в среднем для крупных европейских чемпионатов
    side_adv = HOME_ADVANTAGE * (1 if side == '(д)' else -1)
    # захардкоженные имена для нескольких клубов, для которых имена в разных местах на спортс.ру отличаются
    if SPORTS_CLUB_MAP.get(team2):
        team2 = SPORTS_CLUB_MAP[team2]
    # tableStats - глобальный, для доступа к переменной из основной функции обработки
    try:
        difficulty = stats_data[team1] - stats_data[team2]
        difficulty = side_adv + round(difficulty, 2)
        return difficulty
    except KeyError:
        # если нашлась новая проблема с разными названиями в разных местах на спортс ру
        logging.error('Неизвестный клуб, матч {} - {}'.format(team1, team2))
        return 0


# геттер для словаря, если ключа не было - применить к данным словаря некоторую функцию
def getter_probs(data: Dict[Any, Any], k: Any, func: Callable) -> Any:
    res = data.get(k)
    if res is None:
        logging.warning('Команда {} не найдена в маппинге в sports.ru имена'.format(k))
        res = func(data.values())
    return res


# функция для вычисления сложности календаря на основе букмекерских котиовок на чемпиона
def difficulty_probs(team1: str, team2: str, side: str, stats_data: Dict[str, float]) -> float:
    if side == '(г)':
        team1, team2 = team2, team1
    s1 = getter_probs(stats_data, team1, min)
    s2 = getter_probs(stats_data, team2, min)
    diff = 1.4 * (0.23 + 0.175*log(s1) - 0.148*log(s2))
    return diff * (1 if side == '(д)' else -1)
