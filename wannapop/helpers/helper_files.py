import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def save_image(file, upload_folder=None):
    """
    Guarda archivo en /static/uploads y devuelve solo filename
    """
    if not file:
        return None

    # Carpeta destino (defecto = static/uploads)
    if not upload_folder:
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')

    # Extensión y nombre único
    ext = os.path.splitext(file.filename)[1]
    filename = secure_filename(f"{uuid.uuid4().hex}{ext}")

    # Crear carpeta si no existe
    os.makedirs(upload_folder, exist_ok=True)

    # Ruta final
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    return filename
