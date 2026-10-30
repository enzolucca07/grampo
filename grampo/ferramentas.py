"""O catálogo das ferramentas (cada uma vira um cartão na tela inicial) e quem executa cada uma.

A tela monta o formulário de opções a partir de OPCOES, então uma ferramenta nova só precisa entrar aqui.
Tipos de opção: escolha, texto, senha, numero, marcar, faixa. "se" mostra a opção só quando outra tem certo valor.
"""

from pathlib import Path

from . import conversao, operacoes
from .erros import ErroAmigavel
from .saida import caminho_livre, limpar_nome

PDF = [".pdf"]
GRUPOS = [
    ("organizar", "Organizar"),
    ("editar", "Diminuir e editar"),
    ("para_pdf", "Converter para PDF"),
    ("do_pdf", "Converter do PDF"),
    ("seguranca", "Senha"),
]

FERRAMENTAS = [
    {"id": "juntar", "grupo": "organizar", "titulo": "Juntar PDFs",
     "descricao": "Vários PDFs viram um só, na ordem que você escolher.", "aceita": PDF, "varios": True, "minimo": 2},
    {"id": "dividir", "grupo": "organizar", "titulo": "Dividir PDF",
     "descricao": "Separa um PDF em vários arquivos menores.", "aceita": PDF,
     "opcoes": [
         {"nome": "modo", "tipo": "escolha", "rotulo": "Como dividir", "padrao": "cada",
          "valores": [["cada", "Uma página por arquivo"], ["a_cada", "De tantas em tantas páginas"],
                      ["intervalos", "Do meu jeito"]]},
         {"nome": "a_cada", "tipo": "numero", "rotulo": "Páginas em cada arquivo", "padrao": 2, "minimo": 1,
          "se": {"modo": "a_cada"}},
         {"nome": "intervalos", "tipo": "texto", "rotulo": "Pedaços", "padrao": "",
          "exemplo": "1-3, 4-6, 7", "ajuda": "Cada pedaço separado por vírgula vira um arquivo.",
          "se": {"modo": "intervalos"}},
     ]},
    {"id": "extrair", "grupo": "organizar", "titulo": "Extrair páginas",
     "descricao": "Copia só as páginas que você quer para um PDF novo.", "aceita": PDF, "paginas": "marcar",
     "opcoes": [{"nome": "paginas", "tipo": "texto", "rotulo": "Páginas", "exemplo": "1, 3-5",
                 "ajuda": "Clique nas páginas ou escreva os números."}]},
    {"id": "excluir", "grupo": "organizar", "titulo": "Excluir páginas",
     "descricao": "Tira as páginas que sobram, como folhas em branco.", "aceita": PDF, "paginas": "marcar",
     "opcoes": [{"nome": "paginas", "tipo": "texto", "rotulo": "Páginas para tirar", "exemplo": "2, 5-6",
                 "ajuda": "Clique nas páginas ou escreva os números."}]},
    {"id": "reordenar", "grupo": "organizar", "titulo": "Reordenar páginas",
     "descricao": "Arraste as páginas para colocar na ordem certa.", "aceita": PDF, "paginas": "ordenar"},
    {"id": "girar", "grupo": "organizar", "titulo": "Girar páginas",
     "descricao": "Desvira páginas deitadas ou de cabeça para baixo.", "aceita": PDF, "paginas": "girar"},
    {"id": "comprimir", "grupo": "editar", "titulo": "Comprimir PDF",
     "descricao": "Deixa o PDF mais leve para mandar por e-mail ou subir em site.", "aceita": PDF, "varios": True,
     "opcoes": [{"nome": "nivel", "tipo": "escolha", "rotulo": "Quanto diminuir", "padrao": "recomendada",
                 "valores": [["leve", "Pouco (qualidade máxima)"], ["recomendada", "Recomendado"],
                             ["forte", "Bastante (imagens mais simples)"]]}]},
    {"id": "marca", "grupo": "editar", "titulo": "Marca d'água",
     "descricao": "Escreve um texto por cima das páginas, como CÓPIA ou CONFIDENCIAL.", "aceita": PDF,
     "varios": True,
     "opcoes": [
         {"nome": "texto", "tipo": "texto", "rotulo": "Texto", "padrao": "CÓPIA"},
         {"nome": "posicao", "tipo": "escolha", "rotulo": "Onde", "padrao": "diagonal",
          "valores": [["diagonal", "Atravessado no meio"], ["centro", "No meio"], ["topo-centro", "Em cima"],
                      ["rodape-centro", "Embaixo"]]},
         {"nome": "cor", "tipo": "escolha", "rotulo": "Cor", "padrao": "cinza",
          "valores": [["cinza", "Cinza"], ["vermelho", "Vermelho"], ["azul", "Azul"], ["preto", "Preto"]]},
         {"nome": "tamanho", "tipo": "faixa", "rotulo": "Tamanho da letra", "padrao": 60, "minimo": 16,
          "maximo": 120, "passo": 2},
         {"nome": "opacidade", "tipo": "faixa", "rotulo": "Transparência", "padrao": 0.25, "minimo": 0.1,
          "maximo": 1, "passo": 0.05, "porcento": True},
     ]},
    {"id": "numerar", "grupo": "editar", "titulo": "Numerar páginas",
     "descricao": "Põe o número em cada página, onde você escolher.", "aceita": PDF, "varios": True,
     "opcoes": [
         {"nome": "posicao", "tipo": "escolha", "rotulo": "Onde", "padrao": "rodape-centro",
          "valores": [["rodape-esquerda", "Embaixo, à esquerda"], ["rodape-centro", "Embaixo, no meio"],
                      ["rodape-direita", "Embaixo, à direita"], ["topo-esquerda", "Em cima, à esquerda"],
                      ["topo-centro", "Em cima, no meio"], ["topo-direita", "Em cima, à direita"]]},
         {"nome": "formato", "tipo": "escolha", "rotulo": "Como escrever", "padrao": "numero",
          "valores": [["numero", "1"], ["n-de-total", "1 de 10"], ["pagina-n-de-total", "Página 1 de 10"]]},
         {"nome": "inicio", "tipo": "numero", "rotulo": "Começar do número", "padrao": 1, "minimo": 1},
         {"nome": "pular_primeira", "tipo": "marcar", "rotulo": "Não numerar a primeira página (capa)",
          "padrao": False},
     ]},
    {"id": "word_pdf", "grupo": "para_pdf", "titulo": "Word para PDF",
     "descricao": "Documentos do Word (.docx, .doc, .rtf, .odt) viram PDF.", "precisa": "word",
     "aceita": sorted(conversao.EXTENSOES_WORD), "varios": True},
    {"id": "excel_pdf", "grupo": "para_pdf", "titulo": "Excel para PDF",
     "descricao": "Planilhas (.xlsx, .xls, .csv, .ods) viram PDF.", "precisa": "excel",
     "aceita": sorted(conversao.EXTENSOES_EXCEL), "varios": True},
    {"id": "powerpoint_pdf", "grupo": "para_pdf", "titulo": "PowerPoint para PDF",
     "descricao": "Apresentações (.pptx, .ppt, .odp) viram PDF.", "precisa": "powerpoint",
     "aceita": sorted(conversao.EXTENSOES_POWERPOINT), "varios": True},
    {"id": "imagem_pdf", "grupo": "para_pdf", "titulo": "Imagens para PDF",
     "descricao": "Fotos e imagens (JPG, PNG...) viram um PDF, uma por página.",
     "aceita": sorted(conversao.EXTENSOES_IMAGEM), "varios": True,
     "opcoes": [
         {"nome": "tamanho", "tipo": "escolha", "rotulo": "Tamanho da página", "padrao": "a4",
          "valores": [["a4", "Folha A4"], ["imagem", "Do tamanho da imagem"]]},
         {"nome": "margem", "tipo": "marcar", "rotulo": "Deixar uma margem branca", "padrao": True,
          "se": {"tamanho": "a4"}},
         {"nome": "separados", "tipo": "marcar", "rotulo": "Um PDF para cada imagem", "padrao": False},
     ]},
    {"id": "texto_pdf", "grupo": "para_pdf", "titulo": "Texto para PDF",
     "descricao": "Arquivos de texto (.txt) viram PDF.", "aceita": sorted(conversao.EXTENSOES_TEXTO),
     "varios": True},
    {"id": "pdf_word", "grupo": "do_pdf", "titulo": "PDF para Word",
     "descricao": "Transforma o PDF num Word para editar. Funciona melhor em PDFs com texto (não escaneados).",
     "aceita": PDF, "varios": True},
    {"id": "pdf_excel", "grupo": "do_pdf", "titulo": "PDF para Excel",
     "descricao": "As tabelas do PDF viram uma planilha, com os valores prontos para somar.", "aceita": PDF,
     "varios": True},
    {"id": "pdf_powerpoint", "grupo": "do_pdf", "titulo": "PDF para PowerPoint",
     "descricao": "Cada página vira um slide, do jeito que está no PDF.", "aceita": PDF, "varios": True},
    {"id": "pdf_jpg", "grupo": "do_pdf", "titulo": "PDF para imagem",
     "descricao": "Cada página vira uma imagem JPG ou PNG.", "aceita": PDF, "varios": True,
     "opcoes": [{"nome": "formato", "tipo": "escolha", "rotulo": "Formato", "padrao": "jpg",
                 "valores": [["jpg", "JPG (mais leve)"], ["png", "PNG (mais nítido)"]]},
                {"nome": "dpi", "tipo": "escolha", "rotulo": "Qualidade", "padrao": "150",
                 "valores": [["100", "Normal (arquivo leve)"], ["150", "Boa"], ["300", "Alta (para imprimir)"]]}]},
    {"id": "pdf_texto", "grupo": "do_pdf", "titulo": "PDF para texto",
     "descricao": "Tira todo o texto do PDF para um arquivo .txt, para copiar e colar.", "aceita": PDF,
     "varios": True},
    {"id": "extrair_imagens", "grupo": "do_pdf", "titulo": "Extrair imagens",
     "descricao": "Salva as fotos e figuras que estão dentro do PDF, no tamanho original.", "aceita": PDF,
     "varios": True},
    {"id": "proteger", "grupo": "seguranca", "titulo": "Pôr senha",
     "descricao": "Só abre o PDF quem souber a senha.", "aceita": PDF, "varios": True,
     "opcoes": [{"nome": "senha", "tipo": "senha", "rotulo": "Senha"},
                {"nome": "confirmar", "tipo": "senha", "rotulo": "Repita a senha"}]},
    {"id": "desproteger", "grupo": "seguranca", "titulo": "Tirar senha",
     "descricao": "Grava uma cópia do PDF que abre sem pedir senha.", "aceita": PDF, "varios": True,
     "opcoes": [{"nome": "senha", "tipo": "senha", "rotulo": "Senha atual do PDF",
                 "ajuda": "Se o PDF abre sem senha e só bloqueia imprimir ou copiar, deixe em branco."}]},
]
POR_ID = {f["id"]: f for f in FERRAMENTAS}

