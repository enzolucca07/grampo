"""As operações em PDF. Cada função recebe os caminhos de entrada e de saída e não mexe no original.

`avisar(fracao, texto)` é opcional e conta o andamento (0.0 a 1.0) para a barra da tela.
As páginas são contadas a partir de 0 aqui dentro; na tela, a partir de 1.
"""

import re
from pathlib import Path

import pikepdf
import pymupdf

from .erros import DANIFICADO, PROTEGIDO, ErroAmigavel


def _nada(fracao, texto=""):
    pass


def abrir_pdf(caminho):
    """Abre um PDF com o PyMuPDF; avisa em português se ele tiver senha ou estiver estragado."""
    caminho = Path(caminho)
    try:
        doc = pymupdf.open(caminho, filetype="pdf")
    except Exception:
        raise ErroAmigavel(DANIFICADO.format(nome=caminho.name)) from None
    if doc.needs_pass:
        doc.close()
        raise ErroAmigavel(PROTEGIDO)
    if doc.page_count == 0:
        doc.close()
        raise ErroAmigavel(f"“{caminho.name}” não tem nenhuma página.")
    return doc


def contar_paginas(caminho):
    with abrir_pdf(caminho) as doc:
        return doc.page_count


def tem_senha(caminho):
    try:
        with pymupdf.open(caminho, filetype="pdf") as doc:
            return bool(doc.needs_pass)
    except Exception:
        return False


def salvar(doc, destino):
    """Grava o PDF já limpando o que sobrou de páginas tiradas (fica menor)."""
    destino = Path(destino)
    destino.parent.mkdir(parents=True, exist_ok=True)
    doc.save(destino, garbage=3, deflate=True)
    return destino


def ler_paginas(texto, total):
    """Lê o que a pessoa escreveu ("1, 3-5, 8-") e devolve as páginas, a partir de 0, na ordem e sem repetir.

    "8-" vai da 8 até a última; "-3" vai da primeira até a 3.
    """
    texto = (texto or "").strip()
    if not texto:
        raise ErroAmigavel("Diga quais páginas: por exemplo 1, 3-5, 8.")
    paginas = []
    for parte in re.split(r"[,;]", texto):
        parte = parte.strip().replace(" ", "")
        if not parte:
            continue
        faixa = re.fullmatch(r"(\d*)(?:[-–a]|até)(\d*)", parte)
        if faixa and (faixa.group(1) or faixa.group(2)):
            inicio = int(faixa.group(1) or 1)
            fim = int(faixa.group(2) or total)
        elif parte.isdigit():
            inicio = fim = int(parte)
        else:
            raise ErroAmigavel(f"Não entendi “{parte}”. Escreva números de página, como 1, 3-5, 8.")
        if inicio < 1 or fim < 1 or inicio > total or fim > total:
            raise ErroAmigavel(f"O PDF tem {total} página{'s' if total > 1 else ''}; “{parte}” fica fora disso.")
        passo = 1 if fim >= inicio else -1
        for numero in range(inicio, fim + passo, passo):
            if numero - 1 not in paginas:
                paginas.append(numero - 1)
    if not paginas:
        raise ErroAmigavel("Diga quais páginas: por exemplo 1, 3-5, 8.")
    return paginas


def ler_intervalos(texto, total):
    """"1-3, 4-6, 7" -> [[0, 1, 2], [3, 4, 5], [6]]: cada pedaço vira um PDF na hora de dividir."""
    grupos = [ler_paginas(parte, total) for parte in re.split(r"[,;]", texto or "") if parte.strip()]
    if not grupos:
        raise ErroAmigavel("Diga como dividir: por exemplo 1-3, 4-6, 7.")
    return grupos


# ---------------------------------------------------------------- organizar


def juntar(entradas, destino, avisar=_nada):
    if len(entradas) < 2:
        raise ErroAmigavel("Escolha pelo menos dois PDFs para juntar.")
    with pymupdf.open() as novo:
        for i, entrada in enumerate(entradas):
            avisar(i / len(entradas), f"Juntando {Path(entrada).name}")
            with abrir_pdf(entrada) as doc:
                novo.insert_pdf(doc)
        avisar(0.95, "Gravando")
        return salvar(novo, destino)


