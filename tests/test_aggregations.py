"""Regras de by_month e top_hotels."""

from helpers import run_cli
from helpers_extra import hotel_rows

# ---------------------------------------------------------------- by_month


def test_by_month_usa_o_mes_do_checkin_mesmo_quando_vira_o_mes(tmp_path):
    report = run_cli(
        tmp_path,
        [{"checkin_date": "2025-01-30", "checkout_date": "2025-02-02", "amount": "100.00"}],
    )
    assert report["by_month"] == [{"month": "2025-01", "reservations": 1, "room_nights": 3, "total_brl": "100.00"}]


def test_by_month_ordenado_ascendente_inclusive_na_virada_de_ano(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "checkin_date": "2025-02-10", "checkout_date": "2025-02-11"},
            {"reservation_id": "R-2", "checkin_date": "2024-12-30", "checkout_date": "2024-12-31"},
            {"reservation_id": "R-3", "checkin_date": "2025-01-05", "checkout_date": "2025-01-06"},
        ],
    )
    assert [m["month"] for m in report["by_month"]] == ["2024-12", "2025-01", "2025-02"]


def test_by_month_ignora_cancelled_e_no_show(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "checkin_date": "2025-01-10", "checkout_date": "2025-01-11"},
            {
                "reservation_id": "R-2",
                "status": "CANCELLED",
                "checkin_date": "2025-03-10",
                "checkout_date": "2025-03-11",
            },
            {"reservation_id": "R-3", "status": "NO_SHOW", "checkin_date": "2025-04-10", "checkout_date": "2025-04-11"},
            {
                "reservation_id": "R-4",
                "status": "CANCELLED",
                "checkin_date": "2025-01-12",
                "checkout_date": "2025-01-14",
            },
        ],
    )
    assert report["by_month"] == [{"month": "2025-01", "reservations": 1, "room_nights": 1, "total_brl": "100.00"}]


def test_by_month_soma_varias_reservas_do_mesmo_mes_com_cambio_e_quartos(tmp_path):
    report = run_cli(
        tmp_path,
        [
            # 2 noites x 2 quartos = 4 noites, 200.00 BRL
            {
                "reservation_id": "R-1",
                "rooms": "2",
                "checkin_date": "2025-01-10",
                "checkout_date": "2025-01-12",
                "amount": "200.00",
            },
            # 1 noite, 100 USD = 542.00 BRL
            {
                "reservation_id": "R-2",
                "currency": "USD",
                "amount": "100.00",
                "checkin_date": "2025-01-20",
                "checkout_date": "2025-01-21",
            },
        ],
    )
    assert report["by_month"] == [{"month": "2025-01", "reservations": 2, "room_nights": 5, "total_brl": "742.00"}]


# -------------------------------------------------------------- top_hotels


def test_top_hotels_ignora_hoteis_sem_reserva_confirmada(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "amount": "100.00"},
            {"reservation_id": "R-2", "hotel_id": "H09", "status": "CANCELLED", "amount": "9999.00"},
            {"reservation_id": "R-3", "hotel_id": "H08", "status": "NO_SHOW", "amount": "8888.00"},
        ],
    )
    assert [h["hotel_id"] for h in report["top_hotels"]] == ["H01"]


def test_top_hotels_conta_so_o_confirmado_de_hotel_com_status_misto(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "status": "CONFIRMED", "amount": "100.00"},
            {"reservation_id": "R-2", "status": "CANCELLED", "amount": "500.00", "checkout_date": "2025-01-15"},
            {"reservation_id": "R-3", "status": "NO_SHOW", "amount": "700.00", "checkout_date": "2025-01-15"},
        ],
    )
    assert report["top_hotels"] == [
        {"hotel_id": "H01", "hotel_name": "Hotel Teste", "room_nights": 1, "total_brl": "100.00"}
    ]


def test_top_hotels_agrega_varias_reservas_do_mesmo_hotel(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "hotel_id": "H09",
                "hotel_name": "Hotel Lisboa, Centro",
                "currency": "EUR",
                "amount": "150.00",
                "checkin_date": "2025-02-05",
                "checkout_date": "2025-02-08",
            },
            {
                "reservation_id": "R-2",
                "hotel_id": "H09",
                "hotel_name": "Hotel Lisboa, Centro",
                "rooms": "2",
                "amount": "100.00",
                "checkin_date": "2025-02-10",
                "checkout_date": "2025-02-11",
            },
        ],
    )
    assert report["top_hotels"] == [
        {"hotel_id": "H09", "hotel_name": "Hotel Lisboa, Centro", "room_nights": 5, "total_brl": "982.00"}
    ]


def test_top_hotels_ranqueia_pelo_valor_em_brl_e_nao_pelo_valor_original(tmp_path):
    # H01: 550 BRL ; H02: 100 EUR = 588 BRL. Em valor original H01 "ganharia" (550 > 100).
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H01", "currency": "BRL", "amount": "550.00"},
            {"reservation_id": "R-2", "hotel_id": "H02", "currency": "EUR", "amount": "100.00"},
        ],
    )
    assert [h["hotel_id"] for h in report["top_hotels"]] == ["H02", "H01"]


def test_top_hotels_ranqueia_por_valor_e_nao_por_noites(tmp_path):
    report = run_cli(
        tmp_path,
        [
            {
                "reservation_id": "R-1",
                "hotel_id": "H01",
                "amount": "100.00",
                "checkin_date": "2025-01-01",
                "checkout_date": "2025-01-11",
            },
            {
                "reservation_id": "R-2",
                "hotel_id": "H02",
                "amount": "900.00",
                "checkin_date": "2025-01-01",
                "checkout_date": "2025-01-02",
            },
        ],
    )
    assert [h["hotel_id"] for h in report["top_hotels"]] == ["H02", "H01"]
    assert [h["room_nights"] for h in report["top_hotels"]] == [1, 10]


def test_top_limita_a_quantidade_de_hoteis(tmp_path):
    report = run_cli(tmp_path, hotel_rows(4), top=2)
    assert [h["hotel_id"] for h in report["top_hotels"]] == ["H01", "H02"]


def test_top_maior_que_o_numero_de_hoteis_devolve_so_os_existentes(tmp_path):
    report = run_cli(tmp_path, hotel_rows(3), top=10)
    assert len(report["top_hotels"]) == 3


def test_desempate_decide_quem_fica_dentro_do_corte_do_top(tmp_path):
    # Três hotéis empatados; com top=2 ficam H01 e H02, independentemente da ordem no arquivo.
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H03", "amount": "500.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "amount": "500.00"},
            {"reservation_id": "R-3", "hotel_id": "H02", "amount": "500.00"},
        ],
        top=2,
    )
    assert [h["hotel_id"] for h in report["top_hotels"]] == ["H01", "H02"]


def test_desempate_apos_conversao_de_moeda(tmp_path):
    # 100 USD = 542.00 BRL, empata com 542.00 BRL.
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H02", "currency": "BRL", "amount": "542.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "currency": "USD", "amount": "100.00"},
        ],
    )
    assert [h["hotel_id"] for h in report["top_hotels"]] == ["H01", "H02"]
