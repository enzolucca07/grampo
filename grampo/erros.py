"""Erros que aparecem na tela: a mensagem já vem escrita para quem não é da área de TI."""


class ErroAmigavel(Exception):
    """Algo deu errado de um jeito que a pessoa consegue entender (e, quase sempre, resolver)."""


PROTEGIDO = ("Este PDF está protegido com senha. Use primeiro a ferramenta “Tirar senha” "
             "e depois tente de novo com o arquivo sem senha.")
DANIFICADO = "Não consegui abrir “{nome}”. Ele não parece ser um PDF, ou está danificado."
