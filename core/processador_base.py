## processador_base.py

import os
from core.file_utils import dividir_e_mover_pdf
from core.logger import configurar_logger

logger = configurar_logger(__name__)

def processar_documentos(base_dir, nome_visualizador_cls):
    """
    Processa documentos PDF de uma estrutura de diretórios base.

    Etapas:
    - Move os PDFs da subpasta 'entrada'.
    - Divide-os página a página na subpasta 'separados'.
    - Move os originais para 'obsoletos'.
    - Inicia a interface visualizadora com a pasta de separados.

    Args:
        base_dir (str): Diretório base onde estão as subpastas.
        nome_visualizador_cls (callable): Classe ou função que abre a interface gráfica com os PDFs.
    """
    pasta_entrada = os.path.join(base_dir, "entrada")
    pasta_obsoletos = os.path.join(base_dir, "obsoletos")
    pasta_separados = os.path.join(base_dir, "separados")

    logger.info("🔄 Iniciando processamento de PDFs da pasta de entrada...")

    arquivos_processados = dividir_e_mover_pdf(
        pasta_origem=pasta_entrada,
        pasta_obsoletos=pasta_obsoletos,
        pasta_separados=pasta_separados
    )

    if arquivos_processados:
        logger.info(f"✅ {len(arquivos_processados)} arquivo(s) processado(s) com sucesso.")
    else:
        logger.warning("⚠️ Nenhum PDF foi processado na pasta de entrada.")

    # Inicia a interface gráfica com os arquivos separados
    try:
        nome_visualizador_cls(pasta_pdf=pasta_separados, base_dir=base_dir)
        logger.info("🟢 Visualizador iniciado com sucesso.")
    except Exception as e:
        logger.exception(f"❌ Erro ao iniciar o visualizador: {e}")
