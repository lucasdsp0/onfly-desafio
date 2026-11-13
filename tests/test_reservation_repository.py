from pathlib import Path

from onfly_report.repositories.csv_reservation_repository import CsvReservationRepository

ARQUIVO = Path(__file__).resolve().parent.parent / "data" / "reservas_hoteis.csv"


def test_le_todas_as_reservas_do_arquivo():
    linhas = CsvReservationRepository(ARQUIVO).read()
    assert len(linhas) == 300