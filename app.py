from flask import Flask, render_template, redirect, url_for, request,session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key="mysecretkey"
# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User Table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(100))

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.Integer)
    
  
   

# Sample Products
products = [
    {"id": 1, "name": "Laptop", "price": 50000},
    {"id": 2, "name": "Phone", "price": 20000},
     {"id": 3, "name": "tv", "price": 20700},
      {"id": 4, "name": "Shoes", "price": 15000}
]

cart = []

# Home Page
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

# Add To Cart
@app.route('/add/<int:id>')
def add_to_cart(id):

    product = Product.query.get(id)

    if product:
        cart.append({
            "id": product.id,
            "name": product.name,
            "price": product.price
        })

    return redirect(url_for('home'))

# View Cart
@app.route('/cart')
def view_cart():
    total = sum(item["price"] for item in cart)

    return render_template(
        'cart.html',
        cart=cart,
        total=total
    )

# Remove Item
@app.route('/remove/<int:index>')
def remove_item(index):
    if index < len(cart):
        cart.pop(index)

    return redirect(url_for('view_cart'))

# Clear Cart
@app.route('/clear_cart')
def clear_cart():
    cart.clear()
    return redirect(url_for('view_cart'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        new_user = User(
            username=username,
            password=password
        )

        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('home'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:
            session['username']=username
            return redirect(url_for('home'))

        return "Invalid Username or Password"

    return render_template('login.html')
@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():  
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "venky" and password == "venky77@":
            session['admin'] = True
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
        image=request.form['image']
        
        product = Product(
            name=name,
            price=price,
            
            
        )

        db.session.add(product)
        db.session.commit()

    products = Product.query.all()

    return render_template(
        'admin.html',
        products=products
    )

# Create Database Tables
with app.app_context():
    db.create_all()
@app.route('/logout')
def logout():

    session.pop('username', None)

    return redirect(url_for('home'))
@app.route('/delete_product/<int:id>')
def delete_product(id):

    product = Product.query.get(id)

    if product:
        db.session.delete(product)
        db.session.commit()

    return redirect(url_for('admin'))
@app.route('/edit_product/<int:id>', methods=['GET', 'POST'])
def edit_product(id):

    product = Product.query.get(id)

    if request.method == 'POST':

        product.name = request.form['name']
        product.price = request.form['price']

        db.session.commit()

        return redirect(url_for('admin'))

    return render_template(
        'edit_product.html',
        product=product
    )
# Run App
if __name__ == '__main__':
    app.run(debug=True)