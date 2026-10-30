import hashlib

import pikepdf
import pymupdf
import pytest

from grampo import operacoes
from grampo.erros import ErroAmigavel


def textos(caminho):
    with pymupdf.open(caminho) as doc:
        return [folha.get_text() for folha in doc]


def numeros_das_paginas(caminho):
    """Qual "Página N" do original está em cada folha do resultado."""
    resultado = []
    for texto in textos(caminho):
        for parte in texto.split():
            if parte.isdigit():
                resultado.append(int(parte))
                break
    return resultado


def resumo(caminho):
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


# ------------------------------------------------------------ páginas escritas pela pessoa

@pytest.mark.parametrize("texto, esperado", [
    ("1", [0]), ("1, 3-5", [0, 2, 3, 4]), ("5-", [4, 5]), ("-2", [0, 1]), ("2 a 3", [1, 2]),
    ("3-1", [2, 1, 0]), ("1,1,2", [0, 1]), (" 6 ; 1 ", [5, 0]),
])
def test_ler_paginas(texto, esperado):
    assert operacoes.ler_paginas(texto, 6) == esperado


@pytest.mark.parametrize("texto", ["", "0", "7", "abc", "1-9", ","])
def test_ler_paginas_recusa_o_que_nao_existe(texto):
    with pytest.raises(ErroAmigavel):
        operacoes.ler_paginas(texto, 6)


# ------------------------------------------------------------ organizar

def test_juntar_na_ordem(exemplos, saida):
    original = resumo(exemplos / "relatorio.pdf")
    destino = operacoes.juntar([exemplos / "anexo.pdf", exemplos / "relatorio.pdf"], saida / "junto.pdf")
    paginas = textos(destino)
    assert len(paginas) == 8
    assert "Anexo" in paginas[0] and "Relatório" in paginas[2]
    assert resumo(exemplos / "relatorio.pdf") == original  # o original não muda


def test_juntar_precisa_de_dois(exemplos, saida):
    with pytest.raises(ErroAmigavel):
        operacoes.juntar([exemplos / "anexo.pdf"], saida / "x.pdf")


def test_dividir_uma_por_arquivo(exemplos, saida):
    partes = operacoes.dividir(exemplos / "relatorio.pdf", saida, "relatorio")
    assert len(partes) == 6
    assert partes[0].name == "relatorio - página 1.pdf"
    assert [numeros_das_paginas(p) for p in partes] == [[n] for n in range(1, 7)]


def test_dividir_de_tantas_em_tantas(exemplos, saida):
    partes = operacoes.dividir(exemplos / "relatorio.pdf", saida, "r", modo="a_cada", a_cada=4)
    assert [numeros_das_paginas(p) for p in partes] == [[1, 2, 3, 4], [5, 6]]
    assert partes[0].name == "r - páginas 1 a 4.pdf"


def test_dividir_por_intervalos(exemplos, saida):
    partes = operacoes.dividir(exemplos / "relatorio.pdf", saida, "r", modo="intervalos", intervalos="1-2, 5-6")
    assert [numeros_das_paginas(p) for p in partes] == [[1, 2], [5, 6]]


def test_dividir_sem_dividir_avisa(exemplos, saida):
    with pytest.raises(ErroAmigavel):
        operacoes.dividir(exemplos / "relatorio.pdf", saida, "r", modo="a_cada", a_cada=10)


def test_extrair(exemplos, saida):
    destino = operacoes.extrair(exemplos / "relatorio.pdf", saida / "e.pdf", "5, 2")
    assert numeros_das_paginas(destino) == [5, 2]


def test_excluir(exemplos, saida):
    destino = operacoes.excluir(exemplos / "relatorio.pdf", saida / "x.pdf", "2-3")
    assert numeros_das_paginas(destino) == [1, 4, 5, 6]


def test_excluir_tudo_nao_deixa(exemplos, saida):
    with pytest.raises(ErroAmigavel, match="nenhuma página"):
        operacoes.excluir(exemplos / "relatorio.pdf", saida / "x.pdf", "1-6")


def test_reordenar(exemplos, saida):
    destino = operacoes.reordenar(exemplos / "relatorio.pdf", saida / "o.pdf", [5, 4, 3, 2, 1, 0])
    assert numeros_das_paginas(destino) == [6, 5, 4, 3, 2, 1]


def test_reordenar_precisa_de_todas(exemplos, saida):
    with pytest.raises(ErroAmigavel):
        operacoes.reordenar(exemplos / "relatorio.pdf", saida / "o.pdf", [0, 1, 2])


def test_girar_cada_pagina(exemplos, saida):
    destino = operacoes.girar(exemplos / "paginas-deitadas.pdf", saida / "g.pdf", {"1": 270, "3": 270, "0": 90})
    with pymupdf.open(destino) as doc:
        assert [folha.rotation for folha in doc] == [90, 0, 0, 0]


def test_girar_todas(exemplos, saida):
    destino = operacoes.girar(exemplos / "anexo.pdf", saida / "g.pdf", 180)
    with pymupdf.open(destino) as doc:
        assert [folha.rotation for folha in doc] == [180, 180]


def test_girar_sem_giro_avisa(exemplos, saida):
    with pytest.raises(ErroAmigavel):
        operacoes.girar(exemplos / "anexo.pdf", saida / "g.pdf", {"0": 0})


