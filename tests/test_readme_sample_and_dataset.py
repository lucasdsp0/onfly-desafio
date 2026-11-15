"""Regressão contra os valores oficiais do README (amostra) e contra o dataset completo.

Os valores do dataset completo foram calculados à parte, com um script independente do CLI
(csv + Decimal, sem reutilizar o código de src/).
"""

import json
from decimal import Decimal

import pytest
from helpers import PROJECT_ROOT
from helpers_extra import run_module

DATA = PROJECT_ROOT / "data"


def _run(tmp_path, nome_csv, top=5):
    saida = tmp_path / "report.json"
    result = run_module(
        [
            "--input",
            DATA / nome_csv,
            "--rates",
            DATA / "taxas_cambio.csv",
            "--output",
            saida,
            "--top",
            top,
        ]
    )
    assert result.returncode == 0, result.stderr
    return json.loads(saida.read_text(encoding="utf-8"))


def test_amostra_de_validacao_do_readme(tmp_path):
    report = _run(tmp_path, "exemplo-validacao.csv")

    assert report["report_version"] == "1.0"
    assert report["summary"] == {
        "total_reservations": 12,
        "confirmed_reservations": 9,
        "cancelled_reservations": 2,
        "no_show_reservations": 1,
        "total_room_nights": 28,
        "total_amount_brl": "7566.00",
        "average_nightly_rate_brl": "270.21",
    }
    assert report["by_month"] == [
        {"month": "2025-01", "reservations": 8, "room_nights": 25, "total_brl": "6684.00"},
        {"month": "2025-02", "reservations": 1, "room_nights": 3, "total_brl": "882.00"},
    ]
    assert report["top_hotels"] == [
        {"hotel_id": "H01", "hotel_name": "Hotel Aurora Paulista", "room_nights": 3, "total_brl": "1200.00"},
        {"hotel_id": "H02", "hotel_name": "Hotel Mirante", "room_nights": 2, "total_brl": "1084.00"},
        {"hotel_id": "H12", "hotel_name": "Hotel Miami Beach", "room_nights": 1, "total_brl": "1000.00"},
        {"hotel_id": "H10", "hotel_name": "Hotel Madrid, Gran Vía", "room_nights": 4, "total_brl": "900.00"},
        {"hotel_id": "H09", "hotel_name": "Hotel Lisboa, Centro", "room_nights": 3, "total_brl": "882.00"},
    ]


def test_dataset_completo_resumo(tmp_path):
    report = _run(tmp_path, "reservas_hoteis.csv")
    assert report["summary"] == {
        "total_reservations": 300,
        "confirmed_reservations": 235,
        "cancelled_reservations": 31,
        "no_show_reservations": 34,
        "total_room_nights": 1347,
        "total_amount_brl": "396170.00",
        "average_nightly_rate_brl": "294.11",
    }


def test_dataset_completo_por_mes(tmp_path):
    report = _run(tmp_path, "reservas_hoteis.csv")
    assert report["by_month"] == [
        {"month": "2024-12", "reservations": 35, "room_nights": 174, "total_brl": "61335.80"},
        {"month": "2025-01", "reservations": 37, "room_nights": 235, "total_brl": "64662.89"},
        {"month": "2025-02", "reservations": 26, "room_nights": 138, "total_brl": "45991.09"},
        {"month": "2025-03", "reservations": 39, "room_nights": 215, "total_brl": "65984.99"},
        {"month": "2025-04", "reservations": 21, "room_nights": 146, "total_brl": "31335.97"},
        {"month": "2025-05", "reservations": 39, "room_nights": 196, "total_brl": "63507.98"},
        {"month": "2025-06", "reservations": 38, "room_nights": 243, "total_brl": "63351.29"},
    ]


def test_dataset_completo_top_5_hoteis(tmp_path):
    report = _run(tmp_path, "reservas_hoteis.csv")
    assert report["top_hotels"] == [
        {"hotel_id": "H06", "hotel_name": "Hotel Salvador Centro", "room_nights": 160, "total_brl": "45165.46"},
        {"hotel_id": "H10", "hotel_name": "Hotel Madrid, Gran Vía", "room_nights": 120, "total_brl": "45041.69"},
        {"hotel_id": "H12", "hotel_name": "Hotel Miami Beach", "room_nights": 106, "total_brl": "41647.69"},
        {"hotel_id": "H07", "hotel_name": "Hotel Brasília Tower", "room_nights": 148, "total_brl": "39920.52"},
        {"hotel_id": "H11", "hotel_name": "Hotel Buenos Aires", "room_nights": 102, "total_brl": "37455.69"},
    ]


def test_dataset_completo_invariantes_entre_resumo_mes_e_hotel(tmp_path):
    # top alto o bastante para cobrir todos os hotéis do dataset (12)
    report = _run(tmp_path, "reservas_hoteis.csv", top=100)
    summary = report["summary"]

    assert sum(m["reservations"] for m in report["by_month"]) == summary["confirmed_reservations"]
    assert sum(m["room_nights"] for m in report["by_month"]) == summary["total_room_nights"]
    assert sum(h["room_nights"] for h in report["top_hotels"]) == summary["total_room_nights"]

    # Cada total é arredondado individualmente: a diferença máxima é meio centavo por parcela.
    total = Decimal(summary["total_amount_brl"])
    soma_meses = sum(Decimal(m["total_brl"]) for m in report["by_month"])
    soma_hoteis = sum(Decimal(h["total_brl"]) for h in report["top_hotels"])
    assert abs(soma_meses - total) <= Decimal("0.01") * len(report["by_month"]) / 2
    assert abs(soma_hoteis - total) <= Decimal("0.01") * len(report["top_hotels"]) / 2

    totais = [Decimal(h["total_brl"]) for h in report["top_hotels"]]
    assert totais == sorted(totais, reverse=True)
    assert len(report["top_hotels"]) == 12


@pytest.mark.parametrize("top", [1, 3, 12, 50])
def test_top_do_dataset_completo_e_prefixo_do_ranking_completo(tmp_path, top):
    completo = _run(tmp_path, "reservas_hoteis.csv", top=100)["top_hotels"]
    parcial = _run(tmp_path, "reservas_hoteis.csv", top=top)["top_hotels"]
    assert parcial == completo[:top]
