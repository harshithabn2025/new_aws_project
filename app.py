from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Connect to MySQL
try:
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        connection_timeout=10
    )
    cursor = db.cursor(dictionary=True)
    print("✅ Connected to MySQL successfully!")

except mysql.connector.Error as err:
    print("❌ Database connection failed:")
    print(err)

# Home Route
@app.route("/")
def home():
    return "Flask App is Running Successfully!"

# Start Flask Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)