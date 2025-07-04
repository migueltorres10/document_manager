# tests/test_ocr_utils.py
from datetime import datetime

from core.ocr_utils import extrair_ano


def test_extrair_ano_valido():
    assert extrair_ano("20250131") == "2025"

def test_extrair_ano_nulo():
    assert extrair_ano("") == str(datetime.now().year)