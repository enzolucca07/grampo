"""Onde o resultado é gravado: na pasta Downloads (ou na que a pessoa escolher), sem nunca sobrescrever nada."""

import ctypes
import json
import os
import re
import uuid
from pathlib import Path

PASTA_DADOS = Path(os.environ.get("LOCALAPPDATA") or Path.home()) / "Grampo"
ARQUIVO_CONFIGURACAO = PASTA_DADOS / "configuracao.json"


def pasta_downloads():
    """A pasta Downloads de verdade (a pessoa pode ter mudado de lugar, por exemplo para o OneDrive)."""
    try:
        from ctypes import wintypes

        class GUID(ctypes.Structure):
            _fields_ = [("Data1", wintypes.DWORD), ("Data2", wintypes.WORD), ("Data3", wintypes.WORD),
                        ("Data4", ctypes.c_ubyte * 8)]

        pasta_guid = GUID.from_buffer_copy(uuid.UUID("{374DE290-123F-4565-9164-39C4925E467B}").bytes_le)  # Downloads
        caminho = ctypes.c_wchar_p()
        if ctypes.windll.shell32.SHGetKnownFolderPath(ctypes.byref(pasta_guid), 0, None, ctypes.byref(caminho)) == 0:
            resultado = Path(caminho.value)
            ctypes.windll.ole32.CoTaskMemFree(caminho)
            return resultado
    except (AttributeError, OSError):
        pass
    return Path.home() / "Downloads"


def ler_configuracao():
    try:
        return json.loads(ARQUIVO_CONFIGURACAO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def gravar_configuracao(dados):
    PASTA_DADOS.mkdir(parents=True, exist_ok=True)
    ARQUIVO_CONFIGURACAO.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")


def pasta_de_saida():
    escolhida = ler_configuracao().get("pasta_de_saida")
    if escolhida and Path(escolhida).is_dir():
        return Path(escolhida)
    return pasta_downloads()


def escolher_pasta_de_saida(caminho):
    """None volta para a Downloads."""
    dados = ler_configuracao()
    if caminho:
        dados["pasta_de_saida"] = str(Path(caminho))
    else:
        dados.pop("pasta_de_saida", None)
    gravar_configuracao(dados)


def limpar_nome(nome):
    """Tira do nome o que o Windows não aceita."""
    nome = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", nome).strip(" .")
    return nome or "documento"


def caminho_livre(pasta, nome):
    """`pasta/nome`, ou `nome (2)`, `nome (3)`... se já existir um arquivo ou pasta com esse nome."""
    pasta = Path(pasta)
    candidato = pasta / nome
    base, ext = Path(nome).stem, Path(nome).suffix
    if candidato.is_dir() or ext == "":
        base, ext = nome, ""
    numero = 2
    while candidato.exists():
        candidato = pasta / f"{base} ({numero}){ext}"
        numero += 1
    return candidato
