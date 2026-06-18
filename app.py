from flask import Flask, render_template, request, redirect, url_for, jsonify
from db import get_connection

app = Flask(__name__)

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

        cursor.execute("""
            SELECT e.equipment_id, e.equipment_name, e.serial_number, e.department,
                   MAX(m.next_due_date) AS next_due_date
            FROM equipment e
            JOIN maintenance_log m ON e.equipment_id = m.equipment_id
            GROUP BY e.equipment_id, e.equipment_name, e.serial_number, e.department
            HAVING MAX(m.next_due_date) < CURDATE()
        """)
        overdue_items = cursor.fetchall()

    conn.close()
    return render_template(
        "dashboard.html",
        total_equipment=total_equipment,
        status_counts=status_counts,
        overdue_items=overdue_items
    )

@app.route("/equipment")
def equipment_list():
    department = request.args.get("department", "")
    status = request.args.get("status", "")

    conn = get_connection()
    with conn.cursor() as cursor:
        query = "SELECT * FROM equipment WHERE 1=1"
        params = []

        if department:
            query += " AND department = %s"
            params.append(department)

        if status:
            query += " AND status = %s"
            params.append(status)

        query += " ORDER BY equipment_id DESC"
        cursor.execute(query, params)
        equipment = cursor.fetchall()

        cursor.execute("SELECT DISTINCT department FROM equipment")
        departments = cursor.fetchall()

    conn.close()
    return render_template(
        "equipment_list.html",
        equipment=equipment,
        departments=departments,
        selected_department=department,
        selected_status=status
    )

@app.route("/equipment/add", methods=["GET", "POST"])
def add_equipment():
    if request.method == "POST":
        equipment_name = request.form["equipment_name"]
        serial_number = request.form["serial_number"]
        department = request.form["department"]
        purchase_date = request.form["purchase_date"]
        status = request.form["status"]

        conn = get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO equipment (equipment_name, serial_number, department, purchase_date, status)
                VALUES (%s, %s, %s, %s, %s)
            """, (equipment_name, serial_number, department, purchase_date, status))
        conn.close()

        return redirect(url_for("equipment_list"))

    return render_template("add_equipment.html")

@app.route("/equipment/<int:equipment_id>")
def equipment_detail(equipment_id):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM equipment WHERE equipment_id = %s", (equipment_id,))
        equipment = cursor.fetchone()

        cursor.execute("""
            SELECT * FROM maintenance_log
            WHERE equipment_id = %s
            ORDER BY maintenance_date DESC
        """, (equipment_id,))
        maintenance_logs = cursor.fetchall()

    conn.close()
    return render_template(
        "equipment_detail.html",
        equipment=equipment,
        maintenance_logs=maintenance_logs
    )

@app.route("/maintenance/add/<int:equipment_id>", methods=["GET", "POST"])
def add_maintenance(equipment_id):
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM equipment WHERE equipment_id = %s", (equipment_id,))
        equipment = cursor.fetchone()

    if request.method == "POST":
        maintenance_date = request.form["maintenance_date"]
        technician_name = request.form["technician_name"]
        issue_reported = request.form["issue_reported"]
        resolution_notes = request.form["resolution_notes"]
        next_due_date = request.form["next_due_date"]

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO maintenance_log
                (equipment_id, maintenance_date, technician_name, issue_reported, resolution_notes, next_due_date)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                equipment_id, maintenance_date, technician_name,
                issue_reported, resolution_notes, next_due_date
            ))
        conn.close()
        return redirect(url_for("equipment_detail", equipment_id=equipment_id))

    conn.close()
    return render_template("add_maintenance.html", equipment=equipment)

@app.route("/equipment/update-status/<int:equipment_id>", methods=["POST"])
def update_status(equipment_id):
    new_status = request.form["status"]

    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            UPDATE equipment
            SET status = %s
            WHERE equipment_id = %s
        """, (new_status, equipment_id))
    conn.close()

    return redirect(url_for("equipment_detail", equipment_id=equipment_id))

@app.route("/api/overdue")
def overdue_json():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            SELECT e.equipment_id, e.equipment_name, e.serial_number, e.department,
                   MAX(m.next_due_date) AS next_due_date
            FROM equipment e
            JOIN maintenance_log m ON e.equipment_id = m.equipment_id
            GROUP BY e.equipment_id, e.equipment_name, e.serial_number, e.department
            HAVING MAX(m.next_due_date) < CURDATE()
        """)
        overdue_items = cursor.fetchall()
    conn.close()
    return jsonify(overdue_items)

if __name__ == "__main__":
    app.run(debug=True)
