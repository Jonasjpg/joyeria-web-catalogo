from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
import json
import os
import sqlite3

app = Flask(__name__)

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "img", "productos")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def allowed_file(filename):
    return "." in filename and \
              filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

app.secret_key = "super-secret-key-cambiar-despues"

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["admin"] = True
            return redirect(url_for("admin"))
        else:
            error = "Credenciales incorrectas. Inténtalo de nuevo."
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def obtener_productos():
    conn = get_db_connection()
    productos = conn.execute(
        "SELECT * FROM productos ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return productos

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            nombre TEXT NOT NULL,
            material TEXT,
            precio INTEGER NOT NULL,
            categoria TEXT NOT NULL,
            imagen TEXT,
            disponible INTEGER DEFAULT 1
        )
    """)
    conn.commit()
    conn.close()
init_db()

def obtener_productos_db():
    conn = get_db_connection()
    productos = conn.execute("""
        SELECT codigo, nombre, material, precio, categoria, imagen, disponible
        FROM productos
        WHERE disponible = 1
    """).fetchall()
    conn.close()
    return productos

@app.route("/test-productos")
def test_productos():
    conn = get_db_connection()
    productos = conn.execute("SELECT * FROM productos").fetchall()
    conn.close()
    return {"cantidad": len(productos)}

def cargar_catalogo():
    ruta = os.path.join(app.root_path, "data", "catalogo.json")
    with open(ruta, encoding="utf-8") as archivo:
        return json.load(archivo)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/catalogo')
def catalogo():
    joyas = obtener_productos_db()
    return render_template("catalogo.html", joyas=joyas)

@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect(url_for("login"))
       
    productos = obtener_productos()
    return render_template("admin.html", productos=productos)

@app.route("/admin/editar/<int:id>")
def editar_producto(id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    producto = conn.execute(
        "SELECT * FROM productos WHERE id = ?", (id,)
    ).fetchone()
    conn.close()

    return render_template("editar.html", producto=producto)

@app.route("/admin/actualizar/<int:id>", methods=["POST"])
def actualizar_producto(id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    nombre = request.form["nombre"]
    material = request.form.get("material")
    precio = request.form["precio"]
    categoria = request.form["categoria"]

    conn = get_db_connection()
    conn.execute("""
                 UPDATE productos
                 SET nombre = ?, material = ?, precio = ?, categoria = ?
                 WHERE id = ?
                 """, (nombre, material, precio, categoria, id))
    conn.commit()
    conn.close()

    flash("Producto actualizado", "info")

    return redirect(url_for("admin"))

@app.route("/admin/eliminar/<int:id>")
def eliminar_producto(id):
    if not session.get("admin"):
        return redirect(url_for("login"))
    
    conn = get_db_connection()
    conn.execute("DELETE FROM productos WHERE id = ?", (id,))
    conn.commit()
    conn.close()

    flash("Producto eliminado", "warning")

    return redirect(url_for("admin"))

@app.route("/admin/add", methods=["POST"])
def admin_add():
    codigo = request.form["codigo"]
    nombre = request.form["nombre"]
    material = request.form.get("material")
    precio = request.form["precio"]
    categoria = request.form["categoria"]
    imagen_file = request.files.get("imagen")
    imagen_nombre = None

    if imagen_file and allowed_file(imagen_file.filename):
        filename = secure_filename(imagen_file.filename)
        imagen_file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        imagen_nombre = filename

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO productos (codigo, nombre, material, precio, categoria, imagen)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (codigo, nombre, material, precio, categoria, imagen_nombre))

    conn.commit()
    conn.close()

    flash("Producto agregado exitosamente.", "success")

    return redirect("/catalogo")

if __name__ == '__main__':
    app.run(debug=True)