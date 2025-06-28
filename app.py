from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:253031@localhost/tienda'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# ----------------------
# MODELOS
# ----------------------

class Producto(db.Model):
    __tablename__ = 'productos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String, nullable=False)
    precio = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False)

class Venta(db.Model):
    __tablename__ = 'ventas'
    id = db.Column(db.Integer, primary_key=True)
    producto_id = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Numeric(10, 2), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    producto = db.relationship('Producto')

# ----------------------
# RUTAS
# ----------------------

@app.route('/')
def index():
    productos = Producto.query.all()
    return render_template('index.html', productos=productos)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if request.method == 'POST':
        nombre = request.form['nombre']
        precio = request.form['precio']
        stock = request.form['stock']

        nuevo_producto = Producto(nombre=nombre, precio=precio, stock=stock)
        db.session.add(nuevo_producto)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('agregar.html')

@app.route('/vender', methods=['GET', 'POST'])
def vender():
    productos = Producto.query.all()

    if request.method == 'POST':
        producto_id = int(request.form['producto_id'])
        cantidad = int(request.form['cantidad'])

        producto = Producto.query.get(producto_id)

        if producto and producto.stock >= cantidad:
            producto.stock -= cantidad
            total = producto.precio * cantidad
            venta = Venta(producto_id=producto.id, cantidad=cantidad, total=total)
            db.session.add(venta)
            db.session.commit()
            return redirect(url_for('ventas'))
        else:
            return "❌ Stock insuficiente o producto no válido."

    return render_template('vender.html', productos=productos)

@app.route('/ventas')
def ventas():
    ventas = Venta.query.order_by(Venta.fecha.desc()).all()
    return render_template('ventas.html', ventas=ventas)

# ----------------------
# EJECUTAR
# ----------------------

if __name__ == '__main__':
    app.run(debug=True)
