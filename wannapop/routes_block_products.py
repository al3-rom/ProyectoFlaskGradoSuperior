from flask import Blueprint, render_template, redirect, url_for, flash
from .models import db, Product, BlockedProduct
from .hashid_utils import decode_id, encode_id
from .forms import BlockProductForm
from flask_login import login_required, current_user
from .helpers.helper_role import HelperRole as hr

routes_block_products = Blueprint(
    'routes_block_products', __name__, template_folder='templates')


@routes_block_products.route('/products/<hashid>/block', methods=['GET', 'POST'])
@login_required
@hr.moderator_role_permission.require(http_exception=403)
def block_product(hashid):
    product_id = decode_id(hashid)
    product = Product.query.get_or_404(product_id)

    if current_user.role.name == 'wanner':
        flash("No tienes permisos para bloquear este producto", "danger")
        return redirect(url_for('routes_products.get_products'))

    if product.blocked:
        flash("Este producto ya está bloqueado", "warning")
        return redirect(url_for('routes_products.get_product', hashid=encode_id(product.id)))

    if any(offer.accepted_offer for offer in product.offers):
        flash("Productos con oferta aceptada no se pueden bloquear", "warning")
        return redirect(url_for('routes_products.get_product', hashid=encode_id(product.id)))

    form = BlockProductForm()

    if form.validate_on_submit():
        block_product = BlockedProduct(
            product_id=product_id,
            moderator_id=current_user.id,
            reason=form.reason.data
        )

        db.session.add(block_product)
        db.session.commit()

        flash("Producto bloqueado correctamente", "success")
        return redirect(url_for('routes_products.get_products'))

    return render_template('products/block.html', form=form, product=product, encode_id=encode_id)


@routes_block_products.route('/products/<hashid>/unblock', methods=['POST'])
@login_required
@hr.moderator_role_permission.require(http_exception=403)
def unblock_product(hashid):
    product_id = decode_id(hashid)

    if current_user.role.name == 'wanner':
        flash("No tienes permisos para desbloquear este producto", "danger")
        return redirect(url_for('routes_products.get_products'))

    # No hace falta para mi implementacion ya que /unblock es solo POST y no tiene su propia pagina, al entrar /products/hasid/unbock saldra error de method not allowed.
    blocked = BlockedProduct.query.filter_by(product_id=product_id).first()
    if not blocked:
        flash("Este producto no está bloqueado", "warning")
        return redirect(url_for('routes_products.get_products'))

    db.session.delete(blocked)
    db.session.commit()

    flash("Producto desbloqueado correctamente", "success")
    return redirect(url_for('routes_products.get_products'))
