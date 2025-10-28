from flask import Blueprint, current_app, render_template, request, flash, redirect, url_for
from config import ALLOWED_EXTENSIONS
from .models import User, db, Role, blocked_users, Product, AcceptedOffer, Offer
from .forms import UserForm, UpdateUserForm, UserDeleteForm
from flask_login import login_required, current_user
from . import bcrypt
from .helpers.helper_role import HelperRole as hr
from .hashid_utils import encode_id, decode_id
from .helpers.helper_files import save_image
from sqlalchemy import or_

routers_user = Blueprint('routers_user', __name__, template_folder='templates')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ====== Lista de usuarios ======
@routers_user.route('/users')
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def users():
    role_name = getattr(current_user.role, "name", "").lower()

    query = db.session.query(User, Role).join(Role).order_by(Role.id.asc())
    if role_name == "wanner":
        query = query.filter(Role.name.ilike("wanner"))

    bloqueados = {b.user_id for b in blocked_users.query.all()}

    busqueda = request.args.get('busqueda[nameOrmail]', '', type=str).strip()

    if busqueda:
        patron = f"%{busqueda}%"
        query = query.filter(or_(User.name.ilike(patron),
                                 User.email.ilike(patron)))

    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    usuarios = pagination.items

    qargs = request.args.to_dict(flat=True)
    qargs.pop('page', None)

    is_admin = role_name == "admin"
    is_moderator = role_name == "moderator"

    return render_template(
        "lista_users.html",
        usuarios=usuarios,
        pagination=pagination,
        qargs=qargs,
        bloqueados=bloqueados,
        is_admin=is_admin,
        is_moderator=is_moderator
    )


# ====== Detalle de usuario ======
@routers_user.route("/user/<hashid>")
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def user_detail(hashid):
    user_id = decode_id(hashid)
    if user_id is None:
        flash("Hash invalido", "danger")
        return redirect(url_for("routers_user.users"))

    usuario = db.session.get(User, user_id)
    
    ofertas_aceptadas = (
        AcceptedOffer.query
        .join(Offer, AcceptedOffer.offer_id == Offer.id)
        .join(Product, Offer.product_id == Product.id)
        .filter(Product.seller_id==user_id)
        .all())
    
    ofertas = Offer.query.join(Product, Offer.product_id == Product.id).filter(Product.seller_id==user_id).all()

    total_ofertas = len(ofertas)
    

    total_aceptadas = len(ofertas_aceptadas)



    if usuario.blocked_as_user:
        flash("Usuario esta bloqueado!", "danger")
        return redirect(url_for("routers_user.users"))

    
    if not usuario:
        flash("Usuario no encontrado", "danger")
        return redirect(url_for("routers_user.users"))

    products = Product.query.filter_by(seller_id=usuario.id).all()
    return render_template("user_info.html", usuario=usuario, products=products, total_aceptadas=total_aceptadas, total_ofertas=total_ofertas)


# ====== Eliminar usuario ======
@routers_user.route('/user/delete/<hashid>', methods=["GET", "POST"])
@login_required
@hr.admin_role_permission.require(http_exception=403)
def delete_user(hashid):
    user_id = decode_id(hashid)
    if user_id is None:
        flash("Hash inválido", "danger")
        return redirect(url_for('routers_user.users'))

    usuario = User.query.get(user_id)
    if not usuario:
        flash("Usuario no encontrado", 'danger')
        return redirect(url_for('routers_user.users'))

    if usuario.role.name == "admin":
        flash("No puedes eliminar a otro administrador.", "danger")
        return redirect(url_for('routers_user.users'))

    if usuario.id == current_user.id:
        flash("No puedes eliminarte a ti mismo.", "warning")
        return redirect(url_for('routers_user.users'))
    
    haveProducts = Product.query.filter_by(seller_id=usuario.id).first()
    if haveProducts:
        flash("No puedes eliminar a usuario que tiene productos!.", "warning")
        return redirect(url_for('routers_user.users'))
    
    haveOffers = Offer.query.filter_by(buyer_id=usuario.id).first()
    if haveOffers:
        flash("No puedes eliminar a usuario que tiene ofertas!.", "warning")
        return redirect(url_for('routers_user.users'))
    

    form = UserDeleteForm()
    if form.validate_on_submit():
        try:
            db.session.delete(usuario)
            db.session.commit()
            flash(f"Usuario '{usuario.name}' eliminado con éxito!", 'success')
            current_app.logger.info(f"Usuario eliminado: {usuario.name} ({usuario.email})")
            return redirect(url_for('routers_user.users'))
        except Exception as e:
            current_app.logger.exception(e)
            db.session.rollback()
            flash("Error al eliminar usuario.", "danger")
            return redirect(url_for("routers_user.delete_user", hashid=encode_id(user_id)))

    return render_template("users/delete.html", usuario=usuario, form=form)


# ====== Crear usuario ======
@routers_user.route('/user/create', methods=["GET", "POST"])
@login_required
@hr.admin_role_permission.require(http_exception=403)
def create():
    form = UserForm()
    roles = db.session.query(Role).all()
    form.role_id.choices = [(r.id, r.name) for r in roles]

    if request.method == 'POST' and form.validate_on_submit():
   
        filename = "avatar.png"
        if form.avatar.data:
            filename = save_image(form.avatar.data, upload_folder=current_app.config.get('UPLOAD_FOLDER'))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password,
            avatar=filename,
            role_id=form.role_id.data,
            verified=True
        )

        db.session.add(user)
        db.session.commit()
        flash('Usuario creado con éxito!', 'success')
        current_app.logger.info(f"Usuario creado: {user.name} {user.email}")
        return redirect(url_for('routers_user.users'))

    return render_template('users/create.html', form=form)


# ====== Actualizar usuario ======
@routers_user.route('/user/update/<hashid>', methods=["GET", "POST"])
@login_required
@hr.wanner_role_permission.require(http_exception=403)
def update_user(hashid):
    user_id = decode_id(hashid)
    if user_id is None:
        flash("Hash inválido", "danger")
        return redirect(url_for('routers_user.users'))

    usuario = db.session.get(User, user_id)
    if not usuario:
        flash("Usuario no encontrado", 'danger')
        return redirect(url_for('routers_user.users'))

    roles = db.session.query(Role).order_by(Role.id.asc()).all()
    form = UpdateUserForm(obj=usuario)
    form.role_id.choices = [(r.id, r.name) for r in roles]

    if request.method == "POST" and form.validate_on_submit():
        if form.avatar.data:
            filename = save_image(form.avatar.data, upload_folder=current_app.config.get('UPLOAD_FOLDER'))
            usuario.avatar = filename

        usuario.name = form.name.data
        usuario.email = form.email.data
        
        if usuario.role_id != 1:
            usuario.role_id = form.role_id.data

        try:
            db.session.commit()
            flash("Usuario actualizado con éxito!", "success")
            current_app.logger.info("Usuario actualizado!")
            return redirect(url_for("routers_user.user_detail", hashid=encode_id(usuario.id)))
        except Exception:
            db.session.rollback()
            flash("Error al actualizar usuario", "danger")

    return render_template("users/update.html", form=form, usuario=usuario)