SUFIXO = {
    "juntar": "juntado", "dividir": "dividido", "extrair": "páginas extraídas", "excluir": "páginas excluídas",
    "reordenar": "reordenado", "girar": "girado", "comprimir": "comprimido", "marca": "com marca d'água",
    "numerar": "numerado", "word_pdf": "convertido", "excel_pdf": "convertido", "powerpoint_pdf": "convertido",
    "imagem_pdf": "convertido", "texto_pdf": "convertido", "pdf_jpg": "imagens", "pdf_word": "convertido", "pdf_excel": "convertido",
    "pdf_powerpoint": "convertido", "pdf_texto": "texto", "extrair_imagens": "imagens extraídas",
    "proteger": "com senha", "desproteger": "sem senha",
}


def _tamanho(bytes_):
    for unidade in ("bytes", "KB", "MB", "GB"):
        if bytes_ < 1024 or unidade == "GB":
            return f"{bytes_:.0f} {unidade}" if unidade == "bytes" else f"{bytes_:.1f} {unidade}".replace(".", ",")
        bytes_ /= 1024


def executar(ferramenta, arquivos, opcoes, pasta, avisar=operacoes._nada):
    """Roda a ferramenta. `arquivos`: lista de (caminho temporário, nome original), na ordem da tela.

    Devolve {"arquivos": [...], "mensagem": "..."}; os arquivos já estão em `pasta`, com o nome dizendo o que foi
    feito e sem sobrescrever nada.
    """
    if ferramenta not in POR_ID:
        raise ErroAmigavel("Ferramenta desconhecida.")
    definicao = POR_ID[ferramenta]
    opcoes = dict(opcoes or {})
    if not arquivos:
        raise ErroAmigavel("Escolha um arquivo primeiro.")
    if len(arquivos) < definicao.get("minimo", 1):
        raise ErroAmigavel(f"Escolha pelo menos {definicao['minimo']} arquivos.")
    if not definicao.get("varios") and len(arquivos) > 1:
        raise ErroAmigavel("Esta ferramenta trabalha com um arquivo de cada vez.")
    for _, nome in arquivos:
        if Path(nome).suffix.lower() not in definicao["aceita"]:
            raise ErroAmigavel(f"“{nome}” não serve aqui. Esta ferramenta aceita: "
                               f"{', '.join(e.lstrip('.').upper() for e in definicao['aceita'])}.")
    pasta = Path(pasta)
    pasta.mkdir(parents=True, exist_ok=True)
    sufixo = SUFIXO[ferramenta]

    def nome_para(nome_original, extensao=".pdf"):
        return caminho_livre(pasta, f"{limpar_nome(Path(nome_original).stem)} ({sufixo}){extensao}")

    if ferramenta == "proteger" and opcoes.get("senha") != opcoes.get("confirmar"):
        raise ErroAmigavel("As duas senhas não estão iguais. Escreva de novo.")

    # ferramentas que juntam tudo num arquivo só
    if ferramenta == "juntar":
        destino = operacoes.juntar([c for c, _ in arquivos], nome_para(arquivos[0][1]), avisar)
        return {"arquivos": [str(destino)], "mensagem": f"{len(arquivos)} PDFs juntados em um só."}
    if ferramenta == "imagem_pdf" and not opcoes.get("separados") and len(arquivos) > 1:
        destino = operacoes_imagens(arquivos, nome_para(arquivos[0][1]), opcoes, avisar)
        return {"arquivos": [str(destino)], "mensagem": f"{len(arquivos)} imagens juntadas num PDF."}

    saidas, observacoes = [], []
    for i, (caminho, nome) in enumerate(arquivos):
        def avisar_este(fracao, texto="", i=i):
            prefixo = f"{nome}: " if len(arquivos) > 1 else ""
            avisar((i + fracao) / len(arquivos), prefixo + texto)

        avisar_este(0, "Começando")
        base = limpar_nome(Path(nome).stem)
        if ferramenta == "dividir":
            subpasta = caminho_livre(pasta, f"{base} ({sufixo})")
            saidas += operacoes.dividir(caminho, subpasta, base, opcoes.get("modo", "cada"), opcoes.get("a_cada", 1),
                                        opcoes.get("intervalos", ""), avisar_este)
        elif ferramenta == "extrair":
            saidas.append(operacoes.extrair(caminho, nome_para(nome), opcoes.get("paginas", "")))
        elif ferramenta == "excluir":
            saidas.append(operacoes.excluir(caminho, nome_para(nome), opcoes.get("paginas", "")))
        elif ferramenta == "reordenar":
            ordem = opcoes.get("ordem")
            if not ordem:
                raise ErroAmigavel("Arraste as páginas para a nova ordem.")
            if list(ordem) == sorted(ordem):
                raise ErroAmigavel("As páginas continuam na mesma ordem. Arraste alguma para outro lugar.")
            saidas.append(operacoes.reordenar(caminho, nome_para(nome), [int(p) for p in ordem]))
        elif ferramenta == "girar":
            saidas.append(operacoes.girar(caminho, nome_para(nome), opcoes.get("giros") or {}))
        elif ferramenta == "comprimir":
            destino, antes, depois = operacoes.comprimir(caminho, nome_para(nome), opcoes.get("nivel", "recomendada"),
                                                         avisar_este)
            if destino:
                saidas.append(destino)
                economia = round(100 * (antes - depois) / antes)
                observacoes.append(f"{nome}: de {_tamanho(antes)} para {_tamanho(depois)} ({economia}% menor).")
            else:
                observacoes.append(f"{nome}: já estava no menor tamanho ({_tamanho(antes)}); não criei cópia.")
        elif ferramenta == "marca":
            saidas.append(operacoes.marca_dagua(caminho, nome_para(nome), opcoes.get("texto", ""),
                                                opcoes.get("tamanho", 60), opcoes.get("opacidade", 0.25),
                                                opcoes.get("cor", "cinza"), opcoes.get("posicao", "diagonal"),
                                                avisar_este))
        elif ferramenta == "numerar":
            saidas.append(operacoes.numerar(caminho, nome_para(nome), opcoes.get("posicao", "rodape-centro"),
                                            opcoes.get("formato", "numero"), opcoes.get("inicio", 1),
                                            bool(opcoes.get("pular_primeira")), avisar=avisar_este))
        elif ferramenta in ("word_pdf", "excel_pdf", "powerpoint_pdf"):
            avisar_este(0.1, "Abrindo no " + conversao.NOME_DO_PROGRAMA[conversao.tipo_office(nome) or "word"])
            saidas.append(conversao.office_para_pdf(caminho, nome_para(nome)))
        elif ferramenta == "imagem_pdf":
            saidas.append(operacoes_imagens([(caminho, nome)], nome_para(nome), opcoes, avisar_este))
        elif ferramenta == "texto_pdf":
            saidas.append(conversao.texto_para_pdf(caminho, nome_para(nome)))
        elif ferramenta == "pdf_jpg":
            total = operacoes.contar_paginas(caminho)
            destino = pasta if total == 1 else caminho_livre(pasta, f"{base} ({sufixo})")
            formato = "png" if opcoes.get("formato") == "png" else "jpg"
            nome_base = caminho_livre(pasta, f"{base} (imagem).{formato}").stem if total == 1 else base
            saidas += conversao.pdf_para_jpg(caminho, destino, nome_base, int(opcoes.get("dpi", 150)), avisar_este,
                                             formato)
        elif ferramenta == "pdf_excel":
            destino, tabelas = conversao.pdf_para_excel(caminho, nome_para(nome, ".xlsx"), avisar_este)
            saidas.append(destino)
            observacoes.append(f"{nome}: {tabelas} tabela{'s' if tabelas != 1 else ''} encontrada"
                               f"{'s' if tabelas != 1 else ''}." if tabelas else
                               f"{nome}: não achei tabelas com linhas desenhadas, então o texto foi para a planilha "
                               "linha por linha.")
        elif ferramenta == "pdf_powerpoint":
            saidas.append(conversao.pdf_para_powerpoint(caminho, nome_para(nome, ".pptx"), avisar=avisar_este))
        elif ferramenta == "pdf_texto":
            saidas.append(conversao.pdf_para_texto(caminho, nome_para(nome, ".txt"), avisar_este))
        elif ferramenta == "extrair_imagens":
            subpasta = caminho_livre(pasta, f"{base} ({sufixo})")
            saidas += conversao.extrair_imagens(caminho, subpasta, base, avisar_este)
        elif ferramenta == "pdf_word":
            if not conversao.tem_texto(caminho):
                observacoes.append(f"{nome}: parece escaneado (não tem texto), então o Word vai ter as páginas "
                                   "como imagem.")
            saidas.append(conversao.pdf_para_word(caminho, nome_para(nome, ".docx"), avisar_este))
        elif ferramenta == "proteger":
            saidas.append(operacoes.proteger(caminho, nome_para(nome), opcoes.get("senha", "")))
        elif ferramenta == "desproteger":
            saidas.append(operacoes.desproteger(caminho, nome_para(nome), opcoes.get("senha", "")))
    avisar(1, "Pronto")
    mensagem = " ".join(observacoes) or (
        "O arquivo foi salvo." if len(saidas) == 1 else f"{len(saidas)} arquivos foram salvos.")
    return {"arquivos": [str(s) for s in saidas], "mensagem": mensagem}


def operacoes_imagens(arquivos, destino, opcoes, avisar):
    return conversao.imagens_para_pdf([c for c, _ in arquivos], destino, opcoes.get("tamanho", "a4"),
                                      bool(opcoes.get("margem", True)), avisar)

