from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, IntegerField, PasswordField, SelectField, TextAreaField, HiddenField, MultipleFileField, DecimalField
from wtforms.validators import DataRequired, Length, Optional, NumberRange, Email, EqualTo
from flask_wtf.file import FileField, FileAllowed, FileRequired

# == Formularios para Usuarios ==

class UserForm(FlaskForm):
    name = StringField('Usuario', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(message="Introduce un email valido"),Length(max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=30)])
    confirm_password = PasswordField("Repite la contraseña", validators=[DataRequired(), EqualTo("password", message="Las contraseñas no coinciden")]) 
    avatar = FileField('Avatar', validators=[DataRequired(), FileAllowed(['png', 'jpg', 'jpeg'], 'Solo imagenes permitidas')])
    role_id = SelectField('Rol', coerce=int)
    submit = SubmitField('CREAR')


class UserDeleteForm(FlaskForm):
    submit = SubmitField('Confirmar')


class UpdateUserForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=120)])
    avatar = FileField('Avatar', validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    role_id = SelectField('Rol', coerce=int)
    submit = SubmitField('ACTUALIZAR')


class BlockUserForm(FlaskForm):
    reason = TextAreaField(label='La razon de bloqueo', validators=[DataRequired()])


class UnblockeoUserForm(BlockUserForm):
    reason = StringField(label='La razon de desbloqueo', validators=[DataRequired()])


# == Login / Register ==

class Registration_form(UserForm):
    name = StringField('Nombre y apellidos', validators=[DataRequired(), Length(min=3, max=80)])
    role_id = HiddenField(default=1)
    submit = SubmitField('Registrarse')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Entrar')

# == Formularios para productos ==

class ProductForm(FlaskForm):
    title = StringField('Título', validators=[DataRequired(), Length(min=2, max=120)])
    description = TextAreaField('Descripción', validators=[DataRequired(), Length(min=5, max=500)])
    photo = FileField('Foto', validators=[Optional(), FileAllowed(['png', 'jpg', 'jpeg'])])
    price = IntegerField('Precio', validators=[DataRequired(), NumberRange(min=1)])
    category = SelectField('Categoria', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Guardar')


class ProductCreateForm(ProductForm):
    photo = FileField('Foto', validators=[
        FileRequired(),
        FileAllowed(['png', 'jpg', 'jpeg'])
    ])


class ProductDeleteForm(FlaskForm):
    submit = SubmitField(label="Eliminar")


class BlockProductForm(FlaskForm):
    reason = TextAreaField('Razón', validators=[DataRequired(), Length(min=5, max=255)])
    submit = SubmitField('Bloquear')

# == Formulrio para contacto ==

class ContactForm(FlaskForm):
    message = TextAreaField(
        label='Mensaje',
        validators=[DataRequired(), Length(min=10, max=1000)]
    )
    attachments = MultipleFileField(label='Adjuntar archivos')  # новые файлы :)
    submit = SubmitField(label='Enviar')

# == Formulario para update de perfil ==

class ProfileUpdateForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=80)])
    avatar = FileField('Avatar', validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    email = StringField('Email', validators=[DataRequired(), Email(message="Introduce un email valido"),Length(max=120)])
    submit = SubmitField('Guardar cambios')

# == Formulario para resend Email ==

class ResendEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(message="Introduce un email valido"),Length(max=120)])
    submit = SubmitField('Reenviar enlace')

class AcceptOfferForm(FlaskForm):
    instructions = StringField('Instrucciones', validators=[DataRequired(), Length(min=1, max=600)])    
    submit = SubmitField('Aceptar oferta')

class CancelOfferForm(FlaskForm):
    instructions = StringField('Nuevas instrucciones', validators=[DataRequired(), Length(min=1, max=600)])    
    submit = SubmitField('Guardar')
    cancel = SubmitField('Cancelar oferta')


# == Formulrio para crear / update oferta ==

class OfferForm(FlaskForm):
    price = DecimalField("Tu oferta",places=2, validators=[DataRequired(message="Ingresa un precio"), NumberRange(min=0)],)
    submit = SubmitField("Enviar oferta")
