from helpers import run_cli


def test_empate_desempata_por_hotel_id(tmp_path):
    # hotéis com o mesmo total ficam em ordem crescente de hotel_id
    report = run_cli(
        tmp_path,
        [
            {"reservation_id": "R-1", "hotel_id": "H03", "amount": "500.00"},
            {"reservation_id": "R-2", "hotel_id": "H01", "amount": "500.00"},
            {"reservation_id": "R-3", "hotel_id": "H02", "amount": "900.00"},
        ],
        top=3,
    )
    assert [h["hotel_id"] for h in report["top_hotels"]] == ["H02", "H01", "H03"]