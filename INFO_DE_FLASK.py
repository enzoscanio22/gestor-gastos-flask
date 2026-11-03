##                                      DIA 7 - 7/10/2026

## Introducción a Flask

## Instalar en la terminal: pip install flask

### ESTRUCTURA
## clases
## funciones
## datos
## rutas

# from flask import Flask

# app = Flask(__name__)   # Crea la aplicación

# class Gasto:
#     def __init__(self, descripcion, monto, categoria, fecha):
#         self.descripcion = descripcion
#         self.monto = monto
#         self.categoria = categoria
#         self.fecha = fecha

#     def __str__(self):
#         return f"{self.fecha} - {self.descripcion} - ${self.monto} - {self.categoria}"

# def calcular_total(gastos):
#     total = 0
#     for gasto in gastos:
#         total += gasto.monto
#     return total

# gastos = []

# gasto_1 = Gasto("Pizza con aceitunas", 1500, "Comida", "15/03/2026")
# gasto_2 = Gasto("UBER - Viaje al trabajo", 500, "Transporte", "17/03/2026")
# gasto_3 = Gasto("Steam - Compra de juego", 2000, "Ocio", "19/03/2026")

# gastos.extend([gasto_1, gasto_2, gasto_3])

# @app.route("/")         # Es un decorador que envuelve a una función para darle un comportamiento especial
# def inicio():
#     return "<h1>Bienvenido a el gestor de gastos</h1>"

# @app.route("/total")
# def total():
#     total_gastos = calcular_total(gastos)
#     return f"<h1>El total es de ${total_gastos}</h1>"

# @app.route("/gastos")
# def ver_gastos():
#     html = "<h1>Lista de gastos</h1><ul>"
#     for gasto in gastos:
#         html += f"<li>{gasto}</li>"
#     html += "</ul>"
#     return html

# if __name__ == "__main__":      # app.run(debug=True) arranca un servidor local en tu computadora
#     app.run(debug = True)       # debug=True hace que se reinicie solo cada vez que se guardan cambios, y muestra errores más detallados en el navegador