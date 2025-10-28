from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from .helpers.helper_role import HelperRole as hr
from .models import db, Product, AcceptedOffer, Offer
from .hashid_utils import encode_id, decode_id
from .forms import AcceptOfferForm, CancelOfferForm

routes_sales = Blueprint("routes_sales", __name__, template_folder="templates")
BalanceTotal = 0

@routes_sales.route("/sales/pending", methods=["GET"])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def sales():

    offers = (
        Offer.query
        .join(Product, Offer.product_id == Product.id)
        .filter(Product.seller_id == current_user.id, Offer.active.is_(True))
        .order_by(Offer.product_id) 
        .all()
    )

    offers_by_product = {}
    for o in offers:
        offers_by_product.setdefault(o.product, []).append(o)

    no_aceptadas = len(offers) > 0

    form = AcceptOfferForm()
    return render_template(
        "vendedor/sales.html",
        offers=offers,
        offers_by_product=offers_by_product,  
        no_aceptadas=no_aceptadas,
        form=form,
        encode_id=encode_id,
    )


@routes_sales.route("/sales/accept/<offer_id>", methods=["POST"])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def accept_offer(offer_id):
    offer_id = decode_id(offer_id)
    instrucciones = request.form.get("instructions", "")

    offer = Offer.query.get_or_404(offer_id)

    acepted_offer = AcceptedOffer(
        offer_id=offer.id,
        instructions=instrucciones,
    )


    for o in Offer.query.filter_by(product_id=offer.product_id).all():
        o.active = False 

    try:
        db.session.add(acepted_offer)
        db.session.commit()
        flash("Oferta aceptada con éxito!", "success")
        return redirect(url_for("routes_sales.sales_accepted"))
    except Exception:
        db.session.rollback()
        flash("ERROR", "danger")
        return redirect(url_for("routes_sales.sales"))


@routes_sales.route("/sales/accepted", methods=["GET"])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def sales_accepted():
    form = CancelOfferForm()
    accepted_offers = (
        AcceptedOffer.query
        .join(Offer, AcceptedOffer.offer_id == Offer.id)
        .join(Product, Offer.product_id == Product.id)
        .filter(Product.seller_id == current_user.id)
        .all()
    )
    return render_template(
        "vendedor/sales_aceptadas.html",
        acceptedOffers=accepted_offers,
        form=form,
        encode_id=encode_id
    )

@routes_sales.route("/sales/update/<accepted_offer_id>", methods=["POST"])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def update_offer(accepted_offer_id):
    decoded_accepted_id = decode_id(accepted_offer_id)
    accepted = AcceptedOffer.query.get_or_404(decoded_accepted_id)

    instrucciones = request.form.get("instructions", "")
    try:
        accepted.instructions = instrucciones
        db.session.commit()
        flash("Instrucciones actualizadas con éxito!", "success")
    except Exception:
        db.session.rollback()
        flash("ERROR", "danger")
    return redirect(url_for("routes_sales.sales_accepted"))

@routes_sales.route("/sales/delete/<accepted_offer_id>", methods=["POST"])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def delete_accepted_offer(accepted_offer_id):
    decoded_accepted_id = decode_id(accepted_offer_id)
    accepted = AcceptedOffer.query.get_or_404(decoded_accepted_id)

    try:
        offer = Offer.query.get_or_404(accepted.offer_id)
        product_id = offer.product_id

        for o in Offer.query.filter_by(product_id=product_id).all():
            o.active = True

        db.session.delete(accepted)

        db.session.commit()
        flash("Has cancelado la aceptación. Todas las ofertas han sido reactivadas.", "info")
        return redirect(url_for("routes_sales.sales"))
    except Exception:
        db.session.rollback()
        flash("ERROR al cancelar la oferta aceptada.", "danger")
        return redirect(url_for("routes_sales.sales_accepted"))
    
@routes_sales.route('/sales/inactive')
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def list_inactive():
    offers_inactive = (
        Offer.query
        .join(Product, Offer.product_id == Product.id)
        .filter(Product.seller_id == current_user.id, Offer.active.is_(False))
        .order_by(Offer.created.desc())
        .all()
    )

    return render_template('vendedor/inactive.html', offers=offers_inactive, encode_id=encode_id)
