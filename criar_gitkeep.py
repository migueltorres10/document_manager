import os

# Subpastas que devem ter .gitkeep se estiverem vazias
PASTAS_IGNORAR = ["entrada", "separados", "obsoletos", "arquivados"]

def criar_gitkeep_em_subpastas_vazias(base_dir="."):
    print(f"🔍 Pasta raiz: {os.path.abspath(base_dir)}")

    # Percorre todas as subpastas diretas do base_dir
    for pasta_base in os.listdir(base_dir):
        caminho_base = os.path.join(base_dir, pasta_base)
        if not os.path.isdir(caminho_base):
            continue

        print(f"\n📂 A verificar: {caminho_base}")

        for nome_subpasta in PASTAS_IGNORAR:
            alvo = os.path.join(caminho_base, nome_subpasta)
            print(f"  ➤ Subpasta: {alvo}")

            if not os.path.exists(alvo):
                print("     ⛔ Não existe.")
                continue

            # Verifica se está vazia
            gitkeep = os.path.join(alvo, ".gitkeep")
            if not os.path.exists(gitkeep):
                with open(gitkeep, "w") as f:
                    f.write("")
                print(f"     ✅ Criado: {gitkeep}")
            else:
                print(f"     🟡 Já existia: {gitkeep}")

if __name__ == "__main__":
    criar_gitkeep_em_subpastas_vazias()
