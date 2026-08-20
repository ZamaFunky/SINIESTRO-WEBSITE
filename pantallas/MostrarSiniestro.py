from flask import render_template_string, request

from __main__ import app
from pantallas.template_base import (
    get_css_link,
    get_header,
    get_footer,
    siniestro_row_html,
    get_aseguradora_select_html,
)


@app.get('/ConsultarSiniestro')
def ConsultarSiniestro():
    return render_template_string("""<!doctype html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Consultar Siniestros — Mazda</title>
  {{ css|safe }}
</head>

<body>

{{ header|safe }}

<div class="mazda-container">
  <div class="mazda-card">

    <h2>Consultar Siniestros</h2>

    <p style="color:#6b6b8a; margin-bottom:1.5rem;">
      Busque por <strong>Aseguradora</strong> o <strong>Placas</strong>.
      Si llena ambos, se mostrarán resultados que coincidan con cualquiera
      de los dos. Use los demás campos para filtrar aún más.
    </p>

    <form method="post" action="/consultar-siniestro">

      <div class="form-row">

        <div class="form-group">
          <label for="aseguradora">Aseguradora</label>
          {{ aseguradora_html|safe }}
        </div>

        <div class="form-group">
          <label for="placas">Placas</label>
          <input
            id="placas"
            name="placas"
            type="text"
            placeholder="Ej: ABC-1234"
          >
        </div>

      </div>

      <div class="form-group">
        <label for="nosiniestro">No. Siniestro</label>
        <input
          id="nosiniestro"
          name="nosiniestro"
          type="text"
          placeholder="Ej: SIN-001"
        >
      </div>

      <div class="btn-group">

        <button type="submit" class="btn btn-primary">
          &#x1F50D; Consultar
        </button>

        <a href="/" class="btn btn-outline">
          &#x2190; Volver
        </a>

      </div>

    </form>

  </div>
</div>

{{ footer|safe }}

</body>
</html>
""",
        css=get_css_link(),
        header=get_header(
            "Consultar Siniestro",
            active_page="consultar"
        ),
        footer=get_footer(),
        aseguradora_html=get_aseguradora_select_html()
    )


@app.post('/consultar-siniestro')
def consultar_form_siniestro():

    # ==============================
    # DATOS DEL FORMULARIO
    # ==============================

    nosiniestro = request.form.get('nosiniestro')
    placas = request.form.get('placas')
    aseguradora = request.form.get('aseguradora')

    # ==============================
    # FILTROS EXACTOS (AND)
    # ==============================

    filtros_and = {}

    nos = (
        str(nosiniestro).strip()
        if nosiniestro is not None
        and str(nosiniestro).strip() != ''
        else None
    )

    if nos is not None:
        filtros_and["nosiniestro"] = nos

    # ==============================
    # FILTROS OR
    # ASEGURADORA / PLACAS
    # ==============================

    pl = (
        str(placas).strip()
        if placas is not None
        and str(placas).strip() != ''
        else None
    )

    aseg = (
        str(aseguradora).strip()
        if aseguradora is not None
        and str(aseguradora).strip()
        not in ('', 'Seleccionar aseguradora...')
        else None
    )

    # ==============================
    # OBTENER SINIESTROS
    # ==============================

    siniestros_mem = getattr(app, 'SINIESTROS', {})

    resultados = []

    for sin in siniestros_mem.values():

        # --------------------------------
        # Filtros AND
        # --------------------------------

        ok = True

        for k, v in filtros_and.items():

            if str(sin.get(k, "")).strip() != v:
                ok = False
                break

        if not ok:
            continue

        # --------------------------------
        # Filtros OR
        # --------------------------------

        if aseg is not None or pl is not None:

            coincide_or = False

            # Aseguradora
            if (
                aseg is not None
                and str(
                    sin.get("aseguradora", "")
                ).strip().lower()
                == aseg.lower()
            ):
                coincide_or = True

            # Placas
            if (
                pl is not None
                and str(
                    sin.get("placas", "")
                ).strip().lower()
                == pl.lower()
            ):
                coincide_or = True

            if not coincide_or:
                continue

        # --------------------------------
        # Agregar resultado
        # --------------------------------

        resultados.append(sin)

    # ==============================
    # GENERAR FILAS DE LA TABLA
    # ==============================

    rows_html = ""

    for sin in resultados:
        rows_html += siniestro_row_html(sin)

    # ==============================
    # SIN RESULTADOS
    # ==============================

    if not resultados:

        rows_html = """
        <tr>
          <td
            colspan="8"
            class="text-center"
            style="
              padding:2rem;
              color:#6b6b8a;
            "
          >
            No se encontraron siniestros
            con los criterios indicados.
          </td>
        </tr>
        """

    # ==============================
    # CRITERIOS APLICADOS
    # ==============================

    criterios_list = []

    if "nosiniestro" in filtros_and:

        criterios_list.append(
            f"<strong>No. Siniestro</strong>: "
            f"{filtros_and['nosiniestro']}"
        )

    if aseg:

        criterios_list.append(
            f"<strong>Aseguradora</strong>: {aseg}"
        )

    if pl:

        criterios_list.append(
            f"<strong>Placas</strong>: {pl}"
        )

    criterios_str = (
        " | ".join(criterios_list)
        if criterios_list
        else "Ninguno (mostrando todos)"
    )

    # ==============================
    # RESULTADOS
    # ==============================

    return render_template_string("""
<!doctype html>

<html lang="es">

<head>

  <meta charset="UTF-8">

  <meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
  >

  <title>Resultados — Mazda</title>

  {{ css|safe }}

</head>

<body>

{{ header|safe }}

<div class="mazda-container">

  <div class="mazda-card">

    <h2>Resultados de la Consulta</h2>

    <p
      style="
        color:#6b6b8a;
        margin-bottom:1rem;
      "
    >

      Criterios aplicados:
      {{ criterios_str|safe }}

      &nbsp;|&nbsp;

      Total:
      <strong>{{ total }}</strong>
      resultado(s)

    </p>

    <div style="overflow-x:auto;">

      <table class="mazda-table">

        <thead>

          <tr>

            <th>No. Siniestro</th>

            <th>Modelo</th>

            <th>Color</th>

            <th>Placas</th>

            <th>Aseguradora</th>

            <th>Ult. Actualización</th>

            <th>Teléfono</th>

            <th>Estado</th>

          </tr>

        </thead>

        <tbody>

          {{ rows|safe }}

        </tbody>

      </table>

    </div>

    <div class="btn-group">

      <a
        href="/ConsultarSiniestro"
        class="btn btn-secondary"
      >
        &#x1F50D; Nueva consulta
      </a>

      <a
        href="/"
        class="btn btn-outline"
      >
        &#x2190; Volver
      </a>

    </div>

  </div>

</div>

{{ footer|safe }}

</body>

</html>
""",
        css=get_css_link(),

        header=get_header(
            "Resultados",
            active_page="consultar"
        ),

        footer=get_footer(),

        rows=rows_html,

        total=len(resultados),

        criterios_str=criterios_str
    )