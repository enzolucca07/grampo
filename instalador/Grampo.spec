# Receita do PyInstaller: transforma o Grampo num programa (Grampo.exe) que não precisa de Python no computador.
# Quem usa é o instalador/montar.py.
from pathlib import Path

from PyInstaller.utils.hooks import collect_all

PROJETO = Path(SPECPATH).parent
dados, binarios, ocultos = [], [], []
for pacote in ("webview", "pymupdf", "pdf2docx", "pptx", "openpyxl"):  # carregam partes de si mesmos pelo nome, na hora
    d, b, o = collect_all(pacote)
    dados, binarios, ocultos = dados + d, binarios + b, ocultos + o

analise = Analysis(
    [str(PROJETO / "app.py")],
    pathex=[str(PROJETO)],
    datas=[(str(PROJETO / pasta), pasta) for pasta in ("templates", "static")] + dados,
    binaries=binarios,
    hiddenimports=ocultos + ["win32timezone", "pythoncom", "win32ui"],
    excludes=["tkinter", "tests", "pytest", "matplotlib", "pymupdf4llm", "pymupdf_layout"],
)
pyz = PYZ(analise.pure)
exe = EXE(pyz, analise.scripts, [], exclude_binaries=True, name="Grampo", console=False,
          icon=str(Path(SPECPATH) / "grampo.ico"))
COLLECT(exe, analise.binaries, analise.datas, name="Grampo")