def copiar_paginas(entrada, paginas, destino):
    """Um PDF novo só com estas páginas, na ordem pedida."""
    with abrir_pdf(entrada) as doc:
        with pymupdf.open() as novo:
            for pagina in paginas:
                novo.insert_pdf(doc, from_page=pagina, to_page=pagina)
            return salvar(novo, destino)


def dividir(entrada, pasta, nome_base, modo="cada", a_cada=1, intervalos="", avisar=_nada):
    """Divide em vários PDFs dentro de `pasta`. Modos: "cada" (uma página por arquivo), "a_cada" (de N em N
    páginas) e "intervalos" (como a pessoa escreveu: 1-3, 4-6)."""
    total = contar_paginas(entrada)
    if modo == "intervalos":
        grupos = ler_intervalos(intervalos, total)
    else:
        passo = 1 if modo == "cada" else int(a_cada or 0)
        if passo < 1:
            raise ErroAmigavel("O número de páginas por arquivo precisa ser 1 ou mais.")
        grupos = [list(range(i, min(i + passo, total))) for i in range(0, total, passo)]
    if len(grupos) == 1 and len(grupos[0]) == total:
        raise ErroAmigavel("Do jeito escolhido o PDF ficaria inteiro num arquivo só. Escolha pedaços menores.")
    digitos = len(str(total))
    saidas = []
    for i, grupo in enumerate(grupos):
        avisar(i / len(grupos), f"Criando a parte {i + 1} de {len(grupos)}")
        primeira, ultima = grupo[0] + 1, grupo[-1] + 1
        if len(grupo) == 1:
            rotulo = f"página {primeira:0{digitos}d}"
        else:
            rotulo = f"páginas {primeira:0{digitos}d} a {ultima:0{digitos}d}"
        saidas.append(copiar_paginas(entrada, grupo, Path(pasta) / f"{nome_base} - {rotulo}.pdf"))
    return saidas


def extrair(entrada, destino, paginas):
    """`paginas`: lista (a partir de 0) ou o texto que a pessoa escreveu."""
    if isinstance(paginas, str):
        paginas = ler_paginas(paginas, contar_paginas(entrada))
    return copiar_paginas(entrada, paginas, destino)


def excluir(entrada, destino, paginas):
    with abrir_pdf(entrada) as doc:
        if isinstance(paginas, str):
            paginas = ler_paginas(paginas, doc.page_count)
        if not paginas:
            raise ErroAmigavel("Marque as páginas que quer tirar.")
        if len(set(paginas)) >= doc.page_count:
            raise ErroAmigavel("Assim não sobraria nenhuma página. Deixe pelo menos uma.")
        doc.delete_pages(sorted(set(paginas)))
        return salvar(doc, destino)


def reordenar(entrada, destino, ordem):
    """`ordem`: a nova sequência de páginas (a partir de 0). Precisa ter todas, cada uma uma vez."""
    with abrir_pdf(entrada) as doc:
        if sorted(ordem) != list(range(doc.page_count)):
            raise ErroAmigavel("A nova ordem precisa ter todas as páginas, cada uma uma vez só.")
        doc.select(list(ordem))
        return salvar(doc, destino)


def girar(entrada, destino, graus=90, paginas=None):
    """Gira `paginas` (todas, se None) em `graus` no sentido do relógio. `graus` pode ser um dicionário
    {página: graus} para girar cada página de um jeito."""
    with abrir_pdf(entrada) as doc:
        if isinstance(graus, dict):
            giros = {int(p): int(g) for p, g in graus.items()}
        else:
            alvo = range(doc.page_count) if paginas is None else paginas
            giros = {p: int(graus) for p in alvo}
        if not any(g % 360 for g in giros.values()):
            raise ErroAmigavel("Nenhuma página foi girada. Clique nas setas das páginas que quer girar.")
        for pagina, g in giros.items():
            if not 0 <= pagina < doc.page_count:
                raise ErroAmigavel(f"O PDF não tem a página {pagina + 1}.")
            if g % 90:
                raise ErroAmigavel("Só dá para girar de 90 em 90 graus.")
            atual = doc[pagina]
            atual.set_rotation((atual.rotation + g) % 360)
        return salvar(doc, destino)


