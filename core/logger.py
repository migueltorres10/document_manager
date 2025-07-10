# core/logger.py

import logging
import os

def configurar_logger(nome_modulo):
    """
    Configura o logger para o módulo especificado.
    Cria um logger que escreve mensagens de debug e info em um arquivo e no console.
    Args:
        nome_modulo (str): Nome do módulo para o qual o logger será configurado.
    Returns:
        logging.Logger: O logger configurado.
    """
    logger = logging.getLogger(nome_modulo)
    logger.setLevel(logging.DEBUG)

    # Evita adicionar múltiplos handlers se já existirem
    if not logger.handlers:
        # Cria diretório de logs se necessário
        log_dir = os.path.join(os.getcwd(), "logs")
        os.makedirs(log_dir, exist_ok=True)

        log_file = os.path.join(log_dir, "app.log")

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(name)s: %(message)s")
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

