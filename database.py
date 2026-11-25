import sqlite3
from datetime import datetime

def conectar_db():
    conexion = sqlite3.connect("gastos.db")
    conexion.execute("PRAGMA foreign_keys = ON")
    cursor = conexion.cursor()

    return conexion, cursor

def crear_tabla():
    conexion, cursor = conectar_db()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                monto INTEGER NOT NULL,
                categoria_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id)
            )
        """)

        conexion.commit()

    finally:
        conexion.close()

def validacion_de_datos(descripcion, monto, categoria, fecha):

    # Validar descripción
    descripcion = descripcion.strip().capitalize()

    if not descripcion:
        raise ValueError("La descripción no puede estar vacía.")

    # Validar monto
    try:
        monto = int(monto)
    except (TypeError, ValueError) as error:
        raise ValueError("El monto debe ser un entero positivo.") from error
    
    if monto <= 0:
        raise ValueError("El monto debe ser mayor que cero.")

    # Validar categoría
    categoria = categoria.strip().capitalize()

    if not categoria:
        raise ValueError("La categoría no puede estar vacía.")
    
    # Validar fecha
    try:
        fecha = datetime.strptime(fecha, "%Y-%m-%d").date().isoformat()

    except (ValueError, TypeError):
        raise ValueError("La fecha debe tener el formato AAAA-MM-DD.")

    return descripcion, monto, categoria, fecha

def insertar_categoria_a_la_tabla(categoria, cursor):

    cursor.execute("""
        INSERT OR IGNORE INTO categorias (nombre)
        VALUES (?)
    """, (categoria,))
    
    cursor.execute("""
        SELECT id FROM categorias
        WHERE nombre = ?
    """, (categoria,))

    resultado = cursor.fetchone()

    if resultado is None:
        raise ValueError("No se encontró la categoría.")

    categoria_id = resultado[0]
    return categoria_id

def construir_filtros(categoria_id = None, desde = None, hasta = None, alias = ""):
    condiciones = []
    parametros = []

    prefijo = f"{alias}." if alias else ""

    if categoria_id:
        condiciones.append(f"{prefijo}categoria_id = ?")
        parametros.append(categoria_id)

    if desde:
        condiciones.append(f"{prefijo}fecha >= ?")
        parametros.append(desde)

    if hasta:
        condiciones.append(f"{prefijo}fecha <= ?")
        parametros.append(hasta)

    return condiciones, parametros

def agregar_gasto(descripcion, monto, categoria, fecha):
    descripcion, monto, categoria, fecha = validacion_de_datos(descripcion, monto, categoria, fecha)
    conexion, cursor = conectar_db()
    
    try:
        categoria_id = insertar_categoria_a_la_tabla(categoria, cursor)

        cursor.execute("""
            INSERT INTO gastos (descripcion, monto, categoria_id, fecha)
            VALUES (?, ?, ?, ?)
        """, (descripcion, monto, categoria_id, fecha))

        conexion.commit()
        return True

    except sqlite3.Error as error:
        conexion.rollback()
        raise RuntimeError(f"Error al insertar gasto: {error}") from error
    
    finally:
        conexion.close()
        
def obtener_gastos(categoria_id = None, desde = None, hasta = None):
    conexion, cursor = conectar_db()

    try:
        condiciones, parametros = construir_filtros(categoria_id, desde, hasta, alias = "g")

        if desde is not None and hasta is not None:
            if hasta < desde:
                raise ValueError("La fecha final no puede ser anterior a la fecha inicial.")

        consulta = """
            SELECT g.id, g.descripcion, g.monto, c.nombre, g.fecha
            FROM gastos g
            INNER JOIN categorias c
            ON g.categoria_id = c.id
        """

        if condiciones:
            consulta += " WHERE " + " AND ".join(condiciones)

        consulta += " ORDER BY g.fecha"

        cursor.execute(consulta, parametros)

        filas_de_gastos = cursor.fetchall()

        return filas_de_gastos
    
    finally:
        conexion.close()

def obtener_total(categoria_id = None, desde = None, hasta = None):
    conexion, cursor = conectar_db()

    try:
        condiciones, parametros = construir_filtros(categoria_id, desde, hasta, alias = "g")

        consulta = "SELECT COALESCE(SUM(monto), 0) FROM gastos g"

        if condiciones:
            consulta += " WHERE " + " AND ".join(condiciones)

        cursor.execute(consulta, parametros)

        total_gastado = cursor.fetchone()[0]

        if total_gastado is None:
            total_gastado = 0

        return total_gastado
    
    finally:
        conexion.close()

def obtener_por_categoria(categoria_id = None, desde = None, hasta = None):
    conexion, cursor = conectar_db()

    try:
        condiciones, parametros = construir_filtros(categoria_id, desde, hasta, alias = "g")

        consulta = """
            SELECT c.nombre AS categoria, COALESCE(SUM(g.monto), 0) AS total
            FROM categorias c
            LEFT JOIN gastos g
            ON c.id = g.categoria_id
        """

        if condiciones:
            consulta += " WHERE " + " AND ".join(condiciones)

        consulta += """
            GROUP BY c.id, c.nombre
            ORDER BY c.nombre
        """

        cursor.execute(consulta, parametros)

        total_por_categoria = cursor.fetchall()

        return total_por_categoria
    
    finally:
        conexion.close()

def obtener_lista_de_categorias():
    conexion, cursor = conectar_db()

    try:
        cursor.execute("SELECT id, nombre FROM categorias ORDER BY nombre")
        lista_de_categorias = cursor.fetchall()

        return lista_de_categorias

    finally:
        conexion.close()

def obtener_gasto_por_id(id_gasto):
    conexion, cursor = conectar_db()

    try:
        cursor.execute("""
            SELECT g.id, g.descripcion, g.monto, c.nombre, g.fecha
            FROM gastos g
            INNER JOIN categorias c
            ON g.categoria_id = c.id
            WHERE g.id = ?
        """, (id_gasto,))

        fila_del_gasto = cursor.fetchone()

        return fila_del_gasto

    finally:
        conexion.close()
    

def actualizar(id_gasto, descripcion, monto, categoria, fecha):
    descripcion, monto, categoria, fecha = validacion_de_datos(descripcion, monto, categoria, fecha)
    conexion, cursor = conectar_db()

    try:
        categoria_id = insertar_categoria_a_la_tabla(categoria, cursor)

        cursor.execute("""
            UPDATE gastos
            SET descripcion = ?, monto = ?, categoria_id = ?, fecha = ?
            WHERE id = ?
        """, (descripcion, monto, categoria_id, fecha, id_gasto))

        if cursor.rowcount == 0:
            raise ValueError("No se encontró el gasto.")

        conexion.commit()
        return True

    except sqlite3.Error as error:
        conexion.rollback()
        raise RuntimeError(f"Error al actualizar gasto: {error}") from error

    except Exception:
        conexion.rollback()
        raise

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

    except sqlite3.Error as error:
        conexion.rollback()
        raise RuntimeError(f"Error al eliminar el gasto: {error}") from error
    
    finally:
        conexion.close()

def migrar_base_datos():
    conexion, cursor = conectar_db()

    try:
        # Iniciar transacción
        cursor.execute("BEGIN")

        # 1. Renombrar tabla vieja
        cursor.execute("""
            ALTER TABLE gastos
            RENAME TO gastos_viejos
        """)

        # 2. Crear tabla categorias
        cursor.execute("""
            CREATE TABLE categorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        """)

        # 3. Crear tabla de gastos
        cursor.execute("""
            CREATE TABLE gastos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                descripcion TEXT NOT NULL,
                monto INTEGER NOT NULL,
                categoria_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                FOREIGN KEY (categoria_id) REFERENCES categorias(id)
            )
        """)

        # 4. Migrar categorias sin repetirlas
        cursor.execute("""
            INSERT INTO categorias (nombre)
            SELECT DISTINCT TRIM(categoria)
            FROM gastos_viejos
            WHERE categoria IS NOT NULL
            AND TRIM(categoria) != ''
        """)

        # 5. Migrar los gastos recuperando el nuevo categoria_id
        cursor.execute("""
            INSERT INTO gastos (
                id,
                descripcion,
                monto,
                categoria_id,
                fecha
            )
            SELECT
                gv.id,
                gv.descripcion,
                gv.monto,
                c.id,
                gv.fecha
            FROM gastos_viejos gv
            INNER JOIN categorias c
            ON TRIM(gv.categoria) = c.nombre
        """)

        # 6. Comprobación de que no se hayan perdido registros
        cursor.execute("SELECT COUNT(*) FROM gastos_viejos")
        cantidad_vieja = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM gastos")
        cantidad_nueva = cursor.fetchone()[0]

        if cantidad_vieja != cantidad_nueva:
            raise ValueError("La cantidad de gastos migrados no coincide.")

        # 7. Confirmación de cambios
        conexion.commit()
        return True

    except sqlite3.Error as error:
        conexion.rollback()
        raise RuntimeError(f"Error al migrar la tabla: {error}") from error

    finally:
        conexion.close()

def eliminar_tabla():
    conexion, cursor = conectar_db()

    try:
        cursor.execute("DROP TABLE IF EXISTS gastos_viejos")

        conexion.commit()

    except sqlite3.Error as error:
        conexion.rollback()
        raise RuntimeError(f"Error al eliminar la tabla: {error}") from error

    finally:
        conexion.close()

