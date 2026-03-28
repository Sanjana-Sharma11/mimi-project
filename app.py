from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB = "database.db"

# ---------------- DATABASE INIT ----------------
def init_db():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        type TEXT,
        amount INTEGER,
        date_time TEXT,
        status TEXT
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------------- BALANCE FUNCTION ----------------
def get_balance(username):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT type, amount, status FROM transactions WHERE username=?", (username,))
    data = cursor.fetchall()

    conn.close()

    balance = 0
    for t in data:
        if t[2] == "SUCCESS":
            if t[0] == "deposit":
                balance += t[1]
            elif t[0] == "withdraw":
                balance -= t[1]

    return balance

# ---------------- FRAUD DETECTION ----------------
def detect_fraud(amount):
    return amount > 100000

# ---------------- HOME ----------------
@app.route("/")
def home():
    return render_template("login.html")

# ---------------- REGISTER ----------------
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users(username,password) VALUES (?,?)", (username,password))

        conn.commit()
        conn.close()

        return redirect("/")

    return render_template("register.html")

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username,password))
    user = cursor.fetchone()

    conn.close()

    if user:
        return render_template("dashboard.html", username=username)
    else:
        return "❌ Invalid Username or Password"

# ---------------- FORGOT PASSWORD ----------------
@app.route("/forgot", methods=["GET","POST"])
def forgot():
    if request.method == "POST":
        username = request.form["username"]
        new_password = request.form["new_password"]

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("UPDATE users SET password=? WHERE username=?", (new_password, username))

        conn.commit()
        conn.close()

        return "✅ Password Updated! Login again."

    return render_template("forgot.html")

# ---------------- DEPOSIT ----------------
@app.route("/deposit", methods=["POST"])
def deposit():
    username = request.form["username"]
    amount = int(request.form["amount"])

    date_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    if detect_fraud(amount):
        status = "BLOCKED"
        msg = "⚠ Fraud Detected! Amount Blocked"
    else:
        status = "SUCCESS"
        msg = "✅ Deposit Successful"

    cursor.execute(
        "INSERT INTO transactions(username,type,amount,date_time,status) VALUES (?,?,?,?,?)",
        (username, "deposit", amount, date_time, status)
    )

    conn.commit()
    conn.close()

    return render_template("dashboard.html",username=username,msg=msg)

# ---------------- WITHDRAW ----------------
@app.route("/withdraw", methods=["POST"])
def withdraw():
    username = request.form["username"]
    amount = int(request.form["amount"])

    balance = get_balance(username)

    if amount > balance:
        return "❌ Insufficient Balance"

    date_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO transactions(username,type,amount,date_time,status) VALUES (?,?,?,?,?)",
        (username, "withdraw", amount, date_time, "SUCCESS")
    )

    conn.commit()
    conn.close()

    return "✅ Withdraw Successful"

# ---------------- BALANCE ----------------
@app.route("/balance", methods=["POST"])
def balance():
    username = request.form["username"]
    bal = get_balance(username)
    return f"💰 Balance: ₹{bal}"

# ---------------- HISTORY ----------------
@app.route("/history", methods=["POST"])
def history():
    username = request.form["username"]

    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    # ✅ FIXED COLUMN NAME
    cursor.execute(
        "SELECT type, amount, date_time, status FROM transactions WHERE username=?",
        (username,)
    )
    data = cursor.fetchall()

    conn.close()

    return render_template("history.html", transactions=data)

# ---------------- ADMIN ----------------
@app.route("/admin")
def admin():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("SELECT id, username, amount, date_time FROM transactions WHERE status='BLOCKED'")
    data = cursor.fetchall()

    conn.close()

    return render_template("admin.html", data=data)

# ---------------- APPROVE ----------------
@app.route("/approve/<int:id>")
def approve(id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()

    cursor.execute("UPDATE transactions SET status='SUCCESS' WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect("/admin")

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)