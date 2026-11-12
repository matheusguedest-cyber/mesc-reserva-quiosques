
from datetime import date

from bs4 import BeautifulSoup

import app.services.janela_reservas as janela_reservas
import app.routes.quiosques as rotas_quiosques

from tests.test_rota_reservas import autenticar_cliente


def test_interface_exibe_periodo_semanal(
    cliente, data_atual_controlada
):
    autenticar_cliente(cliente)

    resposta = cliente.get("/quiosques")
    pagina = BeautifulSoup(resposta.data, "html.parser")

    assert resposta.status_code == 200

    assert "17/11/2026 a 22/11/2026" in pagina.get_text()

    campo_data = pagina.find("input", {"name": "data"})

    assert campo_data["min"] == "2026-11-17"
    assert campo_data["max"] == "2026-11-22"
    assert not campo_data.has_attr("disabled")


def test_interface_segunda_feira_bloqueada(
    cliente, monkeypatch
):
    data_simulada = date(2026, 11, 16)

    monkeypatch.setattr(
        janela_reservas,
        "obter_data_atual",
        lambda: data_simulada
    )

    monkeypatch.setattr(
        rotas_quiosques,
        "obter_data_atual",
        lambda: data_simulada
    )

    autenticar_cliente(cliente)

    resposta = cliente.get("/quiosques")
    pagina = BeautifulSoup(resposta.data, "html.parser")

    assert resposta.status_code == 200

    assert "Reservas temporariamente fechadas" in pagina.get_text()

    campo_data = pagina.find("input", {"name": "data"})
    botao_consultar = pagina.find("button", string=lambda texto: texto and "Consultar" in texto)

    assert campo_data.has_attr("disabled")
    assert botao_consultar.has_attr("disabled")


def test_interface_sexta_feira_nao_permite_datas_passadas(
    cliente, monkeypatch
):
    data_simulada = date(2026, 11, 20)

    monkeypatch.setattr(
        janela_reservas,
        "obter_data_atual",
        lambda: data_simulada
    )

    monkeypatch.setattr(
        rotas_quiosques,
        "obter_data_atual",
        lambda: data_simulada
    )

    autenticar_cliente(cliente)

    resposta = cliente.get("/quiosques")
    pagina = BeautifulSoup(resposta.data, "html.parser")

    assert resposta.status_code == 200

    campo_data = pagina.find("input", {"name": "data"})

    assert campo_data["min"] == "2026-11-20"
    assert campo_data["max"] == "2026-11-22"
    assert "20/11/2026 a 22/11/2026" in pagina.get_text()
