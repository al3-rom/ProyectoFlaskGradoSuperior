import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, Response
from .models import db, Product, Category, User
from .hashid_utils import encode_id, decode_id
from .forms import ProductForm, ProductCreateForm, ProductDeleteForm, OfferForm
import openpyxl
from io import BytesIO
from flask import send_file
from flask_login import login_required, current_user
from .helpers.helper_role import HelperRole as hr
from .helpers.helper_files import save_image
from sqlalchemy import or_

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'wannapop/static/uploads')
if not os.path.isabs(UPLOAD_FOLDER):
    UPLOAD_FOLDER = os.path.join(
        os.path.dirname(__file__), '..', UPLOAD_FOLDER)
    UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)


routes_products = Blueprint(
    'routes_products', __name__, template_folder='templates')


@routes_products.route('/products')
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def get_products():

    categories = Category.query.all()
    form = ProductForm()
    form.category.choices = [(c.name, c.name) for c in categories]

    filter_category = request.args.get('category', None)
    search_query = request.args.get('search', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 12

    if filter_category == '':
        return redirect(url_for('routes_products.get_products'))

    products_query = Product.query

    # == Filtrar por categorias ==
    if filter_category:
        products_query = products_query.join(Category).filter(
            Category.name == filter_category
        )

    # == Buscar ==
    if search_query:
        products_query = products_query.filter(
            or_(
                Product.title.ilike(f"%{search_query}%"),
                Product.description.ilike(f"%{search_query}%")
            )
        )

    products_paginated = products_query.paginate(page=page, per_page=per_page, error_out=False)
    products = products_paginated.items

    return render_template(
        'products.html',
        products=products,
        categories=categories,
        form=form,
        encode_id=encode_id,
        filter_category=filter_category,
        search_query=search_query,
        pagination=products_paginated
    )


@routes_products.route('/products/<hashid>')
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def get_product(hashid):
    product_id = decode_id(hashid)
    product = Product.query.get_or_404(product_id)
    seller = User.query.get(product.seller_id)

    offer_form = OfferForm()
    offer_form.price.data = product.price

    return render_template('product.html', product=product, seller=seller, encode_id=encode_id, offer_form=offer_form)


@routes_products.route('/products/create', methods=['GET', 'POST'])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def create_product():
    form = ProductCreateForm()

    if current_user.role.name != 'wanner':
        flash("Solo los usuarios con rol \"wanner\" pueden crear productos", "warning")
        return redirect(url_for('routes_products.get_products'))

    if current_user.blocked_as_user:
        flash("No tienes acceso por estar bloqueado! Contacta con soporte.", "warning")
        return redirect(url_for('routes_products.get_products'))
    
    categories = Category.query.all()
    form.category.choices = [(c.id, c.name) for c in categories]

    if form.validate_on_submit():
        filename = save_image(form.photo.data)
        product = Product(
            title=form.title.data,
            description=form.description.data,
            photo=filename,
            price=form.price.data,
            category_id=form.category.data,
            seller_id=current_user.id
        )
        db.session.add(product)
        db.session.commit()
        flash('Producto creado!', 'success')
        current_app.logger.info(
            f"Producto creado: {product.title}-{product.description}!")
        return redirect(url_for('routes_products.get_products'))
    return render_template('products/create.html', form=form)


@routes_products.route('/products/update/<hashid>', methods=["GET", "POST"])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def update_product(hashid):
    product_id = decode_id(hashid)
    product = Product.query.get_or_404(product_id)

    if product.seller_id != current_user.id:
        flash("No tienes permisos para editar este producto", "danger")
        return redirect(url_for('routes_products.get_products'))

    if any(offer.accepted_offer for offer in product.offers):
        flash("El producto tiene una oferta aceptada y no se puede editar", "danger")
        return redirect(request.referrer or url_for('routes_products.get_products'))

    form = ProductForm(obj=product)

    categories = Category.query.all()
    form.category.choices = [(c.id, c.name) for c in categories]

    if request.method == "GET":
        form.category.data = product.category_id

    if form.validate_on_submit():
        product.title = form.title.data
        product.description = form.description.data
        product.price = form.price.data
        product.category_id = form.category.data

        if form.photo.data and hasattr(form.photo.data, 'filename'):
            filename = save_image(form.photo.data)
            product.photo = filename

        db.session.commit()
        flash('Producto actualizado!', 'success')
        current_app.logger.info(
            f"Producto actualizado: {product.title}-{product.description}!")
        return redirect(url_for('routes_products.get_product', hashid=hashid))

    return render_template('products/update.html', form=form, product=product)


@routes_products.route('/products/delete/<hashid>', methods=["GET", "POST"])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def delete_product(hashid):
    product_id = decode_id(hashid)
    product = Product.query.get_or_404(product_id)

    if product.seller_id != current_user.id:
        flash("No tienes permisos para eliminar este producto", "danger")
        return redirect(url_for('routes_products.get_products'))

    if any(offer.accepted_offer for offer in product.offers):
        flash("El producto tiene una oferta aceptada y no se puede eliminar", "danger")
        return redirect(request.referrer or url_for('routes_products.get_products'))

    form = ProductDeleteForm()

    if form.validate_on_submit():
        if request.form.get("confirm") == "yes":
            db.session.delete(product)
            db.session.commit()
            flash("Producto eliminado!", "success")
            current_app.logger.info(
                f"Producto eliminado: {product.title}-{product.description}!")
            return redirect(url_for('routes_products.get_products'))
        else:
            flash("Eliminación cancelada.", "info")
            return redirect(url_for('routes_products.get_product', hashid=hashid))
    return render_template('products/delete.html', product=product, form=form)


@routes_products.route('/exportar/csv')
@login_required
def export_csv():
    products = Product.query.all()

    def generate():

        yield "id,title,description,price\n"

        for p in products:
            yield f"{p.id},{p.title},{p.description},{p.price}\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=products.csv"}
    )


@routes_products.route('/exportar/excel')
@login_required
def export_excel():
    products = Product.query.all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Productos"

    ws.append(["ID", "Título", "Descripción", "Precio"])

    for p in products:
        ws.append([p.id, p.title, p.description, p.price])

    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name="products.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
