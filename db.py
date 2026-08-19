import os
from datetime import date
from dotenv import load_dotenv
import requests

# Carga .env localmente.
# En Render se usan las variables configuradas en Environment.
load_dotenv()

from clases.Siniestro import Siniestro


# ============================================================
# SUPABASE
# ============================================================

SUPABASE_URL = os.getenv(
    "SUPABASE_URL",
    "https://uheewrxpwsogknqgjqwe.supabase.co"
).rstrip("/")

SUPABASE_KEY = (
    os.getenv("SUPABASE_SECRET_KEY")
    or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    or os.getenv("SUPABASE_PUBLISHABLE_KEY")
)

SUPABASE_JWKS_URL = os.getenv(
    "SUPABASE_JWKS_URL",
    f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"
)


if not SUPABASE_URL:
    raise RuntimeError(
        "Falta SUPABASE_URL en las variables de entorno."
    )

if not SUPABASE_KEY:
    raise RuntimeError(
        "Falta SUPABASE_SECRET_KEY "
        "(o SUPABASE_PUBLISHABLE_KEY) "
        "en las variables de entorno."
    )


# ============================================================
# REST API
# ============================================================

REST_URL = f"{SUPABASE_URL}/rest/v1"


_session = requests.Session()

_session.headers.update({
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json",
})


# ============================================================
# ERROR SUPABASE
# ============================================================

class SupabaseError(RuntimeError):
    pass


# ============================================================
# REQUEST
# ============================================================

def _request(
    method,
    table,
    *,
    params=None,
    json=None,
    headers=None
):
    url = f"{REST_URL}/{table}"

    try:
        response = _session.request(
            method,
            url,
            params=params,
            json=json,
            headers=headers,
            timeout=20
        )

    except requests.RequestException as e:
        raise SupabaseError(
            f"No se pudo conectar con Supabase: {e}"
        )

    if not response.ok:

        try:
            detail = response.json()
        except Exception:
            detail = response.text

        raise SupabaseError(
            f"Supabase {response.status_code}: {detail}"
        )

    if not response.content:
        return []

    try:
        return response.json()

    except Exception:
        return []


# ============================================================
# SCHEMA
# ============================================================

def ensure_schema():
    """
    La estructura se administra mediante el SQL
    configurado directamente en Supabase.
    """
    return True


# ============================================================
# CONEXIÓN
# ============================================================

def ensure_connection():

    try:

        _request(
            "GET",
            "aseguradoras",
            params={
                "select": "id_aseguradora",
                "limit": "1"
            }
        )

        return True

    except Exception as e:

        print("Supabase:", e)

        return False


# ============================================================
# ASEGURADORA
# ============================================================

def _aseg_id(nombre):

    if not nombre:
        return None

    rows = _request(
        "GET",
        "aseguradoras",
        params={
            "select": "id_aseguradora",
            "nombre": f"eq.{nombre}",
            "limit": "1"
        }
    )

    if rows:
        return rows[0]["id_aseguradora"]

    rows = _request(
        "POST",
        "aseguradoras",
        params={
            "select": "id_aseguradora"
        },
        json={
            "nombre": nombre,
            "activo": True
        },
        headers={
            "Prefer": "return=representation"
        }
    )

    return rows[0]["id_aseguradora"]


def _all_aseguradoras():

    return _request(
        "GET",
        "aseguradoras",
        params={
            "select": "id_aseguradora,nombre,activo",
            "activo": "eq.true",
            "order": "nombre.asc"
        }
    )


# ============================================================
# CONVERTIR REGISTRO
# ============================================================

