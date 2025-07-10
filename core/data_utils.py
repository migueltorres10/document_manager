# core/utils.py

import datetime
import logging

logger = logging.getLogger(__name__)

def parse_data_flexivel(data_str, formatos=None):
    """
    Tenta converter uma string de data para um objeto datetime.date, aceitando múltiplos formatos.

    Args:
        data_str (str): Data em formato string (ex: '20250710', '10/07/2025').
        formatos (list[str], opcional): Lista de formatos a tentar.

    Returns:
        datetime.date | None: Objeto date se conversão for bem-sucedida; senão, None.
    """
    if not formatos:
        formatos = ("%Y%m%d", "%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y")

    for formato in formatos:
        try:
            data = datetime.datetime.strptime(data_str.strip(), formato).date()
            logger.debug(f"Data formatada com sucesso: {data} usando formato '{formato}'")
            return data
        except ValueError:
            logger.debug(f"Formato de data '{formato}' não corresponde: {data_str}")
    logger.warning(f"Não foi possível converter data: {data_str}")
    return None
