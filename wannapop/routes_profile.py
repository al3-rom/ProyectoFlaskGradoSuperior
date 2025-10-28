import smtplib
import ssl
from flask import Blueprint, current_app, render_template, redirect, request, flash, url_for
from flask_login import login_required, current_user
from .forms import ProfileUpdateForm
from .hashid_utils import encode_id
from .helpers.helper_files import save_image
from .models import db, AcceptedOffer, Offer, Product
import os
from config import MAIL_SENDER_ADDR, MAIL_SENDER_PASSWORD, MAIL_SMTP_PORT, MAIL_SMTP_SERVER
from email.message import EmailMessage
from email.utils import formataddr
import secrets




routes_profile = Blueprint(
    'routes_profile', __name__,
    template_folder='templates/profile'
)

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'wannapop/static/uploads')
if not os.path.isabs(UPLOAD_FOLDER):
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', UPLOAD_FOLDER)
    UPLOAD_FOLDER = os.path.abspath(UPLOAD_FOLDER)


@routes_profile.route("/profile")
@login_required
def profile():
    Balance = 0

    ofertas_aceptadas = AcceptedOffer.query.join(Product, Offer.product_id==Product.id).filter(Product.seller_id==current_user.id, Offer.active.is_(False)).all()

    if ofertas_aceptadas:
        for oferta in ofertas_aceptadas:
            if oferta.offer.buyer_id != current_user.id:
                Balance += oferta.offer.offer
            elif oferta.offer.buyer_id == current_user.id:
                Balance -= oferta.offer.offer


    return render_template('profile.html', current_user=current_user, products=current_user.products, encode_id=encode_id, Balance=Balance)

@routes_profile.route("/profile/update", methods=["GET", "POST"])
@login_required
def update_profile():
    form = ProfileUpdateForm()

    if form.validate_on_submit():
        current_user.name = form.name.data
        email_cambiado = form.email.data != current_user.email

        if form.avatar.data:
            filename = save_image(form.avatar.data)
            if filename:
                current_user.avatar = filename
        
        if email_cambiado:
            nuevo_email  = form.email.data
            tokenEmail = secrets.token_urlsafe(20)

            existing_correo = current_user.query.filter_by(email=form.email.data).first()
            if existing_correo:
                flash("Ese correo ya esta registrado. Prueba con otro.", "warning")
                return redirect(url_for("routes_profile.profile"))

            sender_addr = MAIL_SENDER_ADDR
            sender_pass = MAIL_SENDER_PASSWORD
            sender_server = MAIL_SMTP_SERVER
            sender_port = MAIL_SMTP_PORT
            contact_addr = nuevo_email 

            
            
            objeto = 'Enlace de verificacion'
            enlace = url_for('auth_page.verify_email', user_id=current_user.id, email_token=tokenEmail, _external=True)
            contenido = f"Buenas {current_user.name}! Aquí tienes tu nuevo enlace de verificación:\n\n{enlace}"

            msg = EmailMessage()
            msg['From'] = formataddr(("Soporte Wannapop", sender_addr))
            msg['To'] = formataddr(("New User", contact_addr))
            msg['Subject'] = objeto
            msg.set_content(contenido)

            contexto = ssl.create_default_context()
                    
            with smtplib.SMTP(sender_server, sender_port) as server:
                        server.starttls(context=contexto)
                        server.login(sender_addr, sender_pass)
                        server.send_message(msg, from_addr=sender_addr, to_addrs=contact_addr) 

            current_user.email = nuevo_email
            current_user.email_token = tokenEmail
            current_user.verified = False
            flash("Revisa tu correo para confirmar el nuevo email.", "success")
            current_app.logger.info(f"Usuario actualizó su email: {current_user.name} ({nuevo_email})")


        db.session.commit()
        flash("Perfil actualizado con éxito", "success")
        return redirect(url_for("routes_profile.profile"))

    if request.method == "GET":
        form.name.data = current_user.name
        form.email.data = current_user.email

    return render_template("update.html", form=form, current_user=current_user)