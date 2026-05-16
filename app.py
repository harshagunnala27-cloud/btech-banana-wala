from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "banana_secret_key"

DATABASE = "store.db"

PRODUCTS = {
    "1": {"name": "Apple", "price": 15},
    "2": {"name": "Banana", "price": 10},
    "3": {"name": "Orange", "price": 12},
    "4": {"name": "Grapes", "price": 20},
    "5": {"name": "Mango", "price": 30},
    "6": {"name": "Pineapple", "price": 18},
}

GST_RATE = 0.18


def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    conn.commit()
    conn.close()


init_db()


@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        cur.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )

        user = cur.fetchone()
        conn.close()

        if user:
            session["user"] = username
            return redirect("/home")

    return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users(username,password) VALUES(?,?)",
            (username, password)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("signup.html")


@app.route("/home", methods=["GET", "POST"])
def home():

    if "cart" not in session:
        session["cart"] = {}

    payment_success = False
    final_amount = 0

    if request.method == "POST":

        for code in PRODUCTS:
            qty = request.form.get(f"qty_{code}")

            if qty and int(qty) > 0:
                session["cart"][code] = int(qty)

        session.modified = True

    cart_items = []
    subtotal = 0

    for code, qty in session["cart"].items():
        product = PRODUCTS[code]
        total = product["price"] * qty

        subtotal += total

        cart_items.append({
            "name": product["name"],
            "price": product["price"],
            "quantity": qty,
            "total": total
        })

    gst = subtotal * GST_RATE
    final_amount = subtotal + gst

    return render_template(
        "index.html",
        products=PRODUCTS,
        cart_items=cart_items,
        subtotal=subtotal,
        gst=gst,
        final_amount=final_amount,
        payment_success=payment_success
    )


@app.route("/payment")
def payment():
    return render_template("payment.html")


@app.route("/success")
def success():
    session["cart"] = {}
    return render_template("success.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)