from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__)
app.secret_key = "mysecretkey"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=10)

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    image = db.Column(db.String(200)) 

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    product_id = db.Column(db.Integer)
    product_name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    image = db.Column(db.String(200))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100))
    product_name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    image = db.Column(db.String(200))  

products = [
    {"id": 1, "name": "Laptop", "price": 50000},
    {"id": 2, "name": "Phone", "price": 20000},
    {"id": 3, "name": "tv", "price": 20700},
    {"id": 4, "name": "Shoes", "price": 15000}
]

cart = []

@app.route('/')
def home():
    cart_count = len(cart)
    username = session.get('username')
    products = Product.query.all()
    return render_template(
        'index.html',
        products=products,
        cart_count=cart_count,
        username=username
    )

@app.route('/add/<int:id>')
def add_to_cart(id):
    if 'username' not in session:
        return redirect(url_for('login'))

    product = Product.query.get(id)
    if product:
        item = Cart(
            username=session['username'],
            product_id=product.id,
            product_name=product.name,
            price=product.price,
            image=product.image
        )
        db.session.add(item)
        db.session.commit()

    return redirect(url_for('home'))

@app.route('/cart')
def view_cart():
    if 'username' not in session:
        return redirect(url_for('login'))

    cart_items = Cart.query.filter_by(username=session['username']).all()
    total = sum(item.price for item in cart_items)

    return render_template(
        'cart.html',
        cart=cart_items,
        total=total
    )

@app.route('/remove/<int:id>')
def remove_item(id):
    item = Cart.query.get(id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect(url_for('view_cart'))

@app.route('/clear_cart')
def clear_cart():
    Cart.query.filter_by(username=session['username']).delete()
    db.session.commit()
    return redirect(url_for('view_cart'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()

        if user:
            session['username'] = username
            session.permanent = True
            return redirect(url_for('home'))
        return "Invalid Username or Password"
    return render_template('login.html')

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():  
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "admin123":
            session['admin'] = True
            session.permanent = True
            return redirect(url_for('admin'))
        return "Invalid Admin Login"
    return render_template('admin_login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        image = request.form['image']

        product = Product(name=name, price=price, image=image)
        db.session.add(product)
        db.session.commit()

    products = Product.query.all()
    return render_template('admin.html', products=products)

@app.route('/delete_product/<int:id>')
def delete_product(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    product = Product.query.get(id)
    if product:
        db.session.delete(product)
        db.session.commit()
    return redirect(url_for('admin'))

@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    product = Product.query.get(id)
    if request.method == 'POST':
        product.name = request.form['name']
        product.price = request.form['price']
        db.session.commit()
        return redirect(url_for('admin'))

    return render_template('edit_product.html', product=product)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin-logout')
def admin_logout():
    session.clear()
    return redirect(url_for('admin_login'))

@app.route('/search')
def search():
    keyword = request.args.get('q')
    products = Product.query.filter(Product.name.contains(keyword)).all()
    return render_template('index.html', products=products)

@app.route('/orders')
def my_orders():
    if 'username' not in session:
        return redirect(url_for('login'))

    orders = Order.query.filter_by(username=session['username']).all()
    return render_template('orders.html', orders=orders)

@app.route('/place_order')
def place_order():
    if 'username' not in session:
        return redirect(url_for('login'))

    cart_items = Cart.query.filter_by(username=session['username']).all()
    for item in cart_items:
        order = Order(
            username=item.username,
            product_name=item.product_name,
            price=item.price,
            image=item.image
        )
        db.session.add(order)

    Cart.query.filter_by(username=session['username']).delete()
    db.session.commit()
    return redirect(url_for('my_orders'))

@app.route('/cancel_order/<int:id>')
def cancel_order(id):
    order = Order.query.get(id)
    if order:
        db.session.delete(order)
        db.session.commit()
    return redirect(url_for('my_orders'))

with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)