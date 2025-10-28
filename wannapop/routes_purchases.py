from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, Response
from .models import db, Product, User, Offer, blocked_users
from .forms import OfferForm
from .hashid_utils import encode_id, decode_id
from flask_login import login_required, current_user
from .helpers.helper_role import HelperRole as hr


routes_purchases = Blueprint(
    'routes_purchases', __name__, template_folder='templates/purchases')


@routes_purchases.route('/purchases/create/<hashid>', methods=['POST'])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def create_offer(hashid):
    product_id = decode_id(hashid)

    if current_user.role.name != 'wanner':
        flash("Solo los Wanners pueden hacer ofertas", "danger")
        return redirect(url_for('routes_products.get_product', hashid=hashid))

    if current_user.blocked_as_user:
        flash("No tienes permiso de compra por estar bloqueado! Contacta con soporte.", "warning")
        return redirect(url_for('routes_products.get_products'))

    product = Product.query.get_or_404(product_id)

    if current_user.id == product.seller_id:
        flash("No puedes hacer ofertas a tu propio producto", "danger")
        return redirect(url_for('routes_products.get_product', hashid=hashid))

    if product.blocked:
        flash("No puedes hacer oferta a un producto bloqueado", "danger")
        return redirect(url_for('routes_products.get_product', hashid=hashid))

    seller_blocked = blocked_users.query.filter_by(
        user_id=product.seller_id).first()
    if seller_blocked:
        flash("No puedes hacer oferta a un usuario bloqueado!", "danger")
        return redirect(url_for('routes_products.get_product', hashid=hashid))

    form = OfferForm()
    if form.validate_on_submit():
        price = form.price.data
        min_price = product.price

        if price < min_price:
            flash(f"La oferta debe ser al menos {min_price}", "warning")
            return redirect(url_for('routes_products.get_product', hashid=hashid))

        existing_offer = Offer.query.filter_by(
            product_id=product.id,
            buyer_id=current_user.id
        ).first()

        if existing_offer:
            flash("Ya has hecho una oferta para este producto", "warning")
            return redirect(url_for('routes_products.get_product', hashid=hashid))

        if any(offer.accepted_offer for offer in product.offers):
            flash("Este producto ya esta vendido", "danger")
            return redirect(url_for('routes_products.get_product', hashid=hashid))

        offer = Offer(
            product_id=product.id,
            buyer_id=current_user.id,
            offer=price
        )
        db.session.add(offer)
        db.session.commit()
        flash("Oferta creada con éxito!", "success")
        return redirect(url_for('routes_purchases.list_pending'))

    flash("Error en la oferta", "danger")
    return redirect(url_for('routes_products.get_product', hashid=hashid))


@routes_purchases.route('/purchases/pending')
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def list_pending():
    offers = (
        Offer.query
        .filter_by(buyer_id=current_user.id)
        .filter(Offer.accepted_offer == None)
        .order_by(Offer.created.desc())
        .all()
    )

    # Se pasaa el diccionario de forms para cada producto para que tenga su precio correspondiente
    forms = {offer.id: OfferForm(price=offer.offer) for offer in offers}

    return render_template('pending.html', offers=offers, forms=forms, encode_id=encode_id)


@routes_purchases.route('/purchases/accepted')
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def list_accepted():


    offers = (
        Offer.query
        .filter_by(buyer_id=current_user.id)
        .filter(Offer.accepted_offer != None)
        .order_by(Offer.created.desc())
        .all()
    )

    return render_template('accepted.html', offers=offers)


@routes_purchases.route('/purchases/update/<hashid>', methods=['POST'])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def update_offer(hashid):
    offer_id = decode_id(hashid)

    offer = Offer.query.get_or_404(offer_id)

    # Realmente no hace falta porque solo acepta POST, pero lo dejo como segunda capa por si alguien intenta hacer peticiones POST con CURL etc..
    if current_user.id != offer.buyer_id:
        flash("No tienes permisos para editar esta oferta", "danger")
        return redirect(url_for('routes_purchases.list_pending'))

    if offer.accepted_offer:  # Lo mismo que comprobacion anterior
        flash("La oferta ya fue aceptada y no se puede modificar", "warning")
        return redirect(url_for('routes_purchases.list_pending'))

    form = OfferForm()
    if form.validate_on_submit():
        price = form.price.data
        min_price = offer.product.price

        if price < min_price:
            flash(f"La oferta debe ser al menos {min_price}", "warning")
            return redirect(url_for('routes_purchases.list_pending'))

        offer.offer = price
        db.session.commit()

    return redirect(url_for('routes_purchases.list_pending'))


@routes_purchases.route('/purchases/delete/<hashid>', methods=['POST'])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def delete_offer(hashid):
    offer_id = decode_id(hashid)

    offer = Offer.query.get_or_404(offer_id)

    if current_user.id != offer.buyer_id:
        flash("No tienes permisos para eliminar esta oferta", "danger")
        return redirect(url_for('routes_purchases.list_pending'))

    if offer.accepted_offer:
        flash("La oferta ya fue aceptada y no se puede eliminar", "warning")
        return redirect(url_for('routes_purchases.list_pending'))

    db.session.delete(offer)
    db.session.commit()

    flash("Oferta eliminada", "success")
    return redirect(url_for('routes_purchases.list_pending'))


@routes_purchases.route('/purchases/inactive')
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def list_inactive():
    offers_inactive = Offer.query.filter(
        Offer.buyer_id == current_user.id,
        Offer.active == False
    ).order_by(Offer.created.desc()).all()

    return render_template('inactive.html', offers=offers_inactive)
