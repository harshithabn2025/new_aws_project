USE meditrack;

INSERT INTO equipment (equipment_name, serial_number, department, purchase_date, status)
VALUES
('Ventilator', 'VENT-1001', 'ICU', '2023-05-10', 'Active'),
('Infusion Pump', 'INF-2001', 'Emergency', '2022-11-15', 'Under Maintenance'),
('Defibrillator', 'DEF-3001', 'Cardiology', '2021-08-20', 'Active');

INSERT INTO maintenance_log (equipment_id, maintenance_date, technician_name, issue_reported, resolution_notes, next_due_date)
VALUES
(1, '2026-01-10', 'Rahul', 'Routine inspection', 'Working fine', '2026-03-01'),
(2, '2026-02-15', 'Anita', 'Battery issue', 'Battery replaced', '2026-04-01'),
(3, '2026-02-20', 'Vikram', 'Pads expired', 'Pads replaced', '2026-12-31');
