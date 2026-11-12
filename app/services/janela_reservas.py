
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo


FUSO_MESC = ZoneInfo("America/Sao_Paulo")


def obter_data_atual():
    """Retorna a data atual no fuso horário do MESC."""
    return datetime.now(FUSO_MESC).date()


def obter_janela_atual(data_atual=None):
    """
    Retorna a terça-feira e o domingo da janela atual.

    Antes de terça-feira, não existe janela aberta.
    """
    if data_atual is None:
        data_atual = obter_data_atual()

    # Segunda-feira = 0; terça-feira = 1; domingo = 6.
    if data_atual.weekday() == 0:
        return None

    dias_desde_terca = data_atual.weekday() - 1

    inicio = data_atual - timedelta(days=dias_desde_terca)
    fim = inicio + timedelta(days=5)

    return inicio, fim


def validar_data_reserva(data_reserva, data_atual=None):
    """
    Verifica se a data solicitada pertence à janela aberta.

    Retorna (True, None) quando permitida.
    Retorna (False, mensagem) quando não permitida.
    """
    if not isinstance(data_reserva, date) or isinstance(
        data_reserva, datetime
    ):
        return False, "A data informada é inválida."

    if data_atual is None:
        data_atual = obter_data_atual()

    if data_reserva < data_atual:
        return False, "Não é permitido reservar datas anteriores à data atual."

    janela = obter_janela_atual(data_atual)

    if janela is None:
        return False, (
            "As reservas estão fechadas. "
            "A próxima janela abre terça-feira às 00h."
        )

    inicio, fim = janela

    if not inicio <= data_reserva <= fim:
        return False, (
            "A data selecionada está fora da janela de reservas. "
            f"Período permitido: {inicio:%d/%m/%Y} a {fim:%d/%m/%Y}."
        )

    return True, None
