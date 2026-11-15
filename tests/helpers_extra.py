"""Utilitários adicionais para os testes novos (não altera tests/helpers.py fornecido)."""

from __future__ import annotations

import csv
import os
import subprocess
import sys
from pathlib import Path

from helpers import BASE, COLUMNS, PROJECT_ROOT, SRC_DIR

DEFAULT_RATES = "currency,rate_to_brl\nBRL,1.000000\nUSD,5.420000\nEUR,5.880000\n"


def write_reservations(path: Path, rows: list[dict[str, str]]) -> Path:
    """Grava um CSV de reservas completo (cada linha é mesclada sobre BASE)."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS, lineterminator="\n")
        writer.writeheader()
        writer.writerows({**BASE, **row} for row in rows)
    return path


def write_rates(path: Path, content: str = DEFAULT_RATES) -> Path:
    path.write_text(content, encoding="utf-8")
    return path


def run_module(
    args: list[object],
    cwd: Path | None = None,
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess:
    """Executa `python -m onfly_report` e devolve o processo, sem exigir exit code 0."""
    environment = os.environ.copy()
    environment["PYTHONPATH"] = str(SRC_DIR) + os.pathsep + environment.get("PYTHONPATH", "")
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment.update(extra_env or {})
    return subprocess.run(
        [sys.executable, "-m", "onfly_report", *[str(arg) for arg in args]],
        cwd=str(cwd or PROJECT_ROOT),
        env=environment,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )


def hotel_rows(count: int, **overrides: str) -> list[dict[str, str]]:
    """Gera `count` reservas CONFIRMED, cada uma em um hotel distinto (H01, H02, ...)."""
    return [
        {
            "reservation_id": f"R-{index}",
            "hotel_id": f"H{index:02d}",
            "hotel_name": f"Hotel {index}",
            "amount": f"{1000 - index * 10}.00",
            **overrides,
        }
        for index in range(1, count + 1)
    ]
