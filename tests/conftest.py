import sys
from pathlib import Path

import pytest

PROJETO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJETO))
sys.path.insert(0, str(PROJETO / "exemplos"))

import gerar_exemplos  # noqa: E402


@pytest.fixture(scope="session")
def exemplos(tmp_path_factory):
    """Pasta com os arquivos de exemplo, criada uma vez para todos os testes."""
    return gerar_exemplos.gerar(tmp_path_factory.mktemp("exemplos"))


@pytest.fixture
def saida(tmp_path):
    pasta = tmp_path / "saida"
    pasta.mkdir()
    return pasta