# ---------------------------------------------------------------- otimizar

NIVEIS_DE_COMPRESSAO = {
    # nível: (imagens acima deste DPI são reduzidas, para este DPI, qualidade JPEG)
    "leve": (220, 200, 85),
    "recomendada": (160, 130, 70),
    "forte": (110, 90, 50),
}


def comprimir(entrada, destino, nivel="recomendada", avisar=_nada):
    """Reduz as imagens e limpa o PDF. Devolve (destino, tamanho_antes, tamanho_depois); se não ficar menor,
    o destino não é criado e volta None no lugar dele."""
    if nivel not in NIVEIS_DE_COMPRESSAO:
        raise ErroAmigavel("Escolha o nível de compressão.")
    limite, alvo, qualidade = NIVEIS_DE_COMPRESSAO[nivel]
    antes = Path(entrada).stat().st_size
    destino = Path(destino)
    with abrir_pdf(entrada) as doc:
        avisar(0.1, "Diminuindo as imagens")
        try:
            doc.rewrite_images(dpi_threshold=limite, dpi_target=alvo, quality=qualidade)
        except Exception:
            pass  # imagem num formato que o PyMuPDF não regrava: segue só com a limpeza
        avisar(0.7, "Gravando")
        destino.parent.mkdir(parents=True, exist_ok=True)
        doc.save(destino, garbage=4, deflate=True, deflate_images=True, deflate_fonts=True, clean=True,
                 use_objstms=1)
    depois = destino.stat().st_size
    if depois >= antes:
        destino.unlink()
        return None, antes, antes
    return destino, antes, depois


# ---------------------------------------------------------------- editar

POSICOES = {
    # posição: (horizontal, vertical) -> esquerda/centro/direita, topo/meio/rodapé
    "rodape-centro": ("centro", "rodape"), "rodape-direita": ("direita", "rodape"),
    "rodape-esquerda": ("esquerda", "rodape"), "topo-centro": ("centro", "topo"),
    "topo-direita": ("direita", "topo"), "topo-esquerda": ("esquerda", "topo"),
    "centro": ("centro", "meio"),
}
CORES = {"cinza": (0.45, 0.45, 0.45), "preto": (0, 0, 0), "vermelho": (0.8, 0.1, 0.1), "azul": (0.1, 0.25, 0.7)}


def _escrever(pagina, texto, tamanho, posicao, cor, opacidade=1.0, angulo=0, margem=28):
    """Escreve `texto` na página. Páginas giradas são "desviradas" antes, sem mudar como aparecem, para o texto
    sair sempre em pé."""
    if pagina.rotation:
        pagina.remove_rotation()
    area = pagina.rect
    largura = pymupdf.get_text_length(texto, fontname="helv", fontsize=tamanho)
    horizontal, vertical = POSICOES[posicao]
    x = {"esquerda": area.x0 + margem, "centro": area.x0 + (area.width - largura) / 2,
         "direita": area.x1 - margem - largura}[horizontal]
    y = {"topo": area.y0 + margem + tamanho * 0.8, "meio": area.y0 + area.height / 2 + tamanho * 0.35,
         "rodape": area.y1 - margem}[vertical]
    morph = None
    if angulo:
        centro = pymupdf.Point(x + largura / 2, y - tamanho * 0.35)
        morph = (centro, pymupdf.Matrix(angulo))  # sobe da esquerda para a direita
    pagina.insert_text((x, y), texto, fontname="helv", fontsize=tamanho, color=cor, fill_opacity=opacidade,
                       morph=morph, overlay=True)


