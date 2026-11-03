import sqlite3
from datetime import datetime

def conectar_db():
    conexion = sqlite3.connect("gastos.db")
    cursor = conexion.cursor()

    return conexion, cursor


def crear_tabla():
    conexion, cursor = conectar_db()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                monto INTEGER NOT NULL,
                categoria TEXT NOT NULL,
                fecha TEXT NOT NULL
            )
        """)

        conexion.commit()

    finally:
        conexion.close()

def agregar_gasto(descripcion, monto, categoria, fecha):
    conexion, cursor = conectar_db()

    try:
        # Validar descripción
        descripcion = descripcion.strip().capitalize()

        if not descripcion:
            raise ValueError("La descripción no puede estar vacía.")

        # Validar monto
        try:
            monto = int(monto)
            if monto <= 0:
                raise ValueError("El monto debe ser mayor que cero.")
        except (TypeError, ValueError) as error:
            raise ValueError("El monto debe ser un entero positivo.") from error

        # Validar categoría
        categoria = categoria.strip().capitalize()

        if not categoria:
            raise ValueError("La categoría no puede estar vacía.")
        
        # Validar fecha
        try:
            fecha = datetime.strptime(fecha, "%Y-%m-%d").date().isoformat() # .date() hace que solo me devuelva la fecha sin la hora y isoformat() hace que vuelva a convertir la fecha a cadena de texto asi se agrega a la base de datos luego de la validacion
        except (ValueError, TypeError):
            raise ValueError("La fecha debe tener el formato AAAA-MM-DD.")

        # Insertar en la base de datos
        cursor.execute(
            "INSERT INTO gastos (descripcion, monto, categoria, fecha) VALUES (?, ?, ?, ?)",
            (descripcion, monto, categoria, fecha)
        )

        conexion.commit()
        return True
    
    finally:
        conexion.close()
        
def obtener_gastos():
    conexion, cursor = conectar_db()

    try:
        cursor.execute("SELECT * FROM gastos")
        filas_de_gastos = cursor.fetchall()

        return filas_de_gastos
    
    finally:
        conexion.close()

def obtener_total():
    conexion, cursor = conectar_db()

    try:
        cursor.execute("SELECT SUM(monto) FROM gastos")
        total_gastado = cursor.fetchone()[0]

        if total_gastado is None:
            total_gastado = 0

        return total_gastado
    
    finally:
        conexion.close()

def obtener_por_categoria():
    conexion, cursor = conectar_db()

    try:
        cursor.execute("SELECT categoria, SUM(monto) FROM gastos GROUP BY categoria")
        total_por_categoria = cursor.fetchall()

        return total_por_categoria
    
    finally:
        conexion.close()

def eliminar_gasto(id_gasto):
    conexion, cursor = conectar_db()

    try:
        cursor.execute("DELETE FROM gastos WHERE id = ?", (id_gasto,))

        if cursor.rowcount == 0:
            return False

        conexion.commit()
        return True
    
    finally:
        conexion.close()