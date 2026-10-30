import pymupdf
import pytest
from docx import Document
from PIL import Image

from grampo import conversao
from grampo.erros import ErroAmigavel


def test_imagens_em_a4(exemplos, saida):
    destino = conversao.imagens_para_pdf([exemplos / "foto1.jpg", exemplos / "foto2.png"], saida / "i.pdf")
    with pymupdf.open(destino) as doc:
        assert doc.page_count == 2
        deitada, em_pe = doc[0].rect, doc[1].rect
        assert deitada.width > deitada.height  # foto deitada -> A4 deitado
        assert em_pe.height > em_pe.width
        assert doc[0].get_images()


def test_imagem_do_tamanho_dela(exemplos, saida):
    destino = conversao.imagens_para_pdf([exemplos / "foto2.png"], saida / "i.pdf", tamanho="imagem")
    with pymupdf.open(destino) as doc:
        assert round(doc[0].rect.width / doc[0].rect.height, 2) == round(600 / 900, 2)


def test_imagem_com_transparencia(tmp_path, saida):
    transparente = tmp_path / "logo.png"
    Image.new("RGBA", (200, 100), (255, 0, 0, 0)).save(transparente)
    assert conversao.imagens_para_pdf([transparente], saida / "t.pdf").is_file()


def test_imagem_estragada(tmp_path, saida):
    falsa = tmp_path / "falsa.jpg"
    falsa.write_text("não sou imagem")
    with pytest.raises(ErroAmigavel, match="como imagem"):
        conversao.imagens_para_pdf([falsa], saida / "x.pdf")


def test_texto_para_pdf_com_acentos_e_varias_paginas(exemplos, saida):
    destino = conversao.texto_para_pdf(exemplos / "recibo.txt", saida / "t.pdf")
    with pymupdf.open(destino) as doc:
        assert doc.page_count >= 2
        assert "Padaria São João" in doc[0].get_text()


def test_texto_em_cp1252(tmp_path, saida):
    antigo = tmp_path / "antigo.txt"
    antigo.write_bytes("Ação e certidão".encode("cp1252"))
    destino = conversao.texto_para_pdf(antigo, saida / "a.pdf")
    with pymupdf.open(destino) as doc:
        assert "Ação e certidão" in doc[0].get_text()


def test_pdf_para_jpg(exemplos, saida):
    imagens = conversao.pdf_para_jpg(exemplos / "anexo.pdf", saida, "anexo", dpi=72)
    assert [i.name for i in imagens] == ["anexo - página 1.jpg", "anexo - página 2.jpg"]
    with Image.open(imagens[0]) as imagem:
        assert imagem.format == "JPEG" and imagem.size == (595, 842)


def test_pdf_para_word(exemplos, saida):
    destino = conversao.pdf_para_word(exemplos / "anexo.pdf", saida / "a.docx")
    texto = "\n".join(p.text for p in Document(destino).paragraphs)
    assert "Anexo" in texto and "Página 2" in texto


def test_pdf_para_word_com_senha(exemplos, saida):
    with pytest.raises(ErroAmigavel, match="protegido com senha"):
        conversao.pdf_para_word(exemplos / "com-senha.pdf", saida / "a.docx")


def test_tipo_office():
    assert conversao.tipo_office("a.DOCX") == "word"
    assert conversao.tipo_office("a.csv") == "excel"
    assert conversao.tipo_office("a.pptx") == "powerpoint"
    assert conversao.tipo_office("a.pdf") is None


def test_office_sem_programa_explica(monkeypatch, exemplos, saida):
    monkeypatch.setattr(conversao, "office_instalado", lambda tipo: False)
    monkeypatch.setattr(conversao, "achar_libreoffice", lambda: None)
    with pytest.raises(ErroAmigavel, match="LibreOffice"):
        conversao.office_para_pdf(exemplos / "contrato.docx", saida / "c.pdf")
    assert conversao.programas_disponiveis() == {"word": None, "excel": None, "powerpoint": None}


@pytest.mark.office
@pytest.mark.parametrize("arquivo, tipo, trecho", [
    ("contrato.docx", "word", "Cláusula 1"), ("balancete.xlsx", "excel", "Fevereiro"),
    ("reuniao.pptx", "powerpoint", "Reunião mensal"),
])
def test_office_de_verdade(exemplos, saida, arquivo, tipo, trecho):
    """Usa o Office (ou LibreOffice) instalado. Pula se o computador não tiver."""
    if not (conversao.office_instalado(tipo) or conversao.achar_libreoffice()):
        pytest.skip("sem Office nem LibreOffice neste computador")
    import win32print

    padrao = win32print.GetDefaultPrinter()
    destino = conversao.office_para_pdf(exemplos / arquivo, saida / (arquivo + ".pdf"))
    assert win32print.GetDefaultPrinter() == padrao  # a impressora padrão volta a ser a de antes
    with pymupdf.open(destino) as doc:
        assert trecho in "".join(folha.get_text() for folha in doc)
        tamanhos = [s["size"] for b in doc[0].get_text("dict")["blocks"] for l in b.get("lines", []) for s in l["spans"]]
        assert max(tamanhos) < 50  # com impressora "Somente Texto" o Word punha letra de 200 pontos
