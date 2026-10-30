"""Monta o instalador do Grampo: dist\\Grampo-<versão>.exe.

  .venv\\Scripts\\python.exe instalador\\montar.py

Precisa do PyInstaller (já vem no requirements de desenvolvimento) e do Inno Setup 6 (jrsoftware.org). A versão vem
de grampo/__init__.py (VERSAO).
"""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PASTA_PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PASTA_PROJETO))

from grampo import VERSAO  # noqa: E402

# A montagem (milhares de arquivos) fica fora do OneDrive, que trava os arquivos enquanto sincroniza
PASTA_MONTAGEM = Path(tempfile.gettempdir()) / "Grampo-montagem"
LUGARES_DO_INNO = [Path(os.environ.get(variavel, "")) / "Inno Setup 6" / "ISCC.exe"
                   for variavel in ("ProgramFiles(x86)", "ProgramFiles")] + \
                  [Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Inno Setup 6" / "ISCC.exe"]


def achar_inno():
    for caminho in [shutil.which("ISCC"), *LUGARES_DO_INNO]:
        if caminho and Path(caminho).is_file():
            return Path(caminho)
    return None


def main():
    instalador = PASTA_PROJETO / "instalador"
    if not (instalador / "grampo.ico").is_file():
        subprocess.run([sys.executable, str(instalador / "gerar_icone.py")], check=True)
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean",
                    "--distpath", str(PASTA_MONTAGEM / "dist"), "--workpath", str(PASTA_MONTAGEM / "build"),
                    str(instalador / "Grampo.spec")], check=True)
    programa = PASTA_MONTAGEM / "dist" / "Grampo"
    print("Programa montado em", programa)
    inno = achar_inno()
    if not inno:
        print("Inno Setup 6 não encontrado: o programa ficou montado, mas sem instalador. "
              "Instale de https://jrsoftware.org/isdl.php e rode de novo.")
        return
    subprocess.run([str(inno), f"/DVersao={VERSAO}", f"/DPrograma={programa}", str(instalador / "Grampo.iss")],
                   check=True)
    print("Instalador em", PASTA_PROJETO / "dist" / f"Grampo-{VERSAO}.exe")


if __name__ == "__main__":
    main()
