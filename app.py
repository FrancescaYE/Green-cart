# app.py
from flask import Flask, render_template, redirect, url_for, session, request
import pyodbc
from datetime import datetime

app = Flask(__name__)
app.secret_key = "une-cle-secrete-a-changer"

CONNECTION_STRING = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=tcp:greencart-server.database.windows.net,1433;"
    "DATABASE=greencart-db;"
    "Encrypt=yes;"
    "TrustServerCertificate=no;"
    "Authentication=ActiveDirectoryMsi;"
)

def get_connection():
    return pyodbc.connect(CONNECTION_STRING, timeout=15)


@app.route("/")
def home():
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id_product, name, price, image_url FROM dbo.Products ORDER BY id_product")
        products = [
            {"id": row.id_product, "name": row.name, "price": f"{row.price:.0f} FCFA", "image_url": row.image_url}
            for row in cursor.fetchall()
        ]
    return render_template("catalog.html", products=products)


@app.route("/products/<int:product_id>")
def product_detail(product_id):
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id_product, name, description, price, image_url FROM dbo.Products WHERE id_product = ?",
            product_id
        )
        row = cursor.fetchone()
        if row is None:
            return "Produit introuvable", 404
        product = {
            "id": row.id_product, "name": row.name, "description": row.description,
            "price": row.price, "image_url": row.image_url
        }
    return render_template("product_detail.html", product=product)


@app.route("/cart/add/<int:product_id>", methods=["GET", "POST"])
def add_to_cart(product_id):
    qty = 1
    if request.method == "POST":
        qty = int(request.form.get("quantity", 1))
    cart = session.get("cart", {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + qty
    session["cart"] = cart
    return redirect(url_for("view_cart"))


@app.route("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):
    cart = session.get("cart", {})
    cart.pop(str(product_id), None)
    session["cart"] = cart
    return redirect(url_for("view_cart"))


@app.route("/cart")
def view_cart():
    cart = session.get("cart", {})
    items = []
    total = 0
    if cart:
        with get_connection() as conn:
            cursor = conn.cursor()
            for product_id, qty in cart.items():
                cursor.execute(
                    "SELECT id_product, name, price, image_url FROM dbo.Products WHERE id_product = ?",
                    int(product_id)
                )
                row = cursor.fetchone()
                if row:
                    subtotal = row.price * qty
                    total += subtotal
                    items.append({
                        "id": row.id_product, "name": row.name, "price": row.price,
                        "qty": qty, "subtotal": subtotal, "image_url": row.image_url
                    })
    return render_template("cart.html", items=items, total=total)


@app.route("/checkout", methods=["POST"])
def checkout():
    cart = session.get("cart", {})
    if not cart:
        return redirect(url_for("view_cart"))

    with get_connection() as conn:
        cursor = conn.cursor()
        total = 0
        order_items = []
        for product_id, qty in cart.items():
            cursor.execute("SELECT price FROM dbo.Products WHERE id_product = ?", int(product_id))
            row = cursor.fetchone()
            subtotal = row.price * qty
            total += subtotal
            order_items.append((int(product_id), qty, row.price))

        cursor.execute(
            "INSERT INTO dbo.Orders (date, total_commande) OUTPUT INSERTED.id_order VALUES (?, ?)",
            datetime.now(), total
        )
        order_id = cursor.fetchone()[0]

        for product_id, qty, prix_dachat in order_items:
            cursor.execute(
                "INSERT INTO dbo.Order_items (id_product, id_order, number, prix_dachat) VALUES (?, ?, ?, ?)",
                product_id, order_id, qty, prix_dachat
            )
        conn.commit()

    session["cart"] = {}
    return redirect(url_for("order_confirmation", order_id=order_id, total=total))


@app.route("/order-confirmation/<int:order_id>")
def order_confirmation(order_id):
    total = request.args.get("total", 0)
    return render_template("order_confirmation.html", order_id=order_id, total=float(total))


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
