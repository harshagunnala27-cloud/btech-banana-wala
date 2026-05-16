from flask import Flask, render_template, request
from datetime import datetime
import os

app = Flask(__name__)

# === Fruit products ===
PRODUCTS = {
    "1": {"name": "Apple",      "price": 15.5},
    "2": {"name": "Banana",     "price": 10.0},
    "3": {"name": "Orange",     "price": 12.0},
    "4": {"name": "Grapes",     "price": 20.0},
    "5": {"name": "Watermelon", "price": 25.0},
    "6": {"name": "Mango",      "price": 30.0},
    "7": {"name": "Pineapple",  "price": 18.0},
    "8": {"name": "Mango (Grade B)", "price": 22.0},
    "9": {"name": "Strawberry", "price": 28.0},
    "10": {"name": "Custard Apple", "price": 35.0},
}

GST_RATE = 0.18

BILLS_DIR = "bills"
os.makedirs(BILLS_DIR, exist_ok=True)


def save_bill_to_file(bill):
    filename = f"{BILLS_DIR}/bill_{bill['timestamp'].replace(':', '-').replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("BTech Banana Wala - Fruit Supermarket\n")
        f.write("=" * 50 + "\n")
        f.write(f"Customer name  : {bill['name']}\n")
        f.write(f"Mobile number  : {bill['contact']}\n")
        f.write(f"Payment method : {bill['payment_method']}\n")
        f.write(f"Date & time    : {bill['timestamp']}\n")
        f.write("-" * 50 + "\n")
        f.write("Item                Qty    Price     Total\n")
        for item in bill["items"]:
            left = item["name"]
            qty = str(item["quantity"])
            price = f"{item['price']:.2f}"
            total = f"{item['total']:.2f}"
            f.write(f"{left:<15} {qty:>4} {price:>8} {total:>8}\n")
        f.write("-" * 50 + "\n")
        f.write(f"{'Subtotal':<25} ₹{bill['subtotal']:.2f}\n")
        f.write(f"{'GST (18%)':<25} ₹{bill['gst']:.2f}\n")
        f.write(f"{'Final Amount':<25} ₹{bill['final_amount']:.2f}\n")
        f.write("=" * 50 + "\n")
        f.write("Thank you for shopping with BTech Banana Wala!\n")
        f.write("Visit again!\n")
    return filename


@app.route("/", methods=["GET", "POST"])
def index():
    error = ""
    bill = None

    if request.method == "POST":
        try:
            name = request.form.get("name", "").strip()
            contact = request.form.get("contact", "").strip()
            payment_method = request.form.get("payment_method", "cash")

            if not name:
                raise ValueError("Customer name is required.")
            if not contact.isdigit() or len(contact) != 10:
                raise ValueError("Please enter a valid 10‑digit mobile number.")

            cart = {}
            subtotal = 0.0

            for code in PRODUCTS:
                qty_str = request.form.get(f"qty_{code}")
                if qty_str and qty_str.strip():
                    qty = int(qty_str)
                    if qty <= 0:
                        continue
                    cart[code] = {"quantity": qty}
                    subtotal += PRODUCTS[code]["price"] * qty

            if not cart:
                raise ValueError("Please add at least one fruit.")

            gst = subtotal * GST_RATE
            final_amount = subtotal + gst

            timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            bill = {
                "name": name,
                "contact": contact,
                "items": [],
                "subtotal": subtotal,
                "gst": gst,
                "final_amount": final_amount,
                "payment_method": payment_method,
                "timestamp": timestamp_str,
            }

            for code, data in cart.items():
                qty = data["quantity"]
                price = PRODUCTS[code]["price"]
                total = price * qty
                bill["items"].append({
                    "name": PRODUCTS[code]["name"],
                    "quantity": qty,
                    "price": price,
                    "total": total,
                })

            saved_file = save_bill_to_file(bill)

        except Exception as e:
            error = str(e)

    return render_template("index.html", products=PRODUCTS, error=error, bill=bill)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))