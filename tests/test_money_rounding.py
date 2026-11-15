"""Regras de exatidão monetária: Decimal, soma exata, arredondamento só na serialização (half-up)."""

import re

from helpers import run_cli

MONEY = re.compile(r"^\d+\.\d{2}$")


def test_arredondamento_half_up_no_valor_convertido(tmp_path):
    # 0.75 USD x 5.42 = 4.065 -> half-up = 4.07 (half-even daria 4.06)
    report = run_cli(tmp_path, [{"currency": "USD", "amount": "0.75"}])
    assert report["summary"]["total_amount_brl"] == "4.07"
    assert report["by_month"][0]["total_brl"] == "4.07"
    assert report["top_hotels"][0]["total_brl"] == "4.07"


def test_media_diaria_usa_half_up(tmp_path):
    # 1.00 / 8 noites = 0.125 -> half-up = 0.13 (half-even daria 0.12)
    report = run_cli(
        tmp_path,
        [{"amount": "1.00", "checkin_date": "2025-01-10", "checkout_date": "2025-01-18"}],
    )
    assert report["summary"]["total_room_nights"] == 8
    assert report["summary"]["average_nightly_rate_brl"] == "0.13"


def test_soma_exata_e_arredonda_so_no_final(tmp_path):
    # Cada reserva vale 0.01 x 5.42 = 0.0542. Arredondada por linha seria 0.05 + 0.05 = 0.10;
    # somando o valor exato: 0.1084 -> 0.11.
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "currency": "USD", "amount": "0.01"},
            {"reservation_id": "R-2", "hotel_id": "H02", "currency": "USD", "amount": "0.01"},
        ],
    )
    assert report["summary"]["total_amount_brl"] == "0.11"
    assert [h["total_brl"] for h in report["top_hotels"]] == ["0.05", "0.05"]


def test_soma_exata_dentro_do_mesmo_hotel_e_mes(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "currency": "USD", "amount": "0.01"},
            {"reservation_id": "R-2", "currency": "USD", "amount": "0.01"},
        ],
    )
    assert report["by_month"][0]["total_brl"] == "0.11"
    assert report["top_hotels"][0]["total_brl"] == "0.11"


def test_media_diaria_usa_total_exato_e_nao_o_total_arredondado(tmp_path):
    # total exato 0.1084 / 2 noites = 0.0542 -> "0.05".
    # Se usasse o total já arredondado (0.11 / 2 = 0.055) daria "0.06".
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "currency": "USD", "amount": "0.01"},
            {"reservation_id": "R-2", "hotel_id": "H02", "currency": "USD", "amount": "0.01"},
        ],
    )
    assert report["summary"]["total_room_nights"] == 2
    assert report["summary"]["average_nightly_rate_brl"] == "0.05"


def test_media_diaria_arredonda_dizima_para_cima(tmp_path):
    # 2000.00 / 3 noites = 666.666... -> 666.67
    report = run_cli(
        tmp_path,
        [{"amount": "2000.00", "checkin_date": "2025-01-10", "checkout_date": "2025-01-13"}],
    )
    assert report["summary"]["average_nightly_rate_brl"] == "666.67"


def test_valor_nao_e_multiplicado_pela_quantidade_de_quartos(tmp_path):
    # `amount` é o valor da reserva; `rooms` só multiplica as noites.
    report = run_cli(
        tmp_path,
        [{"amount": "300.00", "rooms": "3", "checkin_date": "2025-01-10", "checkout_date": "2025-01-12"}],
    )
    assert report["summary"]["total_room_nights"] == 6
    assert report["summary"]["total_amount_brl"] == "300.00"
    assert report["summary"]["average_nightly_rate_brl"] == "50.00"


def test_dinheiro_e_string_com_duas_casas_sem_separador_de_milhar(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "amount": "1234.50"},
            {"reservation_id": "R-2", "hotel_id": "H02", "amount": "1000000.00"},
        ],
    )
    assert report["summary"]["total_amount_brl"] == "1001234.50"
    money_values = [
        report["summary"]["total_amount_brl"],
        report["summary"]["average_nightly_rate_brl"],
        *(month["total_brl"] for month in report["by_month"]),
        *(hotel["total_brl"] for hotel in report["top_hotels"]),
    ]
    for value in money_values:
        assert isinstance(value, str)
        assert MONEY.match(value), value
    assert [h["total_brl"] for h in report["top_hotels"]] == ["1000000.00", "1234.50"]


def test_moedas_distintas_convertidas_com_tabela_de_cambio(tmp_path):
    # EUR 150 x 5.88 = 882.00 ; USD 200 x 5.42 = 1084.00
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "currency": "EUR", "amount": "150.00"},
            {"reservation_id": "R-2", "hotel_id": "H02", "currency": "USD", "amount": "200.00"},
        ],
    )
    assert report["summary"]["total_amount_brl"] == "1966.00"
    assert [h["total_brl"] for h in report["top_hotels"]] == ["1084.00", "882.00"]
