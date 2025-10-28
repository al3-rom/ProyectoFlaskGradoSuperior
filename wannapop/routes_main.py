from flask import Blueprint, render_template, redirect, flash, url_for
from flask_login import login_required, current_user
from .forms import ContactForm
from wannapop import mail_manager
import os

main_page = Blueprint(
    'main_page', __name__,
    template_folder='templates'
)

@main_page.route('/')
def home():
    return render_template('home.html')

@main_page.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        try:
            uploaded_files = []
            for f in form.attachments.data:
                if f:
                    file_path = os.path.join(mail_manager.upload_folder, f.filename)
                    f.save(file_path)
                    uploaded_files.append(file_path)

            mail_manager.send_contact_msg(
                user=current_user,
                message_text=form.message.data,
                attachments=uploaded_files,
                include_avatar=True
            )

            flash("Tu mensaje ha sido enviado con éxito.", "success")
            return redirect(url_for('main_page.home'))

        except Exception as e:
            flash(f"Error al enviar el correo: {e}", "danger")

    return render_template('contact.html', form=form)