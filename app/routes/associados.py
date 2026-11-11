
from flask import Blueprint, render_template
from flask_login import login_required, current_user


associados_bp = Blueprint("associados", __name__)


@associados_bp.route("/area-associado", methods=["GET"])
@login_required
def area_associado():

    return render_template(
        "area_associado.html",
        associado=current_user
    )
