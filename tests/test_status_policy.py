from onfly_report.services.status_policy import is_billable


def test_confirmed_e_faturavel():
    assert is_billable("CONFIRMED") is True


def test_cancelled_nao_e_faturavel():
    assert is_billable("CANCELLED") is False


def test_no_show_nao_e_faturavel():
    # Somente CONFIRMED é faturável.
    assert is_billable("NO_SHOW") is False