def _row_base(r, aseguradoras):

    aid = r.get("id_aseguradora")

    aseguradora = aseguradoras.get(aid)

    # Compatibilidad por si Supabase devuelve el nombre
    # mediante un join.
    if not aseguradora:

        join = r.get("aseguradoras")

        if isinstance(join, dict):
            aseguradora = join.get("nombre")

    sin = Siniestro(
        modelo=r.get("modelo"),
        color=r.get("color"),
        placas=r.get("placas"),
        nosiniestro=r.get("nosiniestro"),
        fecha_actualizacion=r.get(
            "fecha_actualizacion"
        ),
        orden=r.get("orden") or 0,
        tipo_cliente=r.get(
            "tipo_cliente"
        ) or (
            "aseguradora"
            if aseguradora
            else "particular"
        ),
        aseguradora=aseguradora,
        terminado=bool(
            r.get("terminado")
        ),
        refacciones=r.get(
            "refacciones"
        ) or 0,
        mano_obra=r.get(
            "mano_obra"
        ) or 0,
        telefono=r.get("telefono"),
        estatus_taller=r.get(
            "estatus_taller"
        ) or "valuacion",
        fecha_estatus_taller=r.get(
            "fecha_estatus_taller"
        ),
    )

    return {
        "id_siniestro":
            r.get("id_siniestro"),

        "modelo":
            sin.get_modelo(),

        "color":
            sin.get_color(),

        "placas":
            sin.get_placas(),

        "nosiniestro":
            sin.get_nosiniestro(),

        "aseguradora":
            sin.get_aseguradora(),

        "terminado":
            sin.get_terminado(),

        "refacciones":
            sin.get_refacciones(),

        "mano_obra":
            sin.get_mano_obra(),

        "telefono":
            sin.get_telefono(),

        "orden":
            sin.orden,

        "tipo_cliente":
            sin.get_tipo_cliente(),

        "tipo_cliente_label":
            sin.get_tipo_cliente_label(),

        "estatus_taller":
            sin.get_estatus_taller(),

        "estatus_taller_label":
            sin.get_estatus_taller_label(),

        "fecha_estatus_taller":
            sin.get_fecha_estatus_taller_str(),

        "dias_en_estatus_taller":
            sin.get_dias_en_estatus_taller(),

        "fecha_actualizacion":
            sin.get_fecha_str(),

        "dias_desde_actualizacion":
            sin.get_dias_desde_actualizacion(),

        "dias_habiles":
            sin.get_dias_desde_actualizacion(),

        "total":
            sin.get_total(),

        "status_color":
            "terminados"
            if sin.get_terminado()
            else sin.get_status_color(),

        "status_emoji":
            "🔵"
            if sin.get_terminado()
            else sin.get_status_emoji(),

        "status_label":
            "Terminado"
            if sin.get_terminado()
            else sin.get_status_label(),
    }


# ============================================================
# ASEGURADORAS
# ============================================================

def get_aseguradoras():
    return _all_aseguradoras()


# ============================================================
# OBTENER TODOS
# ============================================================

def fetch_all():

    rows = _request(
        "GET",
        "siniestros",
        params={
            "select": "*",
            "order": "orden.asc,id_siniestro.asc",
        }
    )

    aseguradoras = {
        x["id_aseguradora"]: x["nombre"]
        for x in _all_aseguradoras()
    }

    return [
        _row_base(x, aseguradoras)
        for x in rows
    ]


# ============================================================
# OBTENER UNO
# ============================================================

def fetch_one(key):

    rows = _request(
        "GET",
        "siniestros",
        params={
            "select": "*",
            "nosiniestro": f"eq.{str(key)}",
            "limit": "1"
        }
    )

    if not rows:
        return None

    aseguradoras = {
        x["id_aseguradora"]: x["nombre"]
        for x in _all_aseguradoras()
    }

    return _row_base(
        rows[0],
        aseguradoras
    )


# ============================================================
# INSERTAR
# ============================================================

def insert_siniestro(d):

    tipo = (
        "aseguradora"
        if str(
            d.get("tipo_cliente")
            or "particular"
        ).strip().lower()
        == "aseguradora"
        else "particular"
    )

    aid = (
        _aseg_id(d.get("aseguradora"))
        if tipo == "aseguradora"
        else None
    )

    if tipo == "aseguradora" and not d.get("aseguradora"):

        raise ValueError(
            "La aseguradora es obligatoria cuando "
            "el tipo de cliente es aseguradora"
        )

    no = str(
        d.get("nosiniestro") or ""
    ).strip().upper()

    hoy = date.today().isoformat()

    payload = {

        "nosiniestro":
            no,

        "orden":
            int(d.get("orden") or 0),

        "tipo_cliente":
            tipo,

        "modelo":
            d["modelo"],

        "color":
            d["color"],

        "placas":
            d["placas"],

        "fecha_actualizacion":
            d.get("fecha_actualizacion")
            or hoy,

        "id_aseguradora":
            aid,

        "refacciones":
            float(
                d.get("refacciones") or 0
            ),

        "mano_obra":
            float(
                d.get("mano_obra") or 0
            ),

        "telefono":
            d.get("telefono"),

        "estatus_taller":
            d.get("estatus_taller")
            or "valuacion",

        "fecha_estatus_taller":
            d.get("fecha_estatus_taller")
            or hoy,

        "terminado":
            bool(
                d.get("terminado")
            ),
    }

    _request(
        "POST",
        "siniestros",
        json=payload,
        headers={
            "Prefer": "return=representation"
        }
    )

    return fetch_one(no)


# ============================================================
# ACTUALIZAR
# ============================================================

