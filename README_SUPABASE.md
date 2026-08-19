# SINIESTRO WEB V9 - Supabase

## 1. Crear las tablas

En Supabase abre **SQL Editor**, pega TODO el contenido de `supabase_schema.sql` y ejecuta el archivo completo.

El script primero elimina las tablas anteriores y las recrea. Esto es intencional: evita el error `column "nosiniestro" does not exist` cuando quedó una tabla vieja con otra estructura.

## 2. Variables de entorno local

Copia `.env.example` como `.env` y coloca tus claves reales.

No subas `.env` a GitHub.

## 3. Instalar y ejecutar

```bat
py -m pip install -r requirements.txt
py app.py
```

## 4. Render

Build Command:

```text
pip install -r requirements.txt
```

Start Command:

```text
gunicorn app:app --bind 0.0.0.0:$PORT
```

En Render agrega:

- `SUPABASE_URL`
- `SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_SECRET_KEY`
- `SUPABASE_JWKS_URL`

El backend usa preferentemente `SUPABASE_SECRET_KEY`.
