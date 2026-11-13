from decimal import Decimal

from onfly_report.services.currency_converter import convert_to_brl


def test_usd():
    # 100 x 5.42 = 542
    assert convert_to_brl(Decimal("100.00"), "USD", {"USD": Decimal("5.42")}) == Decimal("542.00")


def test_eur():
    # 150 x 5.88 = 882
    assert convert_to_brl(Decimal("150.00"), "EUR", {"EUR": Decimal("5.88")}) == Decimal("882.00")


def test_sem_erro_de_float():
    # com float, 0.10 x 3 daria 0.30000000000000004
    assert convert_to_brl(Decimal("0.10"), "USD", {"USD": Decimal("3")}) == Decimal("0.30")