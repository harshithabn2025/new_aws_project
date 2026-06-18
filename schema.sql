CREATE DATABASE IF NOT EXISTS meditrack;
USE meditrack;

CREATE TABLE IF NOT EXISTS equipment (
    equipment_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_name VARCHAR(100) NOT NULL,
    serial_number VARCHAR(50) NOT NULL UNIQUE,
    department VARCHAR(100) NOT NULL,
    purchase_date DATE,
    status VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS maintenance_log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    equipment_id INT NOT NULL,
    maintenance_date DATE NOT NULL,
    technician_name VARCHAR(100) NOT NULL,
    issue_reported TEXT,
    resolution_notes TEXT,
    next_due_date DATE,
    FOREIGN KEY (equipment_id) REFERENCES equipment(equipment_id)
        ON DELETE CASCADE
);
