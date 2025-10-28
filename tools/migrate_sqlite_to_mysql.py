from sqlalchemy import create_engine, MetaData
from os import environ, path
import os
from dotenv import load_dotenv

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))


# 1️⃣ Conectar SQLite
sqlite_engine = create_engine(
    "sqlite:///" + os.path.join(os.path.dirname(__file__), "sqlite", "database.db")
)

# 2️⃣ Conectar MySQL
mysql_engine = create_engine(environ.get("DATABASE_URI"))

# 3️⃣ Cargar MetdaData
metadata = MetaData()
metadata.reflect(bind=sqlite_engine)

# 4️⃣ Crear tablas en MySQL
metadata.create_all(mysql_engine)

# 5️⃣ Migrar los datos
with sqlite_engine.connect() as sqlite_conn:
    with mysql_engine.connect() as mysql_conn:
        for table in metadata.sorted_tables:
            print(f"📦 Migracion de tabla: {table.name}")
            
            # Leer rows
            result = sqlite_conn.execute(table.select())
            rows = result.fetchall()

            # Convertir a diccionarios
            dict_rows = [dict(row._mapping) for row in rows]

            if dict_rows:
                mysql_conn.execute(table.insert(), dict_rows)
                print(f"✅ {len(dict_rows)} columnas insertadas en {table.name}")

        mysql_conn.commit()

print("🎉 Migrcion finalizada con exito!")
