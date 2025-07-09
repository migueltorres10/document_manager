# core/logger.py

import logging

def configurar_logger(nome_modulo):
    logger = logging.getLogger(nome_modulo)

    if not logger.hasHandlers():  # Evita múltiplos handlers duplicados
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    return logger
