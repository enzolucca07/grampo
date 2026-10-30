# Grampo

**Seus PDFs, resolvidos aqui mesmo.** O Grampo junta, divide, comprime, converte e põe senha em PDFs, tudo no
próprio computador. Ele não usa internet: nenhum arquivo sai da máquina.

Por que "Grampo"? É o objeto mais simples de escritório para juntar papéis. É curto, é bem nosso e diz o que o
programa faz: arrumar a papelada sem complicação.

## O que ele faz

Cada ferramenta é um cartão na tela inicial:

| Grupo | Ferramentas |
|---|---|
| Organizar | Juntar PDFs, Dividir PDF, Extrair páginas, Excluir páginas, Reordenar páginas, Girar páginas |
| Diminuir e editar | Comprimir PDF, Marca d'água, Numerar páginas |
| Converter para PDF | Word, Excel, PowerPoint, Imagens (JPG, PNG…) e Texto (.txt) |
| Converter do PDF | PDF para Word, PDF para Excel, PDF para PowerPoint, PDF para imagem (JPG ou PNG), PDF para texto, Extrair imagens |
| Senha | Pôr senha, Tirar senha |

## Como usar

1. Abra o Grampo (atalho no menu Iniciar ou na Área de Trabalho).
2. Clique na ferramenta que você quer. Se não achar, escreva na busca ("juntar", "senha", "Word"…).
3. Arraste os arquivos para a tela ou clique em **Escolher no computador**.
4. Escolha as opções do lado direito e clique no botão verde.
5. Pronto: o arquivo novo fica na pasta **Downloads**. Clique em **Abrir** ou em **Mostrar na pasta**.

Algumas coisas que é bom saber:

- **O original nunca muda.** O Grampo sempre grava um arquivo novo, com o nome dizendo o que foi feito, por
  exemplo `contrato (com senha).pdf`. Se já existir um arquivo com esse nome, ele grava `contrato (com senha) (2).pdf`.
- **Dividir**, **PDF para imagem** e **Extrair imagens** criam vários arquivos. Eles ficam juntos numa pasta nova dentro da Downloads.
- Para salvar em outro lugar, clique em **Salvando em Downloads**, no alto da tela.
- O botão de lua ou de sol, no alto da tela, troca entre o tema claro e o escuro.
- **Excluir**, **Extrair**, **Girar** e **Reordenar** mostram as páginas: é só clicar, girar com as setas ou arrastar.
- **PDF para Word** funciona bem com PDFs que têm texto. PDF escaneado (foto de papel) vira um Word com as
  páginas como imagem.
- **PDF para Excel** procura as tabelas de cada página (com ou sem linhas de grade) e põe cada uma numa aba. Os
  valores em reais ("1.234,56", "(900,00)", "12,5%") já viram números, prontos para somar. Página só com texto
  corrido entra linha por linha.
- **PDF para PowerPoint** põe cada página num slide, como imagem, do jeito que está no PDF.
- **PDF para texto** e **PDF para Excel** precisam de PDF com texto. PDF escaneado (foto do papel) não tem texto, e a
  tela avisa.
- **Word, Excel e PowerPoint para PDF** usam o Microsoft Office instalado no computador. Sem o Office, o Grampo
  usa o LibreOffice (gratuito). Sem nenhum dos dois, o cartão mostra "Precisa do Office" e a tela explica o que
  instalar.

## Instalar (computadores do escritório)

Baixe o `Grampo-<versão>.exe` na página **Releases** do repositório no GitHub e rode. Ele instala só para quem
está usando o Windows, sem pedir senha de administrador, cria o atalho no menu Iniciar e já abre o programa. Não
precisa de Python nem de internet depois de instalado.

Para instalar sem perguntas: `Grampo-1.1.0.exe /SILENT`.

## Para a TI

### Instalar para desenvolver

Precisa do Python 3.12.

```
git clone https://github.com/enzolucca07/grampo.git
cd grampo
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Abrir

- Duplo clique em `iniciar.bat` (janela própria), ou
- `.venv\Scripts\python.exe app.py --navegador` (no navegador), ou
- `.venv\Scripts\python.exe app.py --sem-janela --porta 5110` (só o servidor, em http://127.0.0.1:5110).

### Testes

```
.venv\Scripts\python.exe -m pytest
```

Os testes criam os próprios arquivos de exemplo. Os testes marcados com `office` usam o Word, o Excel e o
PowerPoint de verdade (ou o LibreOffice); sem eles, são pulados. Para rodar sem o Office:
`pytest -m "not office"`.

Para ter os arquivos de exemplo numa pasta e testar pela tela:
`.venv\Scripts\python.exe exemplos\gerar_exemplos.py` (grava em `exemplos\arquivos`).

### Montar o instalador

Precisa do Inno Setup 6. Suba a versão em `grampo/__init__.py` e rode:

```
.venv\Scripts\python.exe instalador\montar.py
```

O resultado é `dist\Grampo-<versão>.exe`. A montagem intermediária fica em `%TEMP%\Grampo-montagem`, fora do
OneDrive.

### Como funciona por dentro

- `app.py`: abre a janela (pywebview) e um servidor Flask que só atende no próprio computador (127.0.0.1, porta
  sorteada). A API só aceita pedidos da tela do Grampo (cabeçalho com chave sorteada a cada abertura) e só abre
  arquivos que o próprio Grampo gravou.
- `grampo/operacoes.py`: juntar, dividir, girar, comprimir, marca d'água, numerar, senha (PyMuPDF e pikepdf).
- `grampo/conversao.py`: Office para PDF (COM do Office ou LibreOffice), imagens e texto para PDF; PDF para imagem,
  Word (pdf2docx), Excel (tabelas pela grade ou pelo alinhamento do texto, com openpyxl), PowerPoint (python-pptx) e
  texto; extração das imagens.
- `grampo/ferramentas.py`: o catálogo dos cartões e das opções. A tela monta os formulários a partir dele.
- `grampo/saida.py`: a pasta Downloads de verdade, a pasta escolhida e os nomes sem sobrescrever.
- `templates/` e `static/`: a tela.

Os arquivos que a tela manda ficam numa pasta temporária (`%TEMP%\Grampo-envios-…`), apagada quando o programa
fecha. A configuração (pasta escolhida) fica em `%LOCALAPPDATA%\Grampo\configuracao.json`.

**Impressora "Somente Texto".** O Word e o Excel montam as páginas com as medidas da impressora padrão. Quando ela
é uma impressora "Somente Texto" (como a do Domínio/Domsis), a letra sai enorme no PDF. Por isso, só durante a
conversão, o Grampo põe a "Microsoft Print to PDF" como padrão e depois devolve a de antes. Se o programa fechar no
meio, ele devolve na próxima vez que abrir.

### Licença

AGPL-3.0 (arquivo `LICENSE`), a mesma do PyMuPDF, que o Grampo usa. Pode ser usado e alterado à vontade; quem
distribuir uma versão alterada precisa distribuir o código junto.
