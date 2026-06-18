from flask import Flask, render_template, request, redirect, url_for, jsonify
from db import get_connection

app = Flask(__name__)


# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():
    conn = get_connection()
    with conn.cursor() as cursor:

        cursor.execute("SELECT COUNT(*) AS total FROM equipment")
        total_equipment = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT status, COUNT(*) AS count
            FROM equipment
            GROUP BY status
        """)
        status_counts = cursor.fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        total_equipment=total_equipment,
        status_counts=status_counts
    )


# ---------------- EQUIPMENT LIST ----------------
@app.route("/equipment")
def equipment_list():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM equipment ORDER BY equipment_id DESC")
        equipment = cursor.fetchall()

    conn.close()

    return render_template("equipment_list.html", equipment=equipment)


# ---------------- ADD EQUIPMENT ----------------
@app.route("/equipment/add", methods=["GET", "POST"])
def add_equipment():
    if request.method == "POST":

        # ✅ MUST MATCH HTML name=""
        equipment_name = request.form["equipment_name"]
        serial_number = request.form["serial_number"]
        department = request.form["department"]
        purchase_date = request.form["purchase_date"]
        status = request.form["status"]

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO equipment
                (equipment_name, serial_number, department, purchase_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (equipment_name, serial_number, department, purchase_date, status))

        conn.commit()
        conn.close()

        return redirect(url_for("equipment_list"))

    return render_template("add_equipment.html")


# ---------------- EQUIPMENT DETAIL ----------------
@app.route("/equipment/<int:equipment_id>")
def equipment_detail(equipment_id):
    conn = get_connection()
    with conn.cursor() as cursor:

        cursor.execute("SELECT * FROM equipment WHERE equipment_id=%s", (equipment_id,))
        equipment = cursor.fetchone()

    conn.close()

    return render_template("equipment_detail.html", equipment=equipment)


# ---------------- API ----------------
@app.route("/api/health")
def health():
    return jsonify({"status": "running"})


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)