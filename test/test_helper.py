from datetime import date

import pytest

from src.helper import Helper


@pytest.mark.parametrize('code,coeff,expected', [
    (4, None, (2.0, False)),  # обычный невременнаый разряд
    (104, None, (2.0, True)), # временный разряд
    (30, None, (1.2, False)), # иностранец при отсуствии коэффициента
    (30, 2, (0.6, False)),    # иностранный при наличии коэффициента
    (95, None, (-2.5, True)), # Временный -2.5
])
def test_rank_conversion(code, coeff, expected):
    assert Helper.getRazr(code, coeff) == expected


@pytest.mark.parametrize('code,coeff,expected', [
    (4, None, "2.0"),  # обычный невременнаый разряд
    (104, None, "2.0*"), # временный разряд
    (-2, None, "-1.0"), # отрицательный разряд
    (1, None, "0.5"), # с половинкой
    (101, None, "0.5*"), # временный с половинкой
    (30, None, "1.2"), # иностранец при отсуствии коэффициента
    (30, 2, "0.6"),    # иностранный при наличии коэффициента
    (95, None, "-2.5*"), # Временный -2.5
])
def test_rank_string(code, coeff, expected):
    assert Helper.getRazrStr(code, coeff) == expected


@pytest.mark.parametrize('target,expected', [
    (date(2020, 1, 1), date(2021, 1, 1)),
    (date(2021, 1, 1), date(2021, 1, 1)),
    (date(2021, 6, 1), date(2021, 1, 1)),
    (date(2023, 1, 1), date(2022, 1, 1)),
])
def test_rating_date(target, expected):
    """Helper для выбора ближайшей даты рейтинга
    Должен возвращать последнюю дану из списка, не превышающую запрашиваемую"""
    assert Helper.getDate(target, [date(2022, 1, 1), date(2021, 1, 1)]) == expected


@pytest.mark.parametrize('value,expected', [
    (None, [None]), ('', [None]), (' ; , ', [None]),
    ('a,b; c', ['a', 'b', 'c']),
])
def test_split_contacts(value, expected):
    assert Helper.smartSplit(value) == expected
