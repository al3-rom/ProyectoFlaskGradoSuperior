from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import login_required
from .helpers.helper_role import HelperRole as hr
from .models import User, blocked_users, Product, BlockedProduct, db
from .hashid_utils import encode_id, decode_id

routes_admin = Blueprint("routes_admin", __name__, template_folder="templates")

@routes_admin.route('/admin', methods=["GET", "POST"])
@login_required
@hr.moderator_role_permission.require(http_exception=403)
def admin():
    usuarios = User.query.all()
    productos = Product.query.all()

    hay_bloqueado = False
    hay_producto_bloqueado = False

    for usuario in usuarios:
        if usuario.blocked_as_user:
            hay_bloqueado  = True
    
    for producto in productos:
        if producto.blocked:
            hay_producto_bloqueado  = True

    if request.method == "POST":
        seleccionados_usuarios = request.form.getlist("usuarios")
        seleccionados_productos = request.form.getlist("productos")

        for hashid in seleccionados_usuarios:
            user_id = decode_id(hashid)
            bloqueo = blocked_users.query.filter_by(user_id=user_id).first()
            if bloqueo:
                db.session.delete(bloqueo)


        for hashid in seleccionados_productos:
            product_id = decode_id(hashid)
            bloqueo = BlockedProduct.query.filter_by(product_id=product_id).first()
            if bloqueo:
                db.session.delete(bloqueo)

        try:
            db.session.commit()
            flash("Usuarios || Productos - desbloqueados correctamente.", "success")
        except Exception as e:
            db.session.rollback()
            current_app.logger.exception(e)
            flash("Error al desbloquear: " + str(e), "danger")

        return redirect(url_for('routes_admin.admin'))

    return render_template(
        "admin/admin.html",
        usuarios=usuarios,
        productos=productos,
        hay_producto_bloqueado=hay_producto_bloqueado,
        hay_bloqueado=hay_bloqueado,
        encode_id=encode_id
    )