def update_siniestro(key, d):

    actual_rows = _request(
        "GET",
        "siniestros",
        params={
            "select": "*",
            "nosiniestro":
                f"eq.{str(key)}",
            "limit": "1"
        }
    )

    if not actual_rows:
        return None

    actual = actual_rows[0]

    tipo_nuevo = str(
        d.get("tipo_cliente")
        or actual.get("tipo_cliente")
        or (
            "aseguradora"
            if actual.get("id_aseguradora")
            else "particular"
        )
    ).strip().lower()

    if tipo_nuevo not in {
        "particular",
        "aseguradora"
    }:
        tipo_nuevo = "particular"

    payload = {
        "tipo_cliente": tipo_nuevo
    }

    if (
        "tipo_cliente" in d
        or "aseguradora" in d
    ):

        nombre = (
            d.get("aseguradora")
            if tipo_nuevo == "aseguradora"
            else None
        )

        if (
            tipo_nuevo == "aseguradora"
            and not nombre
        ):
            raise ValueError(
                "La aseguradora es obligatoria cuando "
                "el tipo de cliente es aseguradora"
            )

        payload["id_aseguradora"] = (
            _aseg_id(nombre)
            if nombre
            else None
        )

    for key_name in (
        "orden",
        "modelo",
        "color",
        "placas",
        "telefono",
        "fecha_actualizacion",
        "terminado"
    ):

        if key_name in d:

            value = d.get(key_name)

            if key_name == "orden":

                try:
                    value = int(value or 0)

                except (
                    TypeError,
                    ValueError
                ):
                    value = 0

            if key_name == "terminado":
                value = bool(value)

            payload[key_name] = value

    for key_name in (
        "refacciones",
        "mano_obra"
    ):

        if key_name in d:

            try:
                payload[key_name] = float(
                    d.get(key_name) or 0
                )

            except (
                TypeError,
                ValueError
            ):
                payload[key_name] = 0

    if "estatus_taller" in d:

        nuevo = str(
            d.get("estatus_taller")
            or "valuacion"
        ).strip()

        anterior = (
            actual.get("estatus_taller")
            or "valuacion"
        )

        payload["estatus_taller"] = nuevo

        if nuevo != anterior:

            payload["fecha_estatus_taller"] = (
                d.get("fecha_estatus_taller")
                or date.today().isoformat()
            )

        elif d.get("fecha_estatus_taller"):

            payload["fecha_estatus_taller"] = (
                d["fecha_estatus_taller"]
            )

    elif d.get("fecha_estatus_taller"):

        payload["fecha_estatus_taller"] = (
            d["fecha_estatus_taller"]
        )

    _request(
        "PATCH",
        "siniestros",
        params={
            "nosiniestro":
                f"eq.{str(key)}"
        },
        json=payload,
        headers={
            "Prefer": "return=representation"
        }
    )

    return fetch_one(key)


# ============================================================
# ELIMINAR
# ============================================================

def delete_siniestro(key):

    rows = _request(
        "GET",
        "siniestros",
        params={
            "select": "id_siniestro",
            "nosiniestro":
                f"eq.{str(key)}",
            "limit": "1"
        }
    )

    if not rows:
        return False

    _request(
        "DELETE",
        "siniestros",
        params={
            "nosiniestro":
                f"eq.{str(key)}"
        }
    )

    return True


# ============================================================
# AGREGAR COMENTARIO
# ============================================================

def add_comment(key, text):

    rows = _request(
        "GET",
        "siniestros",
        params={
            "select": "id_siniestro",
            "nosiniestro":
                f"eq.{str(key)}",
            "limit": "1"
        }
    )

    if not rows:
        return None

    created = _request(
        "POST",
        "comentarios",
        json={
            "id_siniestro":
                rows[0]["id_siniestro"],

            "comentario":
                text
        },
        headers={
            "Prefer": "return=representation"
        }
    )

    return (
        created[0]["id_comentario"]
        if created
        else None
    )


# ============================================================
# OBTENER COMENTARIOS
# ============================================================

def comments(key):

    rows = _request(
        "GET",
        "siniestros",
        params={
            "select": "id_siniestro",
            "nosiniestro":
                f"eq.{str(key)}",
            "limit": "1"
        }
    )

    if not rows:
        return []

    return _request(
        "GET",
        "comentarios",
        params={
            "select":
                "id_comentario,"
                "id_siniestro,"
                "comentario,"
                "fecha_comentario",

            "id_siniestro":
                f"eq.{rows[0]['id_siniestro']}",

            "order":
                "fecha_comentario.desc",
        }
    )