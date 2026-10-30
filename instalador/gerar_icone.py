"""Desenha o ícone do Grampo (folha verde com o grampo dourado) em grampo.ico, nos tamanhos que o Windows usa.

  .venv\\Scripts\\python.exe instalador\\gerar_icone.py
"""

from pathlib import Path

from PIL import Image, ImageDraw

VERDE, DOURADO, LINHA = (29, 107, 95, 255), (231, 176, 79, 255), (255, 255, 255, 140)


def desenhar(lado=256):
    escala = lado / 40  # o desenho original (static/grampo.svg) é de 40x40
    s = lambda v: round(v * escala)  # noqa: E731
    imagem = Image.new("RGBA", (lado, lado), (0, 0, 0, 0))
    d = ImageDraw.Draw(imagem)
    d.rounded_rectangle([0, 0, lado - 1, lado - 1], radius=s(11), fill=VERDE)
    for y, fim in ((15, 28), (21, 28), (27, 22)):
        d.line([(s(12), s(y)), (s(fim), s(y))], fill=LINHA, width=max(1, s(2.4)))
    grossura = max(2, s(3.6))
    d.line([(s(9), s(13)), (s(9), s(8.5))], fill=DOURADO, width=grossura)
    d.line([(s(31), s(13)), (s(31), s(8.5))], fill=DOURADO, width=grossura)
    d.line([(s(10.5), s(7)), (s(29.5), s(7))], fill=DOURADO, width=grossura)
    d.arc([s(9) - grossura // 2, s(7) - grossura // 2, s(12) + grossura // 2, s(10) + grossura // 2], 180, 270,
          fill=DOURADO, width=grossura)
    d.arc([s(28) - grossura // 2, s(7) - grossura // 2, s(31) + grossura // 2, s(10) + grossura // 2], 270, 360,
          fill=DOURADO, width=grossura)
    return imagem


if __name__ == "__main__":
    destino = Path(__file__).resolve().parent / "grampo.ico"
    desenhar(256).save(destino, sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("Ícone em", destino)
