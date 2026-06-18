from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from dotenv import load_dotenv
import os

# Load env variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

# ---------------- HOME (READ) ----------------
@app.route("/")
def home():
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM equipment")
    data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("index.html", equipment=data)

# ---------------- ADD EQUIPMENT ----------------
@app.route("/add_equipment", methods=["GET", "POST"])
def add_equipment():
    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]

        db = get_db_connection()
        cursor = db.cursor()

        cursor.execute(
            "INSERT INTO equipment (name, quantity) VALUES (%s, %s)",
            (name, quantity)
        )

        db.commit()
        cursor.close()
        db.close()

        flash("Equipment added successfully!")
        return redirect(url_for("home"))

    return render_template("add_equipment.html")

# ---------------- EDIT EQUIPMENT ----------------
@app.route("/edit_equipment/<int:id>", methods=["GET", "POST"])
def edit_equipment(id):
    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        quantity = request.form["quantity"]

        cursor.execute(
            "UPDATE equipment SET name=%s, quantity=%s WHERE id=%s",
            (name, quantity, id)
        )

        db.commit()
        cursor.close()
        db.close()

        flash("Equipment updated successfully!")
        return redirect(url_for("home"))

    cursor.execute("SELECT * FROM equipment WHERE id=%s", (id,))
    item = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template("edit_equipment.html", item=item)

# ---------------- DELETE EQUIPMENT ----------------
@app.route("/delete_equipment/<int:id>")
def delete_equipment(id):
    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM equipment WHERE id=%s", (id,))
    db.commit()

    cursor.close()
    db.close()

    flash("Equipment deleted successfully!")
    return redirect(url_for("home"))

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)