import shutil

import pytest

from grampo import ferramentas
from grampo.erros import ErroAmigavel
from grampo.saida import caminho_livre, limpar_nome


def nomes(resultado):
    return [p.rsplit("\\", 1)[-1].rsplit("/", 1)[-1] for p in resultado["arquivos"]]


def test_catalogo_coerente():
    grupos = {g for g, _ in ferramentas.GRUPOS}
    for f in ferramentas.FERRAMENTAS:
        assert f["grupo"] in grupos
        assert f["id"] in ferramentas.SUFIXO
        assert f["aceita"] and all(e.startswith(".") for e in f["aceita"])
        for o in f.get("opcoes", []):
            assert o["tipo"] in {"escolha", "texto", "senha", "numero", "marcar", "faixa"}


def test_nome_diz_a_operacao_e_nao_sobrescreve(exemplos, saida):
    entrada = [(exemplos / "anexo.pdf", "anexo.pdf"), (exemplos / "relatorio.pdf", "relatorio.pdf")]
    primeiro = ferramentas.executar("juntar", entrada, {}, saida)
    segundo = ferramentas.executar("juntar", entrada, {}, saida)
    assert nomes(primeiro) == ["anexo (juntado).pdf"]
    assert nomes(segundo) == ["anexo (juntado) (2).pdf"]


def test_dividir_vai_para_uma_pasta(exemplos, saida):
    resultado = ferramentas.executar("dividir", [(exemplos / "anexo.pdf", "anexo.pdf")], {"modo": "cada"}, saida)
    assert all("anexo (dividido)" in p for p in resultado["arquivos"])
    assert len(resultado["arquivos"]) == 2


def test_varios_arquivos_de_uma_vez(exemplos, saida):
    entrada = [(exemplos / "anexo.pdf", "anexo.pdf"), (exemplos / "relatorio.pdf", "relatorio.pdf")]
    resultado = ferramentas.executar("numerar", entrada, {}, saida)
    assert nomes(resultado) == ["anexo (numerado).pdf", "relatorio (numerado).pdf"]


def test_comprimir_conta_quanto_diminuiu(exemplos, saida):
    resultado = ferramentas.executar("comprimir", [(exemplos / "digitalizado-pesado.pdf", "pesado.pdf")],
                                     {"nivel": "forte"}, saida)
    assert nomes(resultado) == ["pesado (comprimido).pdf"]
    assert "% menor" in resultado["mensagem"]


def test_senhas_diferentes(exemplos, saida):
    with pytest.raises(ErroAmigavel, match="não estão iguais"):
        ferramentas.executar("proteger", [(exemplos / "anexo.pdf", "anexo.pdf")],
                             {"senha": "abcd", "confirmar": "abce"}, saida)


def test_tipo_de_arquivo_errado(exemplos, saida):
    with pytest.raises(ErroAmigavel, match="não serve aqui"):
        ferramentas.executar("comprimir", [(exemplos / "foto1.jpg", "foto1.jpg")], {}, saida)


def test_reordenar_sem_mudar_nada(exemplos, saida):
    with pytest.raises(ErroAmigavel, match="mesma ordem"):
        ferramentas.executar("reordenar", [(exemplos / "anexo.pdf", "anexo.pdf")], {"ordem": [0, 1]}, saida)


def test_imagens_juntas_ou_separadas(exemplos, saida):
    entrada = [(exemplos / "foto1.jpg", "foto1.jpg"), (exemplos / "foto2.png", "foto2.png")]
    assert nomes(ferramentas.executar("imagem_pdf", entrada, {}, saida)) == ["foto1 (convertido).pdf"]
    separados = ferramentas.executar("imagem_pdf", entrada, {"separados": True}, saida)
    assert nomes(separados) == ["foto1 (convertido) (2).pdf", "foto2 (convertido).pdf"]


def test_pdf_para_jpg_uma_pagina_fica_solta(exemplos, saida, tmp_path):
    uma = tmp_path / "uma.pdf"
    ferramentas.operacoes.extrair(exemplos / "anexo.pdf", uma, "1")
    resultado = ferramentas.executar("pdf_jpg", [(uma, "uma.pdf")], {"dpi": "72"}, saida)
    assert nomes(resultado) == ["uma (imagem).jpg"]


def test_original_continua_igual(exemplos, saida, tmp_path):
    copia = tmp_path / "relatorio.pdf"
    shutil.copy(exemplos / "relatorio.pdf", copia)
    antes = copia.read_bytes()
    for ferramenta, opcoes in (("marca", {"texto": "X"}), ("girar", {"giros": {"0": 90}}),
                               ("excluir", {"paginas": "1"}), ("proteger", {"senha": "abcd", "confirmar": "abcd"})):
        ferramentas.executar(ferramenta, [(copia, "relatorio.pdf")], opcoes, saida)
    assert copia.read_bytes() == antes


def test_limpar_nome_e_caminho_livre(tmp_path):
    assert limpar_nome('a<b>:"c?.pdf') == "abc.pdf"
    assert limpar_nome("...") == "documento"
    (tmp_path / "x.pdf").write_text("1")
    (tmp_path / "x (2).pdf").write_text("2")
    assert caminho_livre(tmp_path, "x.pdf").name == "x (3).pdf"
    (tmp_path / "pasta").mkdir()
    assert caminho_livre(tmp_path, "pasta").name == "pasta (2)"
