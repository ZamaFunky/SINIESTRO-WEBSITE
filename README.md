# SINIESTROWEB v9 — Supabase + Flask

Proyecto migrado de MySQL a Supabase. El CRUD, comentarios, aseguradoras, tablero y semáforo siguen funcionando desde Flask.

## 1. Crear la base de datos en Supabase

1. Abre tu proyecto de Supabase.
2. Ve a **SQL Editor**.
3. Ejecuta completo `supabase_schema.sql`.

No ejecutes `database.sql` porque ese archivo corresponde a MySQL.

## 2. Variables de entorno

Copia `.env.example` a `.env` para trabajar localmente y configura. El proyecto ya carga automáticamente `.env` gracias a `python-dotenv`:

```bat
copy .env.example .env
```

Después edita `.env` y coloca tus valores reales:

- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_SECRET_KEY`
- `SUPABASE_JWKS_URL`

La aplicación usa la **SUPABASE_SECRET_KEY únicamente en el backend** para acceder a Supabase. No la pongas en JavaScript ni en el repositorio.

## 3. Instalar y ejecutar localmente

```bat
py -m venv venv
venv\Scriptsctivate
py -m pip install -r requirements.txt
py app.py
```

Abre `http://127.0.0.1:5000/`.

## 4. Render

Configura el servicio como **Web Service**:

- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:app`

Agrega las variables de entorno de Supabase en Render.

La aplicación escucha el puerto que proporciona Render mediante `PORT`. **En Render debes agregar las 4 variables en Environment; Render no necesita ni debe recibir un archivo `.env` con secretos.**

## 5. Verificar conexión

Con el servidor iniciado:

`/estado-supabase`

Debe responder:

```json
{"supabase":"conectado"}
```

## 6. Notas

- `db.py` ya no usa `mysql.connector`.
- Los datos se leen y escriben mediante la API REST de Supabase.
- `db_store.py` conserva la interfaz que usa el resto del proyecto.
- Se eliminó la dependencia de MySQL para el despliegue.
- `database.sql` queda como referencia histórica para MySQL.
