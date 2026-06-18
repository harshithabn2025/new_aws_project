from dotenv import load_dotenv
import os

load_dotenv()

db = mysql.connector.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME")
)

cursor = db.cursor(dictionary=True)


# Home Page
@app.route('/')
def index():

    department = request.args.get('department')
    status = request.args.get('status')

    query = "SELECT * FROM equipment WHERE 1=1"
    values = []

    if department:
        query += " AND department=%s"
        values.append(department)

    if status:
        query += " AND status=%s"
        values.append(status)

    cursor.execute(query, values)
    equipment = cursor.fetchall()

    return render_template("index.html", equipment=equipment)


# Add Equipment
@app.route('/add', methods=['GET', 'POST'])
def add():

    if request.method == 'POST':

        equipment_name = request.form['equipment_name']
        serial_number = request.form['serial_number']
        department = request.form['department']
        purchase_date = request.form['purchase_date']
        status = request.form['status']

        sql = """
        INSERT INTO equipment
        (equipment_name, serial_number, department, purchase_date, status)
        VALUES (%s,%s,%s,%s,%s)
        """

        values = (
            equipment_name,
            serial_number,
            department,
            purchase_date,
            status
        )

        cursor.execute(sql, values)
        db.commit()

        return redirect('/')

    return render_template("add.html")


# Edit Equipment
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):

    if request.method == 'POST':

        equipment_name = request.form['equipment_name']
        serial_number = request.form['serial_number']
        department = request.form['department']
        purchase_date = request.form['purchase_date']
        status = request.form['status']

        sql = """
        UPDATE equipment
        SET equipment_name=%s,
        serial_number=%s,
        department=%s,
        purchase_date=%s,
        status=%s
        WHERE equipment_id=%s
        """

        cursor.execute(sql, (
            equipment_name,
            serial_number,
            department,
            purchase_date,
            status,
            id
        ))

        db.commit()

        return redirect('/')

    cursor.execute("SELECT * FROM equipment WHERE equipment_id=%s", (id,))
    equipment = cursor.fetchone()

    return render_template("edit.html", equipment=equipment)


# Delete Equipment
@app.route('/delete/<int:id>')
def delete(id):

    cursor.execute("DELETE FROM equipment WHERE equipment_id=%s", (id,))
    db.commit()

    return redirect('/')


# Maintenance History
@app.route('/maintenance/<int:id>')
def maintenance(id):

    cursor.execute("SELECT * FROM equipment WHERE equipment_id=%s", (id,))
    equipment = cursor.fetchone()

    cursor.execute("""
    SELECT * FROM maintenance_log
    WHERE equipment_id=%s
    ORDER BY maintenance_date DESC
    """, (id,))

    logs = cursor.fetchall()

    return render_template(
        "maintenance.html",
        equipment=equipment,
        logs=logs
    )


# Add Maintenance Record
@app.route('/add_log/<int:id>', methods=['POST'])
def add_log(id):

    maintenance_date = request.form['maintenance_date']
    technician_name = request.form['technician_name']
    issue_reported = request.form['issue_reported']
    resolution_notes = request.form['resolution_notes']
    next_due_date = request.form['next_due_date']

    sql = """
    INSERT INTO maintenance_log
    (equipment_id,
    maintenance_date,
    technician_name,
    issue_reported,
    resolution_notes,
    next_due_date)
    VALUES(%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        id,
        maintenance_date,
        technician_name,
        issue_reported,
        resolution_notes,
        next_due_date
    ))

    db.commit()

    return redirect(url_for('maintenance', id=id))


# Dashboard
@app.route('/dashboard')
def dashboard():

    cursor.execute("SELECT COUNT(*) total FROM equipment")
    total = cursor.fetchone()['total']

    cursor.execute("""
    SELECT status,COUNT(*) count
    FROM equipment
    GROUP BY status
    """)

    status_data = cursor.fetchall()

    cursor.execute("""
    SELECT e.equipment_name,
    m.next_due_date

    FROM equipment e
    JOIN maintenance_log m
    ON e.equipment_id=m.equipment_id

    WHERE m.next_due_date < CURDATE()
    """)

    overdue = cursor.fetchall()

    return render_template(
        "dashboard.html",
        total=total,
        status_data=status_data,
        overdue=overdue
    )


if __name__ == "__main__":
    app.run(debug=True)