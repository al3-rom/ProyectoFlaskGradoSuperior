import smtplib, ssl
from email.message import EmailMessage
from email.utils import formataddr
from datetime import datetime
import mimetypes
import os

class MailManager:
    def init_app(self, app):
        self.sender_addr = app.config.get('MAIL_SENDER_ADDR')
        self.sender_pass = app.config.get('MAIL_SENDER_PASSWORD')
        self.sender_server = app.config.get('MAIL_SMTP_SERVER')
        self.sender_port = app.config.get('MAIL_SMTP_PORT')
        self.contact_addr = app.config.get("CONTACT_ADDR")

        if not self.contact_addr:
            raise ValueError("CONTACT_ADDR no está configurado en config.py")

        self.upload_folder = app.config.get("UPLOAD_FOLDER", "./uploads")

    def send_contact_msg(self, user, message_text, attachments=None, include_avatar=True):
        """
        user: objeto User
        message_text: texto de mensaje
        attachments: lista de rutas a ficheros adjuntos
        include_avatar: bool, si anyadimos el avatar
        """

        objeto = f"Nuevo mensaje de {user.name}"

        # Fallback de texto plano
        contenido = f"""
Usuario: {user.name}
Email: {user.email}
Enviado el: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC

Mensaje:
{message_text}
"""

        # Crear EmailMessage
        msg = EmailMessage()
        msg['From'] = formataddr(("Soporte Wannapop", self.sender_addr))
        msg['To'] = formataddr(("Administrador", self.contact_addr))
        msg['Subject'] = objeto
        msg.set_content(contenido)

        # Inicializar variables para avatar inline
        avatar_cid = None
        avatar_path = None

        # Avatar inline
        if include_avatar and hasattr(user, 'avatar') and user.avatar:
            avatar_path = os.path.join(self.upload_folder, user.avatar)
            if os.path.isfile(avatar_path):
                avatar_cid = 'useravatar'

        # version HTML
        html_content = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333; margin:0; padding:0;">
<div style="max-width:600px; margin:0 auto; border:1px solid #ddd; border-radius:8px; overflow:hidden; box-shadow:0 0 10px rgba(0,0,0,0.1);">
    
    <!-- Header con avatar y nombre -->
    <div style="background:#4CAF50; color:#fff; padding:20px; display:flex; align-items:center;">
        {'<img src="cid:useravatar" alt="Avatar" style="width:60px; height:60px; border-radius:50%; margin-right:15px;">' if avatar_cid else ''}
        <div>
            <h2 style="margin:0; font-size:20px;">{user.name}</h2>
            <p style="margin:0; font-size:14px;">{user.email}</p>
        </div>
    </div>

    <!-- Cuerpo del mensaje -->
    <div style="padding:20px; background:#fff;">
        <p><strong>Enviado el:</strong> {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
        <p><strong>Mensaje:</strong></p>
        <div style="padding:15px; background:#f9f9f9; border-left:4px solid #4CAF50; border-radius:4px; white-space:pre-wrap;">
            {message_text.replace('<','&lt;').replace('>','&gt;')}
        </div>
    </div>

    <!-- Footer -->
    <div style="padding:10px 20px; background:#f0f0f0; font-size:12px; color:#777; text-align:center;">
        Este mensaje fue enviado desde el formulario de contacto.
    </div>
</div>
</body>
</html>
"""

        msg.add_alternative(html_content, subtype='html')

        # Añadir avatar como related
        if avatar_cid:
            with open(avatar_path, 'rb') as img:
                msg.get_payload()[1].add_related(
                    img.read(),
                    maintype='image',
                    subtype=os.path.splitext(user.avatar)[1][1:] or 'png',
                    cid=f'<{avatar_cid}>'
                )

        # Archivos adjuntos
        if attachments:
            for file_path in attachments:
                if os.path.isfile(file_path):
                    ctype, encoding = mimetypes.guess_type(file_path)
                    if ctype is None or encoding is not None:
                        ctype = 'application/octet-stream'
                    maintype, subtype = ctype.split('/', 1)
                    with open(file_path, 'rb') as f:
                        msg.add_attachment(
                            f.read(),
                            maintype=maintype,
                            subtype=subtype,
                            filename=os.path.basename(file_path)
                        )

        # Enviar mail
        contexto = ssl.create_default_context()
        with smtplib.SMTP(self.sender_server, self.sender_port) as server:
            server.starttls(context=contexto)
            server.login(self.sender_addr, self.sender_pass)
            server.send_message(msg, from_addr=self.sender_addr, to_addrs=self.contact_addr)
