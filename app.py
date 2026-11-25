from flask import Flask
from flask import render_template
from flask import request, redirect, url_for
from flask import abort
from datetime import datetime
import database as db

app = Flask(__name__)

## Creación de la base de datos (Comentar esta linea de codigo cuando se quiera hacer una migracion de una base de datos)
db.crear_tabla()

@app.route("/")
def inicio():
    error = None
    gastos = []

    categoria_id = request.args.get("categoria_id")
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")

    if categoria_id and not categoria_id.isdigit():
        abort(400)

    try:
        if desde:
            datetime.strptime(desde, "%Y-%m-%d")

        if hasta:
            datetime.strptime(hasta, "%Y-%m-%d")

    except ValueError:
        abort(400)

    try:
        gastos = db.obtener_gastos(categoria_id, desde, hasta)
        total_gastado = db.obtener_total(categoria_id, desde, hasta)
        total_por_categoria = db.obtener_por_categoria(categoria_id, desde, hasta)
        categorias = db.obtener_lista_de_categorias()

    except ValueError as e:
        error = str(e)

    return render_template(
        "index.html",
        gastos = gastos,
        error = error,
        total_gastado = total_gastado,
        total_por_categoria = total_por_categoria,
        categorias = categorias,
        categoria_id = categoria_id,
        desde = desde,
        hasta = hasta
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
        descripcion = request.form.get("descripcion", "")
        monto = request.form.get("monto", "")
        categoria = request.form.get("categoria", "")
        fecha = request.form.get("fecha", "")

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

@app.route("/editar/<int:id_gasto>", methods = ["GET", "POST"])
def editar_gasto(id_gasto):
    error = None
    gasto = db.obtener_gasto_por_id(id_gasto)

    if gasto is None:
        abort(404)

    descripcion = gasto[1]
    monto = gasto[2]
    categoria = gasto[3]
    fecha = gasto[4]

    if request.method == "POST":
        descripcion = request.form.get("descripcion", "")
        monto = request.form.get("monto", "")
        categoria = request.form.get("categoria", "")
        fecha = request.form.get("fecha", "")

        try:
            db.actualizar(id_gasto, descripcion, monto, categoria, fecha)
            return redirect(url_for("inicio"))
        
        except ValueError as e:
            print(f"Error: {e}")
            error = str(e)

    return render_template(
        "editar.html",
        gasto = gasto,
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

@app.errorhandler(400)
def solicitud_incorrecta(error):
    return render_template("400.html"), 400

@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template("404.html"), 404

@app.errorhandler(500)
def error_interno(error):
    return render_template("500.html"), 500

if __name__ == "__main__":
    app.run(debug = True)