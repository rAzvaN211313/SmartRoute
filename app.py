from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
import datetime
import random

app = Flask(__name__)

# --- CONFIGURARE MYSQL ---
DB_CONFIG = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'Root', 
    'database': 'smartroute'
}

CITIES = {
    "Sibiu": [45.7983, 24.1256],
    "Bucharest": [44.4268, 26.1025],
    "Ploiesti": [44.9367, 26.0129],
    "Cluj-Napoca": [46.7712, 23.6236],
    "Brasov": [45.6427, 25.5887],
    "Timisoara": [45.7489, 21.2087],
    "Constanta": [44.1792, 28.6337],
    "Iasi": [47.1585, 27.6014]
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

@app.route("/reset_sistem")
def reset_sistem():
    conn = get_db(); c = conn.cursor()
    c.execute("SET FOREIGN_KEY_CHECKS = 0")
    c.execute("DROP TABLE IF EXISTS curse")
    c.execute("DROP TABLE IF EXISTS soferi")
    c.execute("DROP TABLE IF EXISTS vehicule")
    c.execute("DROP TABLE IF EXISTS istoric_curse")
    
    c.execute('''CREATE TABLE soferi (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(100), phone VARCHAR(20), license_no VARCHAR(50), factor_eficienta FLOAT)''')
    c.execute('''CREATE TABLE vehicule (id INT AUTO_INCREMENT PRIMARY KEY, plate VARCHAR(20), model VARCHAR(100))''')
    c.execute('''CREATE TABLE curse (id INT AUTO_INCREMENT PRIMARY KEY, sofer_id INT, sofer_nume VARCHAR(100), vehicul_id INT, vehicul_detalii VARCHAR(100), start_oras VARCHAR(50), end_oras VARCHAR(50), status VARCHAR(50), factor_sofer FLOAT)''')
    c.execute('''CREATE TABLE istoric_curse (id INT AUTO_INCREMENT PRIMARY KEY, sofer_id INT, factor_nou FLOAT, eroare_procentUALA FLOAT, data_finalizare DATETIME)''')

    fleet = [
        ('John "Elite" Doe', '0720111222', 'C+E', 0.82),
        ('Michael "Pro" Vance', '0720333444', 'C+E', 0.85),
        ('Sarah "Swift" Miller', '0720555666', 'C+E', 0.88),
        ('Robert "Standard" Ross', '0720777888', 'C', 1.00),
        ('Elena "Regular" Pope', '0720999000', 'C', 1.00),
        ('David "Steady" Knight', '0720123456', 'C+E', 1.05),
        ('George "Slow" Pumper', '0720654321', 'C', 1.25),
        ('Maria "Beginner" Lane', '0720000111', 'C', 1.30),
        ('Luca "Newcomer" Silva', '0720222333', 'C', 1.35),
        ('Alex "Reliable" Ford', '0720444555', 'C+E', 0.95)
    ]
    c.executemany("INSERT INTO soferi (name, phone, license_no, factor_eficienta) VALUES (%s, %s, %s, %s)", fleet)
    
    trucks = []
    modele_volvo = ['Volvo FH16 750 Heavy', 'Volvo FH 500 Tractor', 'Volvo FMX 8x4 Tipper']
    for _ in range(4):
        trucks.append((f"SB {random.randint(10, 99)} TRC", random.choice(modele_volvo)))
    for _ in range(6):
        trucks.append((f"B {random.randint(100, 999)} TRC", random.choice(modele_volvo)))

    c.executemany("INSERT INTO vehicule (plate, model) VALUES (%s, %s)", trucks)
    
    c.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit(); conn.close()
    return "<h1>SISTEM RESETAT CU SUCCES!</h1><p>Baza de date a fost reconstruita curat.</p><a href='/'>Inapoi la aplicatie</a>"

@app.route("/")
def index():
    try:
        conn = get_db(); c = conn.cursor()
        c.execute("SELECT * FROM curse ORDER BY id DESC"); curse = c.fetchall()
        c.execute("SELECT COUNT(*) FROM soferi"); nr_s = c.fetchone()[0] or 0
        c.execute("SELECT COUNT(*) FROM vehicule"); nr_v = c.fetchone()[0] or 0
        c.execute("SELECT AVG(ABS(eroare_procentUALA)) FROM istoric_curse")
        row = c.fetchone()
        err = float(row[0]) if row and row[0] else 0.0
        accuracy = round(100.0 - err, 1)
        conn.close()
        return render_template("index.html", curse=curse, nr_soferi=nr_s, nr_vehicule=nr_v, cities_coords=CITIES, accuracy=accuracy)
    except Exception as e:
        return f"Database Error: {e}. Acceseaza http://127.0.0.1:5000/reset_sistem pentru a repara."

@app.route("/complete_mission", methods=["POST"])
def complete_mission():
    data = request.json
    m_id, elapsed = data.get('id'), float(data.get('time_elapsed'))
    conn = get_db(); c = conn.cursor()
    c.execute("SELECT sofer_id, factor_sofer FROM curse WHERE id = %s", (m_id,))
    res = c.fetchone()
    if res:
        s_id, old_f = res[0], res[1]
        perf = elapsed / 400.0 # Baza din JS
        new_f = round((old_f * 0.7) + (perf * 0.3), 3) 
        err = abs((perf - old_f) / (old_f if old_f != 0 else 1)) * 100
        c.execute("UPDATE soferi SET factor_eficienta = %s WHERE id = %s", (new_f, s_id))
        
        c.execute("INSERT INTO istoric_curse (sofer_id, factor_nou, eroare_procentUALA, data_finalizare) VALUES (%s, %s, %s, %s)", (s_id, new_f, err, datetime.datetime.now()))
        c.execute("DELETE FROM curse WHERE id = %s", (m_id,))
    conn.commit(); conn.close()
    return jsonify({"status": "success"})

@app.route("/add_driver", methods=["GET", "POST"])
def add_driver():
    conn = get_db(); c = conn.cursor()
    if request.method == "POST":
        n, p, l = request.form["name"], request.form["phone"], request.form["license_no"]
        f = 0.85 if "Pro" in n else 1.25 if "Slow" in n else 1.0
        c.execute("INSERT INTO soferi (name, phone, license_no, factor_eficienta) VALUES (%s, %s, %s, %s)", (n, p, l, f))
        conn.commit(); return redirect(url_for("add_driver"))
    c.execute("SELECT * FROM soferi ORDER BY id DESC"); drivers = c.fetchall()
    conn.close()
    return render_template("add_driver.html", drivers=drivers)

@app.route("/delete_driver/<int:id>")
def delete_driver(id):
    conn = get_db(); c = conn.cursor()
    c.execute("DELETE FROM curse WHERE sofer_id = %s", (id,))
    c.execute("DELETE FROM istoric_curse WHERE sofer_id = %s", (id,))
    c.execute("DELETE FROM soferi WHERE id = %s", (id,))
    conn.commit(); conn.close()
    return redirect(url_for("add_driver"))

@app.route("/add_vehicle", methods=["GET", "POST"])
def add_vehicle():
    conn = get_db(); c = conn.cursor()
    error = None
    if request.method == "POST":
        p = request.form["plate"].upper().strip()
        m = request.form["model"]
        c.execute("SELECT id FROM vehicule WHERE plate = %s", (p,))
        if c.fetchone():
            error = f"Eroare: Vehiculul {p} există deja!"
        else:
            c.execute("INSERT INTO vehicule (plate, model) VALUES (%s, %s)", (p, m))
            conn.commit()
            return redirect(url_for("add_vehicle"))
    c.execute("SELECT * FROM vehicule ORDER BY id DESC"); v = c.fetchall()
    conn.close()
    return render_template("add_vehicle.html", vehicles=v, error=error)

@app.route("/delete_vehicle/<int:id>")
def delete_vehicle(id):
    conn = get_db(); c = conn.cursor()
    c.execute("DELETE FROM curse WHERE vehicul_id = %s", (id,))
    c.execute("DELETE FROM vehicule WHERE id = %s", (id,))
    conn.commit(); conn.close()
    return redirect(url_for("add_vehicle"))

@app.route("/add_route", methods=["GET", "POST"])
def add_route():
    conn = get_db(); c = conn.cursor()
    if request.method == "POST":
        s_id, v_id, st, en = request.form["sofer_id"], request.form["vehicul_id"], request.form["start_oras"], request.form["end_oras"]
        c.execute("SELECT name, factor_eficienta FROM soferi WHERE id = %s", (s_id,))
        s = c.fetchone()
        c.execute("SELECT plate, model FROM vehicule WHERE id = %s", (v_id,))
        v = c.fetchone()
        c.execute("INSERT INTO curse (sofer_id, sofer_nume, vehicul_id, vehicul_detalii, start_oras, end_oras, status, factor_sofer) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", 
                  (s_id, s[0], v_id, f"{v[1]} ({v[0]})", st, en, "Planned", s[1]))
        conn.commit(); conn.close()
        return redirect(url_for("index"))
    
    c.execute("SELECT * FROM soferi")
    soferi = c.fetchall()
    c.execute("SELECT id, plate, model FROM vehicule")
    vehicule = c.fetchall()
    
    c.execute("SELECT sofer_id FROM curse")
    active_drivers = [row[0] for row in c.fetchall()]
    c.execute("SELECT vehicul_id FROM curse")
    active_vehicles = [row[0] for row in c.fetchall()]
    
    conn.close()
    return render_template("add_route.html", soferi=soferi, vehicule=vehicule, orase=CITIES.keys(), active_drivers=active_drivers, active_vehicles=active_vehicles)

@app.route("/calculate", methods=["GET", "POST"])
def calculate():
    conn = get_db(); c = conn.cursor()
    result = None
    chart_labels = []
    chart_factors = []
    chart_errors = []
    
    if request.method == "POST":
        s_id, time_gps = request.form["sofer_id"], float(request.form["time_gps"])
        c.execute("SELECT name, factor_eficienta FROM soferi WHERE id = %s", (s_id,))
        driver = c.fetchone()
        
        if driver:
            traffic = random.uniform(0.95, 1.25)
            weather = random.choice([1.0, 1.05, 1.15])
            smart_time = time_gps * driver[1] * traffic * weather
            diff = time_gps - smart_time
            result = {
                "driver_name": driver[0], "gps_time": round(time_gps, 2), "smart_time": round(smart_time, 2),
                "traffic": round((traffic-1)*100, 1), "weather": round((weather-1)*100, 1),
                "efficiency": round(driver[1], 3), "optimization": "Gain" if diff > 0 else "Loss", "diff": abs(round(diff, 2))
            }
            
            # AM REZOLVAT AICI: Extragem DateTime standard si il formatam pur in Python (fara erori de MySQL)
            c.execute("SELECT factor_nou, eroare_procentUALA, data_finalizare FROM istoric_curse WHERE sofer_id = %s ORDER BY id ASC", (s_id,))
            history = c.fetchall()
            
            if history:
                # Folosim strftime() pentru a formata ora in Python
                chart_labels = [row[2].strftime('%H:%M:%S') if row[2] else "" for row in history]
                chart_factors = [row[0] for row in history]
                chart_errors = [round(row[1], 1) for row in history]
                
    c.execute("SELECT id, name, factor_eficienta FROM soferi"); soferi = c.fetchall()
    conn.close()
    return render_template("calculate.html", soferi=soferi, result=result, labels=chart_labels, factors=chart_factors, errors=chart_errors)

if __name__ == "__main__":
    app.run(debug=True)