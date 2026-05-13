#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Organizador Automatico de Arquivos - Versao Windows (.exe)
Interface Grafica moderna com tkinter.
Compativel com Python 3.6+
"""

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import shutil
import threading
import sys
import os

# ---------------------------------------------------------------
# MAPA DE CATEGORIAS
# ---------------------------------------------------------------
CATEGORIAS = {
    "Documentos": [".pdf", ".docx", ".doc", ".txt", ".xlsx", ".xls", ".pptx", ".ppt", ".odt", ".ods", ".odp", ".csv", ".rtf"],
    "Imagens":    [".jpg", ".jpeg", ".png", ".gif", ".svg", ".bmp", ".webp", ".tiff", ".ico", ".raw"],
    "Videos":     [".mp4", ".mkv", ".mov", ".avi", ".wmv", ".flv", ".webm", ".m4v", ".mpg", ".mpeg"],
    "Musica":     [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma", ".m4a", ".opus"],
}

CATEGORIA_PADRAO = "Outros"

# Icones para cada categoria
ICONES = {
    "Documentos": "[DOC]",
    "Imagens": "[IMG]",
    "Videos": "[VID]",
    "Musica": "[MUS]",
    "Outros": "[...]",
}


def construir_mapa_extensao():
    """Inverte o dicionario CATEGORIAS: extensao -> categoria."""
    mapa = {}
    for categoria, extensoes in CATEGORIAS.items():
        for ext in extensoes:
            mapa[ext.lower()] = categoria
    return mapa


def gerar_nome_unico(destino):
    """Evita sobrescrever: arquivo.pdf -> arquivo_1.pdf -> arquivo_2.pdf..."""
    if not destino.exists():
        return destino
    nome_base = destino.stem
    extensao = destino.suffix
    pasta_pai = destino.parent
    contador = 1
    while True:
        novo_nome = pasta_pai / "{}_{}{}".format(nome_base, contador, extensao)
        if not novo_nome.exists():
            return novo_nome
        contador += 1


def organizar_pasta_logica(caminho_pasta, progress_callback=None, log_callback=None):
    """Logica principal: percorre a pasta e move os arquivos para subpastas."""
    mapa_ext = construir_mapa_extensao()

    try:
        arquivos = [
            f for f in caminho_pasta.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]
    except PermissionError:
        return {"total_movidos": 0, "total_erros": 1, "contagem": {}}

    if not arquivos:
        return {"total_movidos": 0, "total_erros": 0, "contagem": {}}

    total_movidos = 0
    total_erros = 0
    contagem_por_categoria = {}
    total_arquivos = len(arquivos)

    for i, arquivo in enumerate(arquivos):
        # Ignora o proprio executavel e scripts
        if arquivo.suffix.lower() in ('.py', '.exe', '.spec'):
            if progress_callback:
                progress_callback(int(((i + 1) / total_arquivos) * 100))
            continue

        extensao = arquivo.suffix.lower()
        categoria = mapa_ext.get(extensao, CATEGORIA_PADRAO)

        pasta_destino = caminho_pasta / categoria
        try:
            pasta_destino.mkdir(exist_ok=True)
        except PermissionError:
            if log_callback:
                log_callback("  [ERRO] Sem permissao para criar pasta: {}".format(categoria))
            total_erros += 1
            continue

        caminho_destino = gerar_nome_unico(pasta_destino / arquivo.name)

        try:
            shutil.move(str(arquivo), str(caminho_destino))
            total_movidos += 1
            contagem_por_categoria[categoria] = contagem_por_categoria.get(categoria, 0) + 1
            if log_callback:
                log_callback("  [OK] {}  ->  {}/".format(arquivo.name, categoria))
        except PermissionError:
            if log_callback:
                log_callback("  [BLOQUEADO] Sem permissao: {}".format(arquivo.name))
            total_erros += 1
        except Exception as e:
            if log_callback:
                log_callback("  [ERRO] {} ({})".format(arquivo.name, str(e)))
            total_erros += 1

        if progress_callback:
            progress_callback(int(((i + 1) / total_arquivos) * 100))

    return {
        "total_movidos": total_movidos,
        "total_erros": total_erros,
        "contagem": contagem_por_categoria,
    }


# ---------------------------------------------------------------
# INTERFACE GRAFICA (GUI) - Compativel com Windows 7/10/11
# ---------------------------------------------------------------
class OrganizadorApp(tk.Tk):
    # Paleta de Cores
    COR_FUNDO       = "#1e1e2e"
    COR_PAINEL      = "#2a2a3d"
    COR_DESTAQUE    = "#7c3aed"
    COR_DESTAQUE_HV = "#6d28d9"
    COR_TEXTO       = "#e2e8f0"
    COR_TEXTO_DIM   = "#94a3b8"
    COR_SUCESSO     = "#22c55e"
    COR_ERRO        = "#ef4444"
    COR_INPUT_BG    = "#334155"
    COR_BORDA       = "#475569"

    def __init__(self):
        super(OrganizadorApp, self).__init__()

        self.title("Organizador Automatico de Arquivos")
        self.geometry("620x520")
        self.resizable(False, False)
        self.configure(bg=self.COR_FUNDO)

        # Centralizar a janela na tela
        self.update_idletasks()
        w = 620
        h = 520
        x = (self.winfo_screenwidth() // 2) - (w // 2)
        y = (self.winfo_screenheight() // 2) - (h // 2)
        self.geometry("{}x{}+{}+{}".format(w, h, x, y))

        # Variaveis
        self.pasta_selecionada = tk.StringVar(value="")

        self._criar_widgets()

    def _criar_widgets(self):
        # -- Cabecalho --
        header = tk.Frame(self, bg=self.COR_DESTAQUE, height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Organizador Automatico de Arquivos",
            font=("Segoe UI", 15, "bold"),
            bg=self.COR_DESTAQUE,
            fg="white"
        ).pack(expand=True)

        # -- Corpo --
        body = tk.Frame(self, bg=self.COR_FUNDO, padx=25, pady=20)
        body.pack(fill=tk.BOTH, expand=True)

        # Instrucao
        tk.Label(
            body,
            text="Selecione a pasta com os arquivos que deseja organizar:",
            font=("Segoe UI", 10),
            bg=self.COR_FUNDO,
            fg=self.COR_TEXTO
        ).pack(anchor=tk.W, pady=(0, 8))

        # Frame de selecao de pasta
        frame_sel = tk.Frame(body, bg=self.COR_FUNDO)
        frame_sel.pack(fill=tk.X, pady=(0, 15))

        self.entry_pasta = tk.Entry(
            frame_sel,
            textvariable=self.pasta_selecionada,
            font=("Segoe UI", 10),
            bg=self.COR_INPUT_BG,
            fg=self.COR_TEXTO,
            insertbackground=self.COR_TEXTO,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightcolor=self.COR_DESTAQUE,
            highlightbackground=self.COR_BORDA
        )
        self.entry_pasta.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))

        btn_procurar = tk.Button(
            frame_sel,
            text="Procurar...",
            font=("Segoe UI", 10, "bold"),
            bg=self.COR_PAINEL,
            fg=self.COR_TEXTO,
            activebackground=self.COR_BORDA,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.selecionar_pasta
        )
        btn_procurar.pack(side=tk.RIGHT, ipady=6, ipadx=8)

        # Categorias info
        info_frame = tk.Frame(body, bg=self.COR_PAINEL, bd=0, highlightthickness=1, highlightbackground=self.COR_BORDA)
        info_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(
            info_frame,
            text="Categorias:  Documentos | Imagens | Videos | Musica | Outros",
            font=("Segoe UI", 9),
            bg=self.COR_PAINEL,
            fg=self.COR_TEXTO_DIM,
            pady=8,
            padx=10
        ).pack()

        # Status
        self.lbl_status = tk.Label(
            body,
            text="Aguardando selecao de pasta...",
            font=("Segoe UI", 9),
            bg=self.COR_FUNDO,
            fg=self.COR_TEXTO_DIM,
            anchor=tk.W
        )
        self.lbl_status.pack(fill=tk.X, pady=(0, 5))

        # Canvas para barra de progresso customizada
        self.progress_canvas = tk.Canvas(
            body, height=20, bg=self.COR_INPUT_BG,
            highlightthickness=1, highlightbackground=self.COR_BORDA, bd=0
        )
        self.progress_canvas.pack(fill=tk.X, pady=(0, 15))
        self.progress_fill = self.progress_canvas.create_rectangle(0, 0, 0, 20, fill=self.COR_DESTAQUE, width=0)

        # Log de atividade
        self.log_text = tk.Text(
            body, height=6,
            font=("Consolas", 9),
            bg=self.COR_INPUT_BG,
            fg=self.COR_TEXTO_DIM,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=self.COR_BORDA,
            state=tk.DISABLED,
            wrap=tk.WORD
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Botao Organizar
        self.btn_organizar = tk.Button(
            body,
            text="Organizar Agora!",
            font=("Segoe UI", 12, "bold"),
            bg=self.COR_DESTAQUE,
            fg="white",
            activebackground=self.COR_DESTAQUE_HV,
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            state=tk.DISABLED,
            command=self.iniciar_organizacao
        )
        self.btn_organizar.pack(fill=tk.X, ipady=10)

    def _log(self, mensagem):
        """Adiciona uma linha ao log visual."""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, mensagem + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _set_progress(self, valor):
        """Atualiza a barra de progresso customizada (0-100)."""
        self.progress_canvas.update_idletasks()
        largura_total = self.progress_canvas.winfo_width()
        largura_fill = int((valor / 100) * largura_total)
        cor = self.COR_SUCESSO if valor == 100 else self.COR_DESTAQUE
        self.progress_canvas.coords(self.progress_fill, 0, 0, largura_fill, 20)
        self.progress_canvas.itemconfig(self.progress_fill, fill=cor)

    def selecionar_pasta(self):
        """Abre o dialogo de selecao de pasta."""
        pasta_inicial = Path.home() / "Downloads"
        if not pasta_inicial.exists():
            pasta_inicial = Path.home() / "Desktop"
        if not pasta_inicial.exists():
            pasta_inicial = Path.home()

        pasta = filedialog.askdirectory(
            title="Selecione a pasta para organizar",
            initialdir=str(pasta_inicial)
        )
        if pasta:
            self.pasta_selecionada.set(pasta)
            self.btn_organizar.config(state=tk.NORMAL)
            self._set_progress(0)
            self.lbl_status.config(text="Pasta selecionada: {}".format(pasta), fg=self.COR_TEXTO)

            # Limpar log anterior
            self.log_text.config(state=tk.NORMAL)
            self.log_text.delete("1.0", tk.END)
            self.log_text.config(state=tk.DISABLED)

    def iniciar_organizacao(self):
        """Inicia a organizacao em uma thread separada."""
        caminho = self.pasta_selecionada.get()
        if not caminho:
            return

        pasta = Path(caminho)
        if not pasta.exists() or not pasta.is_dir():
            messagebox.showerror("Erro", "O caminho selecionado nao e valido.")
            return

        self.btn_organizar.config(state=tk.DISABLED)
        self._set_progress(0)
        self.lbl_status.config(text="Organizando arquivos...", fg=self.COR_TEXTO)

        # Limpar log
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete("1.0", tk.END)
        self.log_text.config(state=tk.DISABLED)

        def executar():
            resultados = organizar_pasta_logica(
                pasta,
                progress_callback=lambda v: self.after(0, lambda val=v: self._set_progress(val)),
                log_callback=lambda msg: self.after(0, lambda m=msg: self._log(m))
            )

            def mostrar_resultado():
                self._set_progress(100)
                self.btn_organizar.config(state=tk.NORMAL)

                if resultados["total_movidos"] == 0:
                    self.lbl_status.config(text="Nenhum arquivo encontrado para organizar.", fg=self.COR_TEXTO_DIM)
                    messagebox.showinfo("Resultado", "Nenhum arquivo solto encontrado nesta pasta.")
                else:
                    msg = "{} arquivo(s) organizados com sucesso!\n\n".format(resultados['total_movidos'])
                    for cat, count in sorted(resultados["contagem"].items()):
                        icone = ICONES.get(cat, "[...]")
                        msg += "  {}  {}: {} arquivo(s)\n".format(icone, cat, count)

                    if resultados["total_erros"] > 0:
                        msg += "\n{} arquivo(s) com erro.".format(resultados['total_erros'])

                    self.lbl_status.config(
                        text="Concluido! {} arquivo(s) organizados.".format(resultados['total_movidos']),
                        fg=self.COR_SUCESSO
                    )
                    messagebox.showinfo("Organizacao Concluida", msg)

            self.after(0, mostrar_resultado)

        threading.Thread(target=executar, daemon=True).start()


# ---------------------------------------------------------------
# PONTO DE ENTRADA
# ---------------------------------------------------------------
if __name__ == "__main__":
    try:
        app = OrganizadorApp()
        app.mainloop()
    except Exception as e:
        # Fallback: mostra erro em messagebox caso tkinter falhe
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("Erro Fatal", "Erro ao iniciar o programa:\n{}".format(str(e)))
        except Exception:
            pass
        sys.exit(1)
