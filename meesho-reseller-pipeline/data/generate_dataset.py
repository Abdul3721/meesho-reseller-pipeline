"""STAND-IN dataset generator - REPLACE WITH THE SCRIPT SUPPLIED IN THE BRIEF.

The lecture deck only describes the generator (random.Random(42), 24 resellers, 900 orders,
fixed status weights); it does not contain the script itself. This file follows that
description so the repo runs end to end, but its random sequence will NOT reproduce the
brief's acceptance values (e.g. April Ethnic Wear = 104520.77). Paste the brief's script
here verbatim - with zero changes to seed, weights or row counts - and re-run it.

Writes next to this file: resellers.csv, orders.csv, meesho_reseller.db
"""
import csv
import os
import random
import sqlite3

HERE = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(42)                                   # fixed seed - do not change

REGIONS = {
    "North": ["Delhi", "Jaipur", "Lucknow"],
    "West": ["Mumbai", "Pune", "Ahmedabad"],
    "South": ["Bengaluru", "Chennai", "Hyderabad"],
    "East": ["Kolkata", "Patna", "Bhubaneswar"],
}
CATEGORIES = ["Ethnic Wear", "Western Wear", "Kids Wear", "Home & Kitchen", "Beauty & Personal Care"]
MONTHS = ["April", "May", "June"]
STATUSES = ["Delivered", "Returned", "Cancelled", "Pending"]
WEIGHTS = [0.70, 0.15, 0.10, 0.05]
ORDERS_PER_MONTH = 300

# 24 resellers = 4 regions x 6 (3 cities per region)
resellers = []
for region, cities in REGIONS.items():
    for i in range(1, 7):
        city = cities[(i - 1) % 3]
        resellers.append({"reseller_id": f"RS{len(resellers) + 1:03d}",
                          "reseller_name": f"{city} Reseller {i}",
                          "region": region, "city": city})

# RS024 is deliberately left without orders (the zero-order reseller)
active_ids = [r["reseller_id"] for r in resellers if r["reseller_id"] != "RS024"]

orders = []
for month in MONTHS:
    for _ in range(ORDERS_PER_MONTH):
        orders.append({
            "order_id": f"ORD{len(orders) + 1:04d}",
            "reseller_id": rng.choice(active_ids),
            "month": month,
            "category": rng.choice(CATEGORIES),
            "quantity": rng.randint(1, 5),
            "unit_price": round(rng.uniform(150, 1200), 2),
            "status": rng.choices(STATUSES, weights=WEIGHTS)[0],
        })

assert len(resellers) == 24 and len(orders) == 900


def write_csv(name, rows):
    with open(os.path.join(HERE, name), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


write_csv("resellers.csv", resellers)
write_csv("orders.csv", orders)

db_path = os.path.join(HERE, "meesho_reseller.db")
if os.path.exists(db_path):
    os.remove(db_path)
con = sqlite3.connect(db_path)
con.execute("CREATE TABLE resellers (reseller_id TEXT PRIMARY KEY, reseller_name TEXT, region TEXT, city TEXT)")
con.execute("""CREATE TABLE orders (order_id TEXT PRIMARY KEY, reseller_id TEXT, month TEXT, category TEXT,
               quantity INTEGER, unit_price REAL, status TEXT)""")
con.executemany("INSERT INTO resellers VALUES (:reseller_id,:reseller_name,:region,:city)", resellers)
con.executemany("INSERT INTO orders VALUES (:order_id,:reseller_id,:month,:category,:quantity,:unit_price,:status)", orders)
con.commit()
con.close()
print(f"Generated {len(resellers)} resellers and {len(orders)} orders in {HERE}")
