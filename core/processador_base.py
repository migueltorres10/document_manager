import os
from core.file_utils import dividir_e_mover_pdf

def processar_documentos(base_dir, nome_visualizador_cls):
    """
    Divide PDFs da entrada, move os originais para obsoletos,
    e abre o visualizador com a pasta de separados.
    """
    pasta_entrada = os.path.join(base_dir, "entrada")
    pasta_obsoletos = os.path.join(base_dir, "obsoletos")
    pasta_separados = os.path.join(base_dir, "separados")

    print("🔄 Movendo PDFs da entrada para separados...")
    arquivos_processados = dividir_e_mover_pdf(
        pasta_origem=pasta_entrada,
        pasta_obsoletos=pasta_obsoletos,
        pasta_separados=pasta_separados
    )

    if arquivos_processados:
        print(f"✅ {len(arquivos_processados)} arquivos processados.")
    else:
        print("⚠️ Nenhum PDF processado da entrada.")

    nome_visualizador_cls(pasta_pdf=pasta_separados, base_dir=base_dir)