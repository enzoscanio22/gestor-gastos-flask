from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
import html
import database as db

app = Flask(__name__)
db.crear_tabla()

@app.route("/")
def inicio():

    gastos = db.obtener_gastos()
    total_gastado = db.obtener_total()
    total_por_categoria = db.obtener_por_categoria()

    return render_template(
        "index.html",
        gastos = gastos,
        total_gastado = total_gastado,
        total_por_categoria = total_por_categoria
    )

@app.template_filter("formato_numerico_html")
def filtro_formato_numerico_html(value):
    try:
        return f"{int(value):,}".replace(",", ".")
    except (ValueError, TypeError):
        return value

@app.route("/agregar", methods = ["GET", "POST"])
def agregar_gasto():
    error = None
    descripcion = monto = categoria = fecha = ""

    if request.method == "POST":
        descripcion = html.escape(request.form["descripcion"])
        monto = request.form["monto"]
        categoria = html.escape(request.form["categoria"])
        fecha = request.form["fecha"]

        if not descripcion.strip():
            error = "La descripción es obligatoria"
            descripcion = ""

        elif float(monto) <= 0:
            error = "El monto debe de ser un número entero mayor a cero"
            monto = ""

        elif not categoria.strip():
            error = "La categoria es obligatoria"
            categoria = ""

        if not error:
            try:
                db.agregar_gasto(descripcion, monto, categoria, fecha)
                return redirect(url_for("inicio"))
            except ValueError as e:
                print(f"Error: {e}")
                error = str(e)

    return render_template(
        "agregar.html",
        error = error,
        descripcion = descripcion,
        monto = monto,
        categoria = categoria,
        fecha = fecha
    )

@app.route("/eliminar", methods = ["GET", "POST"])
def eliminar_gasto():

    if request.method == "POST":
        id_gasto = request.form["id_gasto"]
        db.eliminar_gasto(id_gasto)

        return redirect(url_for("eliminar_gasto"))

    gastos = db.obtener_gastos()
    return render_template("eliminar.html", gastos = gastos)

if __name__ == "__main__":
    app.run(debug = True)