# ------------------------------------------------------------ otimizar e editar

def test_comprimir_diminui(exemplos, saida):
    destino, antes, depois = operacoes.comprimir(exemplos / "digitalizado-pesado.pdf", saida / "c.pdf", "forte")
    assert destino.is_file()
    assert depois < antes * 0.7
    assert len(textos(destino)) == 3


def test_comprimir_sem_ganho_nao_cria_arquivo(exemplos, saida):
    pequeno = saida / "pequeno.pdf"
    operacoes.comprimir(exemplos / "anexo.pdf", pequeno, "leve")
    if pequeno.exists():  # já comprimido uma vez: a segunda não tem mais o que tirar
        destino, antes, depois = operacoes.comprimir(pequeno, saida / "de-novo.pdf", "leve")
        assert destino is None and antes == depois
        assert not (saida / "de-novo.pdf").exists()


def test_marca_dagua_em_todas_as_paginas(exemplos, saida):
    destino = operacoes.marca_dagua(exemplos / "paginas-deitadas.pdf", saida / "m.pdf", "CONFIDENCIAL")
    assert all("CONFIDENCIAL" in t for t in textos(destino))


def test_marca_dagua_fica_dentro_da_folha_e_em_pe(exemplos, saida):
    """Também nas páginas que estavam giradas: o texto tem de aparecer inteiro na folha."""
    for posicao in ("diagonal", "centro", "topo-centro", "rodape-centro"):
        destino = operacoes.marca_dagua(exemplos / "paginas-deitadas.pdf", saida / f"m-{posicao}.pdf", "CÓPIA",
                                        posicao=posicao)
        with pymupdf.open(destino) as doc:
            for folha in doc:
                achados = folha.search_for("CÓPIA")
                assert achados, (posicao, folha.number)
                assert all(folha.rect.contains(r) for r in achados), (posicao, folha.number)


def test_marca_dagua_precisa_de_texto(exemplos, saida):
    with pytest.raises(ErroAmigavel):
        operacoes.marca_dagua(exemplos / "anexo.pdf", saida / "m.pdf", "  ")


def test_numerar(exemplos, saida):
    destino = operacoes.numerar(exemplos / "relatorio.pdf", saida / "n.pdf", formato="pagina-n-de-total")
    paginas = textos(destino)
    assert "Página 1 de 6" in paginas[0] and "Página 6 de 6" in paginas[5]


def test_numerar_pulando_a_capa(exemplos, saida):
    destino = operacoes.numerar(exemplos / "relatorio.pdf", saida / "n.pdf", posicao="topo-direita",
                                formato="n-de-total", pular_primeira=True)
    paginas = textos(destino)
    assert "de 5" not in paginas[0]
    assert "1 de 5" in paginas[1] and "5 de 5" in paginas[5]


def test_numerar_fica_no_canto_certo(exemplos, saida):
    destino = operacoes.numerar(exemplos / "paginas-deitadas.pdf", saida / "n.pdf", posicao="rodape-direita",
                                formato="n-de-total")
    with pymupdf.open(destino) as doc:
        for folha in doc:
            achado = folha.search_for(f"{folha.number + 1} de 4")[0]
            assert achado.x1 > folha.rect.width * 0.8 and achado.y1 > folha.rect.height * 0.9


# ------------------------------------------------------------ senha

def test_proteger_e_desproteger(exemplos, saida):
    protegido = operacoes.proteger(exemplos / "anexo.pdf", saida / "p.pdf", "segredo1")
    with pytest.raises(pikepdf.PasswordError):
        pikepdf.open(protegido)
    with pytest.raises(ErroAmigavel, match="senha não confere"):
        operacoes.desproteger(protegido, saida / "d.pdf", "errada")
    livre = operacoes.desproteger(protegido, saida / "d.pdf", "segredo1")
    with pikepdf.open(livre) as pdf:
        assert not pdf.is_encrypted and len(pdf.pages) == 2


def test_proteger_senha_curta(exemplos, saida):
    with pytest.raises(ErroAmigavel):
        operacoes.proteger(exemplos / "anexo.pdf", saida / "p.pdf", "12")


def test_desproteger_sem_senha_avisa(exemplos, saida):
    with pytest.raises(ErroAmigavel, match="pede senha"):
        operacoes.desproteger(exemplos / "com-senha.pdf", saida / "d.pdf")
    with pytest.raises(ErroAmigavel, match="não tem senha"):
        operacoes.desproteger(exemplos / "anexo.pdf", saida / "d.pdf")


def test_pdf_com_senha_nas_outras_ferramentas(exemplos, saida):
    with pytest.raises(ErroAmigavel, match="protegido com senha"):
        operacoes.excluir(exemplos / "com-senha.pdf", saida / "x.pdf", "1")


def test_arquivo_que_nao_e_pdf(exemplos, saida):
    with pytest.raises(ErroAmigavel, match="não parece ser um PDF"):
        operacoes.juntar([exemplos / "nao-e-pdf.pdf", exemplos / "anexo.pdf"], saida / "j.pdf")


def test_miniatura_e_png(exemplos):
    png = operacoes.miniatura(exemplos / "anexo.pdf", 0, 120)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
