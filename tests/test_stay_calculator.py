from datetime import date

from onfly_report.services.stay_calculator import calculate_room_nights


def test_mesmo_mes():
    # 10/01 a 13/01 = 3 noites (exemplo do README)
    assert calculate_room_nights(date(2025, 1, 10), date(2025, 1, 13), 1) == 3


def test_virada_de_mes():
    # 30/01 a 02/02 = 3 noites
    assert calculate_room_nights(date(2025, 1, 30), date(2025, 2, 2), 1) == 3


def test_virada_de_ano():
    # 30/12 a 01/01 = 2 noites
    assert calculate_room_nights(date(2024, 12, 30), date(2025, 1, 1), 1) == 2


def test_varios_quartos():
    # 5 noites x 2 quartos = 10
    assert calculate_room_nights(date(2025, 1, 28), date(2025, 2, 2), 2) == 10