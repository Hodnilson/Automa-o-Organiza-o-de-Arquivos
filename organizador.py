#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════╗
║           ORGANIZADOR AUTOMÁTICO DE ARQUIVOS                ║
║                                                              ║
║  Organiza arquivos de uma pasta em subpastas categorizadas   ║
║  por tipo: Documentos, Imagens, Vídeos, Música e Outros.     ║
╚══════════════════════════════════════════════════════════════╝

Uso:
    python organizador.py                    → Organiza a pasta atual
    python organizador.py /caminho/da/pasta  → Organiza a pasta especificada
"""

from pathlib import Path
import shutil
import sys
import logging
from datetime import datetime

# ─────────────────────────────────────────────────────────────
# CONFIGURAÇÃO DE LOG
# ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s │ %(levelname)-7s │ %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("organizador")

# ─────────────────────────────────────────────────────────────
# MAPA DE CATEGORIAS
# Cada categoria aponta para uma lista de extensões aceitas.
# Para adicionar novos tipos, basta incluir aqui.
# ─────────────────────────────────────────────────────────────
CATEGORIAS: dict[str, list[str]] = {
    "Documentos": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".odt", ".ods", ".odp", ".csv", ".rtf"],
    "Imagens":    [".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp", ".webp", ".tiff", ".ico", ".raw"],
    "Vídeos":     [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg"],
    "Música":     [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
}

# Categoria padrão para extensões não mapeadas
CATEGORIA_PADRAO = "Outros"


def construir_mapa_extensao() -> dict[str, str]:
    """
    Inverte o dicionário CATEGORIAS para criar um mapa rápido:
    extensão → categoria.
    Exemplo: {".pdf": "Documentos", ".jpg": "Imagens", ...}
    """
    mapa: dict[str, str] = {}
    for categoria, extensoes in CATEGORIAS.items():
        for ext in extensoes:
            mapa[ext.lower()] = categoria
    return mapa


def gerar_nome_unico(destino: Path) -> Path:
    """
    Evita sobrescrever arquivos.
    Se 'relatorio.pdf' já existe, retorna 'relatorio_1.pdf'.
    Se 'relatorio_1.pdf' também existe, retorna 'relatorio_2.pdf', etc.
    """
    if not destino.exists():
        return destino

    # Separa o nome base e a extensão
    nome_base = destino.stem
    extensao = destino.suffix
    pasta_pai = destino.parent
    contador = 1

    while True:
        novo_nome = pasta_pai / f"{nome_base}_{contador}{extensao}"
        if not novo_nome.exists():
            return novo_nome
        contador += 1


def organizar_pasta(caminho_pasta: Path) -> None:
    """
    Função principal que percorre todos os arquivos da pasta
    e os move para subpastas organizadas por categoria.
    """

    # ── Validação do caminho ──
    if not caminho_pasta.exists():
        log.error(f"❌ A pasta '{caminho_pasta}' não existe.")
        sys.exit(1)

    if not caminho_pasta.is_dir():
        log.error(f"❌ '{caminho_pasta}' não é um diretório válido.")
        sys.exit(1)

    # ── Construir mapa de extensões ──
    mapa_ext = construir_mapa_extensao()

    # ── Contadores para o relatório final ──
    total_movidos = 0
    total_erros = 0
    contagem_por_categoria: dict[str, int] = {}

    # ── Listar apenas arquivos (não subpastas, não ocultos) ──
    arquivos = [
        f for f in caminho_pasta.iterdir()
        if f.is_file() and not f.name.startswith(".")
    ]

    if not arquivos:
        log.info("📂 Nenhum arquivo encontrado para organizar.")
        return

    log.info(f"📂 Organizando {len(arquivos)} arquivo(s) em '{caminho_pasta}'...\n")

    # ── Processar cada arquivo ──
    for arquivo in arquivos:
        # Ignorar o próprio script caso esteja na mesma pasta
        if arquivo.name == Path(__file__).name:
            continue

        # Determinar a categoria pelo sufixo (extensão)
        extensao = arquivo.suffix.lower()
        categoria = mapa_ext.get(extensao, CATEGORIA_PADRAO)

        # Criar a subpasta de destino (se não existir)
        pasta_destino = caminho_pasta / categoria
        pasta_destino.mkdir(exist_ok=True)

        # Gerar caminho de destino (com proteção contra duplicatas)
        caminho_destino = gerar_nome_unico(pasta_destino / arquivo.name)

        try:
            shutil.move(str(arquivo), str(caminho_destino))
            log.info(f"  ✅ {arquivo.name:.<45s} → {categoria}/{caminho_destino.name}")
            total_movidos += 1
            contagem_por_categoria[categoria] = contagem_por_categoria.get(categoria, 0) + 1

        except PermissionError:
            log.warning(f"  🔒 Sem permissão para mover: {arquivo.name}")
            total_erros += 1

        except Exception as e:
            log.error(f"  ❌ Erro ao mover '{arquivo.name}': {e}")
            total_erros += 1

    # ── Relatório Final ──
    print("\n" + "═" * 55)
    print("  📊  RELATÓRIO DE ORGANIZAÇÃO")
    print("═" * 55)
    print(f"  📁 Pasta:            {caminho_pasta.resolve()}")
    print(f"  ✅ Arquivos movidos: {total_movidos}")
    print(f"  ❌ Erros:            {total_erros}")
    print("─" * 55)

    for cat, qtd in sorted(contagem_por_categoria.items()):
        print(f"  📂 {cat:<15s}  →  {qtd} arquivo(s)")

    print("═" * 55)
    print(f"  🕐 Concluído em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}")
    print("═" * 55 + "\n")


# ─────────────────────────────────────────────────────────────
# PONTO DE ENTRADA
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Se o usuário passou um caminho como argumento, usa ele.
    # Senão, usa a pasta atual de onde o script foi executado.
    if len(sys.argv) > 1:
        pasta_alvo = Path(sys.argv[1]).expanduser().resolve()
    else:
        pasta_alvo = Path.cwd()

    # Confirmação antes de executar (segurança)
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║       🗂️  ORGANIZADOR AUTOMÁTICO DE ARQUIVOS        ║")
    print("╚══════════════════════════════════════════════════════╝")
    print(f"\n  Pasta alvo: {pasta_alvo}\n")

    resposta = input("  Deseja organizar esta pasta? (s/n): ").strip().lower()

    if resposta in ("s", "sim", "y", "yes"):
        organizar_pasta(pasta_alvo)
    else:
        print("\n  ⏹️  Operação cancelada pelo usuário.\n")
