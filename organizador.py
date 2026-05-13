#!/usr/bin/env python3
"""
Organizador Automático de Arquivos - Versão com Interface Gráfica (GUI)
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import shutil
import logging
from datetime import datetime
import threading

# ─────────────────────────────────────────────────────────────
# MAPA DE CATEGORIAS
# ─────────────────────────────────────────────────────────────
CATEGORIAS: dict[str, list[str]] = {
    "Documentos": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".odt", ".ods", ".odp", ".csv", ".rtf"],
    "Imagens":    [".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp", ".webp", ".tiff", ".ico", ".raw"],
    "Vídeos":     [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg"],
    "Música":     [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
}

CATEGORIA_PADRAO = "Outros"

def construir_mapa_extensao() -> dict[str, str]:
    mapa: dict[str, str] = {}
    for categoria, extensoes in CATEGORIAS.items():
        for ext in extensoes:
            mapa[ext.lower()] = categoria
    return mapa

def gerar_nome_unico(destino: Path) -> Path:
    if not destino.exists():
        return destino
    nome_base = destino.stem
    extensao = destino.suffix
    pasta_pai = destino.parent
    contador = 1
    while True:
        novo_nome = pasta_pai / f"{nome_base}_{contador}{extensao}"
        if not novo_nome.exists():
            return novo_nome
        contador += 1

def organizar_pasta_logica(caminho_pasta: Path, progress_callback=None) -> dict:
    mapa_ext = construir_mapa_extensao()
    
    arquivos = [f for f in caminho_pasta.iterdir() if f.is_file() and not f.name.startswith(".")]
    
    if not arquivos:
        return {"total_movidos": 0, "total_erros": 0, "contagem": {}}

    total_movidos = 0
    total_erros = 0
    contagem_por_categoria: dict[str, int] = {}
    total_arquivos = len(arquivos)

    for i, arquivo in enumerate(arquivos):
        if arquivo.name == Path(__file__).name or arquivo.name.endswith('.exe'):
            continue

        extensao = arquivo.suffix.lower()
        categoria = mapa_ext.get(extensao, CATEGORIA_PADRAO)

        pasta_destino = caminho_pasta / categoria
        pasta_destino.mkdir(exist_ok=True)

        caminho_destino = gerar_nome_unico(pasta_destino / arquivo.name)

        try:
            shutil.move(str(arquivo), str(caminho_destino))
            total_movidos += 1
            contagem_por_categoria[categoria] = contagem_por_categoria.get(categoria, 0) + 1
        except Exception:
            total_erros += 1

        if progress_callback:
            progress_callback(int(((i + 1) / total_arquivos) * 100))

    return {
        "total_movidos": total_movidos,
        "total_erros": total_erros,
        "contagem": contagem_por_categoria
    }

# ─────────────────────────────────────────────────────────────
# INTERFACE GRÁFICA (GUI)
# ─────────────────────────────────────────────────────────────
class OrganizadorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Organizador Automático de Arquivos")
        self.geometry("500x300")
        self.resizable(False, False)
        
        # Estilo
        style = ttk.Style(self)
        style.theme_use('clam')
        
        # Variáveis
        self.pasta_selecionada = tk.StringVar(value="Nenhuma pasta selecionada")
        
        self.criar_widgets()
        
    def criar_widgets(self):
        # Frame Principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        lbl_titulo = ttk.Label(
            main_frame, 
            text="🗂️ Organizador de Arquivos", 
            font=("Helvetica", 16, "bold")
        )
        lbl_titulo.pack(pady=(0, 10))
        
        lbl_desc = ttk.Label(
            main_frame, 
            text="Escolha uma pasta com arquivos bagunçados para organizá-los\nautomaticamente por tipo (Imagens, Documentos, etc).",
            justify=tk.CENTER
        )
        lbl_desc.pack(pady=(0, 20))
        
        # Seleção de Pasta
        frame_selecao = ttk.Frame(main_frame)
        frame_selecao.pack(fill=tk.X, pady=(0, 20))
        
        lbl_pasta = ttk.Label(
            frame_selecao, 
            textvariable=self.pasta_selecionada, 
            background="#f0f0f0", 
            padding=5,
            relief="sunken"
        )
        lbl_pasta.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        btn_procurar = ttk.Button(
            frame_selecao, 
            text="Procurar...", 
            command=self.selecionar_pasta
        )
        btn_procurar.pack(side=tk.RIGHT)
        
        # Barra de Progresso
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            main_frame, 
            variable=self.progress_var, 
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=(0, 20))
        
        # Botão Organizar
        self.btn_organizar = ttk.Button(
            main_frame, 
            text="✨ Organizar Agora!", 
            command=self.iniciar_organizacao,
            state=tk.DISABLED
        )
        self.btn_organizar.pack(ipady=5, ipadx=10)

    def selecionar_pasta(self):
        pasta = filedialog.askdirectory(title="Selecione a pasta para organizar")
        if pasta:
            self.pasta_selecionada.set(pasta)
            self.btn_organizar.config(state=tk.NORMAL)
            self.progress_var.set(0)

    def atualizar_progresso(self, valor):
        self.progress_var.set(valor)
        self.update_idletasks()

    def iniciar_organizacao(self):
        caminho = self.pasta_selecionada.get()
        if not caminho or caminho == "Nenhuma pasta selecionada":
            return
            
        pasta = Path(caminho)
        if not pasta.exists() or not pasta.is_dir():
            messagebox.showerror("Erro", "O caminho selecionado não é válido.")
            return

        self.btn_organizar.config(state=tk.DISABLED)
        self.progress_var.set(0)
        
        # Executar a lógica em uma thread separada para não travar a GUI
        def executar():
            resultados = organizar_pasta_logica(pasta, self.atualizar_progresso)
            
            # Formatar mensagem de sucesso
            if resultados["total_movidos"] == 0:
                msg = "Nenhum arquivo encontrado solto nesta pasta para organizar."
                tipo = messagebox.showinfo
            else:
                msg = f"Sucesso! {resultados['total_movidos']} arquivo(s) organizados.\n\n"
                for cat, count in resultados["contagem"].items():
                    msg += f"📂 {cat}: {count}\n"
                
                if resultados["total_erros"] > 0:
                    msg += f"\n❌ Erros: {resultados['total_erros']} arquivo(s) não puderam ser movidos."
                
                tipo = messagebox.showinfo if resultados["total_erros"] == 0 else messagebox.showwarning
                
            self.after(0, lambda: tipo("Resumo da Organização", msg))
            self.after(0, lambda: self.btn_organizar.config(state=tk.NORMAL))
            self.after(0, lambda: self.progress_var.set(100))

        threading.Thread(target=executar, daemon=True).start()

if __name__ == "__main__":
    try:
        app = OrganizadorApp()
        app.mainloop()
    except Exception as e:
        import sys
        # Tenta mostrar erro se o tkinter falhar (ex: falta de bibliotecas no linux)
        print(f"Erro ao iniciar a interface gráfica: {e}", file=sys.stderr)