def marca_dagua(entrada, destino, texto, tamanho=60, opacidade=0.25, cor="cinza", posicao="diagonal",
                avisar=_nada):
    texto = (texto or "").strip()
    if not texto:
        raise ErroAmigavel("Escreva o texto da marca d'água.")
    tamanho, opacidade = float(tamanho), float(opacidade)
    with abrir_pdf(entrada) as doc:
        for i, pagina in enumerate(doc):
            avisar(i / doc.page_count, f"Página {i + 1} de {doc.page_count}")
            area = pagina.rect
            tam = tamanho
            if posicao == "diagonal":
                # não deixa a diagonal sair da folha: diminui a letra se o texto for comprido
                diagonal = (area.width ** 2 + area.height ** 2) ** 0.5 * 0.8
                largura = pymupdf.get_text_length(texto, fontname="helv", fontsize=tam)
                if largura > diagonal:
                    tam = tam * diagonal / largura
                angulo = 45 if area.height >= area.width else 30
                _escrever(pagina, texto, tam, "centro", CORES.get(cor, CORES["cinza"]), opacidade, angulo)
            else:
                _escrever(pagina, texto, tam, posicao, CORES.get(cor, CORES["cinza"]), opacidade)
        return salvar(doc, destino)


FORMATOS_DE_NUMERO = {"numero": "{n}", "n-de-total": "{n} de {total}", "pagina-n-de-total": "Página {n} de {total}"}


def numerar(entrada, destino, posicao="rodape-centro", formato="numero", inicio=1, pular_primeira=False,
            tamanho=11, avisar=_nada):
    if posicao not in POSICOES:
        raise ErroAmigavel("Escolha onde o número vai ficar.")
    modelo = FORMATOS_DE_NUMERO.get(formato, "{n}")
    inicio = int(inicio or 1)
    with abrir_pdf(entrada) as doc:
        numeradas = [p for p in range(doc.page_count) if not (pular_primeira and p == 0)]
        total = inicio + len(numeradas) - 1
        for n, indice in enumerate(numeradas, start=inicio):
            avisar(indice / doc.page_count, f"Página {indice + 1} de {doc.page_count}")
            _escrever(doc[indice], modelo.format(n=n, total=total), float(tamanho), posicao, CORES["preto"])
        return salvar(doc, destino)


# ---------------------------------------------------------------- segurança


def proteger(entrada, destino, senha):
    if not senha:
        raise ErroAmigavel("Escreva a senha que vai proteger o PDF.")
    if len(senha) < 4:
        raise ErroAmigavel("Use uma senha com pelo menos 4 caracteres.")
    try:
        pdf = pikepdf.open(entrada)
    except pikepdf.PasswordError:
        raise ErroAmigavel("Este PDF já tem senha. Para trocar, tire a senha antes e depois ponha a nova.") from None
    except Exception:
        raise ErroAmigavel(DANIFICADO.format(nome=Path(entrada).name)) from None
    with pdf:
        Path(destino).parent.mkdir(parents=True, exist_ok=True)
        pdf.save(destino, encryption=pikepdf.Encryption(user=senha, owner=senha, R=6))
    return Path(destino)


def desproteger(entrada, destino, senha=""):
    try:
        pdf = pikepdf.open(entrada, password=senha or "")
    except pikepdf.PasswordError:
        if senha:
            raise ErroAmigavel("A senha não confere. Confira maiúsculas e minúsculas e tente de novo.") from None
        raise ErroAmigavel("Este PDF pede senha para abrir. Escreva a senha dele.") from None
    except Exception:
        raise ErroAmigavel(DANIFICADO.format(nome=Path(entrada).name)) from None
    with pdf:
        if not pdf.is_encrypted:
            raise ErroAmigavel(f"“{Path(entrada).name}” não tem senha: não há nada para tirar.")
        Path(destino).parent.mkdir(parents=True, exist_ok=True)
        pdf.save(destino)
    return Path(destino)


# ---------------------------------------------------------------- miniaturas


def miniatura(caminho, pagina, largura=180):
    """PNG pequeno da página, para a tela mostrar e a pessoa escolher, girar ou arrastar."""
    with abrir_pdf(caminho) as doc:
        if not 0 <= pagina < doc.page_count:
            raise ErroAmigavel("Essa página não existe.")
        folha = doc[pagina]
        escala = largura / max(folha.rect.width, 1)
        return folha.get_pixmap(matrix=pymupdf.Matrix(escala, escala), alpha=False).tobytes("png")
