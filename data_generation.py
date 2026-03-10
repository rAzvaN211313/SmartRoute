import random
import string
import mysql.connector
from config import DB_CONFIG

# Date de bază
judete = ["AB","AR","AG","BC","BH","BN","BR","BT","BV","BZ","CS","CL","CJ","CT",
          "CV","DB","DJ","GL","GR","GJ","HR","HD","IL","IS","IF","MM","MH","MS",
          "NT","OT","PH","SM","SJ","SB","SV","TR","TM","TL","VS","VL"]

prenume = ["Ion","Maria","Andrei","Elena","George","Ana","Mihai","Ioana","Vasile","Cristina"]
nume = ["Popescu","Ionescu","Georgescu","Dumitrescu","Stan","Marin","Radu","Toma","Niculescu","Petrescu"]
companies = ["Transporturi SRL","RomTrans SRL","AutoLogistics SRL","CargoFast SRL","TransExpress SRL"]

# Funcții generare date
def generate_plate():
    return f"{random.choice(judete)}{random.randint(0,99):02d}{''.join(random.choices(string.ascii_uppercase, k=3))}"

def generate_phone():
    return f"+40 7{random.randint(0,9)}{random.randint(1000000,9999999)}"

def generate_driver():
    return {
        "name": f"{random.choice(prenume)} {random.choice(nume)}",
        "phone": generate_phone(),
        "company": random.choice(companies),
        "average_delay": random.randint(0,20)
    }

# Conectare MySQL
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

# Generare 10 șoferi
drivers = [generate_driver() for _ in range(10)]
for d in drivers:
    cursor.execute("INSERT INTO drivers (name, phone, company, average_delay) VALUES (%s,%s,%s,%s)",
                   (d['name'], d['phone'], d['company'], d['average_delay']))
conn.commit()

# Generare 10 vehicule
for i in range(10):
    plate = generate_plate()
    vehicle_type = random.choice(['Camion','Basculă'])
    driver_id = i + 1
    cursor.execute("INSERT INTO vehicles (license_plate, type, driver_id) VALUES (%s,%s,%s)",
                   (plate, vehicle_type, driver_id))
conn.commit()

# Generare 10 curse simulate (coord. orașe)
locations = [
    (44.4268, 26.1025), (45.7489, 21.2087), (46.7712, 23.6236),
    (45.7983, 24.1256), (45.6574, 25.6012), (44.1807, 28.6348),
    (47.1585, 27.6014), (44.8500, 24.8667), (47.0465, 21.9189), (44.3181, 23.8008)
]

for i in range(10):
    start_lat, start_lng = locations[i]
    end_lat = start_lat + random.uniform(0.01,0.05)
    end_lng = start_lng + random.uniform(0.01,0.05)
    estimated = random.randint(20,60)
    actual = estimated + random.randint(-5,10)
    cursor.execute("INSERT INTO trips (vehicle_id, start_lat, start_lng, end_lat, end_lng, estimated_time, actual_time) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                   (i+1, start_lat, start_lng, end_lat, end_lng, estimated, actual))
conn.commit()
cursor.close()
conn.close()

print("Date generate cu succes în MySQL!")