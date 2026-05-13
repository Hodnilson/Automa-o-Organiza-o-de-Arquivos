# Organizador Automático de Arquivos 🗂️

Um script em Python robusto e moderno para organizar seus arquivos desordenados em pastas categorizadas por tipo (Documentos, Imagens, Vídeos, Música, etc).

## ✨ Funcionalidades

- **Categorização Inteligente:** Move arquivos automaticamente com base na extensão.
- **Proteção contra Duplicatas:** Se um arquivo com o mesmo nome já existir no destino, o script adiciona um sufixo numérico (ex: `foto_1.jpg`) em vez de sobrescrever.
- **Segurança:** Solicita confirmação do usuário antes de iniciar a movimentação.
- **Relatório Detalhado:** Exibe um resumo de quantos arquivos foram movidos para cada categoria.
- **Moderno:** Utiliza a biblioteca `pathlib` para manipulação de caminhos de forma segura em qualquer sistema operacional.

## 🚀 Como Usar

1. Certifique-se de ter o Python 3 instalado.
2. Baixe o arquivo `organizador.py`.
3. Execute o script no terminal:

```bash
# Para organizar a pasta onde o script está
python3 organizador.py

# Para organizar uma pasta específica
python3 organizador.py /caminho/para/sua/pasta
```

## 📂 Categorias Padrão

- **Documentos:** .pdf, .docx, .txt, .xlsx, .pptx, etc.
- **Imagens:** .jpg, .jpeg, .png, .gif, .svg, etc.
- **Vídeos:** .mp4, .mkv, .mov, .avi, etc.
- **Música:** .mp3, .wav, .flac, etc.
- **Outros:** Qualquer arquivo que não se encaixe nas categorias acima.

## 🛠️ Requisitos

- Python 3.6+
- Bibliotecas padrão (`pathlib`, `shutil`, `logging`) - nenhuma instalação externa necessária.

---
Desenvolvido com ❤️ para manter seu computador organizado.
