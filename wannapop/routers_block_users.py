from flask import Blueprint, render_template, flash, request, current_app, redirect, url_for
from config import SALT
from .models import User, db, blocked_users, Offer, AcceptedOffer, Product
from .forms import BlockUserForm, UnblockeoUserForm
from hashids import Hashids
from flask_login import login_required, current_user
from .helpers.helper_role import HelperRole as hr
from config import SALT
from hashids import Hashids
from .hashid_utils import decode_id

hashids = Hashids(min_length=4, salt=SALT)

routers_block_users = Blueprint('routers_block_users', __name__, template_folder='templates')

@routers_block_users.route('/users/<hashid>/block', methods=['GET', 'POST'])
@login_required
@hr.moderator_role_permission.require(http_exception=403)  
def block_user(hashid):
    user_id = decode_id(hashid)
    if user_id is None:
        flash("Hash invalido", "danger")
        return redirect(url_for('routers_user.users'))

    usuario = db.session.get(User, user_id)
    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for('routers_user.users'))

    form = BlockUserForm()            

    if request.method == "POST":
        if form.validate_on_submit():
            try:
                buyer_id = usuario.id

                (Offer.query.filter(Offer.buyer_id == buyer_id,~Offer.accepted_offer.has()).delete(synchronize_session=False))

                bloqueo = blocked_users(
                    user_id=usuario.id,
                    moderator_id=current_user.id,
                    reason=form.reason.data
                )
                db.session.add(bloqueo)

                db.session.commit()
                flash(f"Usuario {usuario.name} bloqueado con exito!", "success")
                current_app.logger.info(f"Usuario bloqueado: {usuario.name}, {usuario.id}")
                return redirect(url_for('routers_user.users'))

            except Exception as e:
                db.session.rollback()
                flash("Error al bloquear usuario: " + str(e), "danger")
        else:
            flash("Datos del formulario no validos", "warning")

    return render_template("users/block.html", form=form, usuario=usuario, hashids=hashids)


@routers_block_users.route('/users/<hashid>/unblock', methods=['GET', 'POST'])
@login_required
@hr.moderator_role_permission.require(http_exception=403)      
def unblock_user(hashid):
    user_id = decode_id(hashid)
    if user_id is None:
        flash("Hash inválido", "danger")
        return redirect(url_for('routers_user.users'))  

    usuario = db.session.get(User, user_id)
    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for('routers_user.users'))

    form = UnblockeoUserForm()

    if request.method == "POST":
        try:
            bloqueo = blocked_users.query.filter_by(user_id=usuario.id).first()
            if bloqueo:
                db.session.delete(bloqueo)
                db.session.commit()
                flash(f"Usuario {usuario.name} desbloqueado con éxito!", "success")
                current_app.logger.info(f"Usuario desbloqueado: {usuario.name}, {usuario.id}")
                return redirect(url_for('routers_user.users'))
            else:
                flash("Este usuario no estaba bloqueado", "warning")
        except Exception as e:
            db.session.rollback()
            flash("Error al desbloquear usuario: " + str(e), "danger")

    return render_template("users/unblock.html", form=form, usuario=usuario, hashids=hashids)
