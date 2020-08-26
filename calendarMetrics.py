import logging
from math import log
from typing import Dict

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


# функция для вычисления сложности календаря на основе букмекерских котиовок на чемпиона
def difficulty_probs(team1: str, team2: str, side: str, stats_data: Dict[str, float]) -> float:
    if side == '(г)':
        team1, team2 = team2, team1
    diff = 1.4 * (0.23 + 0.175*log(stats_data[team1]) - 0.148*log(stats_data[team2]))
    return diff * (1 if side == '(д)' else -1)
