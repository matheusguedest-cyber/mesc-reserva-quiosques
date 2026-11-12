
from app import create_app
from app.extensions import db
from app.models import Quiosque


app = create_app()

quiosques_teste = [
    {
        "numero": "01",
        "capacidade": 10,
        "descricao": "Próximo à piscina",
        "status": "ativo"
    },
    {
        "numero": "02",
        "capacidade": 15,
        "descricao": "Próximo ao campo",
        "status": "ativo"
    },
    {
        "numero": "03",
        "capacidade": 20,
        "descricao": "Área central",
        "status": "ativo"
    },
    {
        "numero": "04",
        "capacidade": 10,
        "descricao": "Próximo às quadras",
        "status": "ativo"
    },
    {
        "numero": "05",
        "capacidade": 15,
        "descricao": "Em manutenção",
        "status": "inativo"
    }
]


with app.app_context():

    for dados in quiosques_teste:

        existente = Quiosque.query.filter_by(
            numero=dados["numero"]
        ).first()

        if existente:
            print(
                f"Quiosque {dados['numero']} já cadastrado."
            )
            continue

        quiosque = Quiosque(**dados)

        db.session.add(quiosque)

        print(
            f"Quiosque {dados['numero']} preparado para cadastro."
        )

    db.session.commit()

    print("Processamento concluído.")
