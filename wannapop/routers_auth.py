import smtplib
import ssl
from flask import Blueprint, render_template, request, flash, current_app, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .forms import Registration_form, LoginForm, ResendEmailForm
from .models import db, User
from . import bcrypt
from .hashid_utils import encode_id, decode_id
from .helpers.helper_role import HelperRole
from .helpers.helper_files import save_image
from config import ALLOWED_EXTENSIONS
import secrets
from config import MAIL_SENDER_ADDR, MAIL_SENDER_PASSWORD, MAIL_SMTP_PORT, MAIL_SMTP_SERVER
from email.message import EmailMessage
from email.utils import formataddr

auth_page = Blueprint(
    'auth_page', __name__,
    template_folder='templates'
)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# == Funcio para enviar mensajes ==
def send_verification_email(user):
    sender_addr = MAIL_SENDER_ADDR
    sender_pass = MAIL_SENDER_PASSWORD
    sender_server = MAIL_SMTP_SERVER
    sender_port = MAIL_SMTP_PORT
    contact_addr = user.email

    objeto = 'Verifica tu correo'
    enlace = url_for('auth_page.verify_email', hashid=encode_id(user.id), email_token=user.email_token, _external=True)

    # == Email con HTML ==
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; background-color: #f7f7f7; padding: 20px;">
        <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 600px; margin: auto; background: #ffffff; padding: 30px; border-radius: 8px;">
            <tr>
                <td style="text-align: center;">
                    <h2 style="color: #333;">¡Hola, {user.name}!</h2>
                    <p style="color: #555; font-size: 16px;">
                        Gracias por registrarte en <strong>Wannapop</strong>.<br>
                        Solo queda un paso para activar tu cuenta.
                    </p>

                    <a href="{enlace}" target="_blank" 
                       style="display: inline-block; padding: 12px 24px; margin-top: 20px;
                       background-color: #0066ff; color: #ffffff; text-decoration: none;
                       border-radius: 5px; font-size: 16px;">
                        Verificar Email
                    </a>

                    <p style="margin-top: 30px; color: #777; font-size: 14px;">
                        Si el botón no funciona, copia y pega este enlace en tu navegador:
                    </p>

                    <p style="word-break: break-all; font-size: 14px;">
                        <a href="{enlace}" target="_blank" style="color: #0066ff;">{enlace}</a>
                    </p>

                    <hr style="margin-top: 30px; border: none; border-top: 1px solid #eee;">

                    <p style="color: #999; font-size: 12px;">
                        Si no solicitaste este correo, puedes ignorarlo.
                    </p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg['From'] = formataddr(("Soporte Wannapop", sender_addr))
    msg['To'] = formataddr((user.name, contact_addr))
    msg['Subject'] = objeto
    msg.set_content("Por favor verifica tu email.")
    msg.add_alternative(html_content, subtype="html")

    contexto = ssl.create_default_context()

    with smtplib.SMTP(sender_server, sender_port) as server:
        server.starttls(context=contexto)
        server.login(sender_addr, sender_pass)
        server.send_message(msg, from_addr=sender_addr, to_addrs=contact_addr)


# == Registre usuarios ==
@auth_page.route('/register', methods=["GET", "POST"])
def register():
    form = Registration_form()
    if form.validate_on_submit():

        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Ese correo ya esta registrado. Prueba con otro.", "warning")
            return redirect(url_for('auth_page.register'))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        tokenEmail = secrets.token_urlsafe(20)

        filename = "avatar.png"
        if form.avatar.data and form.avatar.data.filename != "":
            if allowed_file(form.avatar.data.filename):
                filename = save_image(form.avatar.data, upload_folder=current_app.config['UPLOAD_FOLDER'])
            else:
                flash("Tipo de archivo no permitido", "danger")
                return render_template('auth/register.html', form=form)

        user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password,
            avatar=filename,
            role_id=1,
            verified=False,
            email_token=tokenEmail
        )

        try:
            db.session.add(user)
            db.session.commit()

            send_verification_email(user)

            flash('Usuario registrado con exito!', 'success')
            flash('Revisa tu correo para confirmar email!', 'success')
            current_app.logger.info(f"Usuario registrado: {user.name} {user.email}")
            return redirect(url_for('auth_page.login'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error en el registro de usuario: {e}', 'danger')
            current_app.logger.error(f"Error al registrar: {e}")
            return render_template('auth/register.html', form=form)

    return render_template('auth/register.html', form=form)


# == Login ==
@auth_page.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    next_page = request.args.get('next')

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            
            if not user.verified:
                flash("Tu cuenta aun no esta verificada. Revisa tu correo.", "warning")
                return redirect(url_for('auth_page.login'))

            flash(f'Bienvenido {user.name}!', 'success')
            login_user(user)
            HelperRole.notify_identity_changed()
            current_app.logger.info(f"Usuario logueado: {user.email}")
            return redirect(next_page or url_for('main_page.home'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
            return redirect(url_for('auth_page.login'))

    return render_template('auth/login.html', form=form, next=next_page)


# == Verificacion email ==
@auth_page.route('/verify/<hashid>/<string:email_token>')
def verify_email(hashid, email_token):
    user_id = decode_id(hashid)
    usuario = User.query.filter_by(id=user_id, email_token=email_token).first()

    if not usuario:
        flash("Error en confirmacion de email", 'danger')
        return redirect(url_for("auth_page.login"))

    usuario.verified = True
    usuario.email_token = None
    db.session.commit()

    flash("Email verificado con exito!", 'success')
    return redirect(url_for("auth_page.login"))


# == Resend de token para verificacion ==
@auth_page.route("/resend", methods=["GET", "POST"])
def resend_email():
    if current_user.is_authenticated:
        flash("Ya estás logueado.", "info")
        return redirect(url_for("main_page.home"))

    form = ResendEmailForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No existe ningún usuario con ese correo.", "danger")
            return redirect(url_for("auth_page.resend_email"))

        if user.verified:
            flash("Tu correo ya ha sido verificado.", "info")
            return redirect(url_for("auth_page.login"))

        user.email_token = secrets.token_urlsafe(20)
        db.session.commit()

        send_verification_email(user)
        flash("Se ha enviado un nuevo correo de verificación.", "success")
        return redirect(url_for("auth_page.login"))

    return render_template('auth/resend.html', form=form)


# == Logout ==
@auth_page.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Has cerrado sesion.", "info")
    return redirect(url_for("auth_page.login"))
