"""Generate the synthetic star-schema dataset used by the Power BI model.

Deterministic (fixed seed) so the numbers in the README always match.
Run:  python scripts/generate_data.py
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(42)
OUT = Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)

CATEGORIES = {
    "Laptops": [("Laptop 14 Basic", 650, 470), ("Laptop 15 Pro", 1150, 820), ("Laptop 13 Ultra", 1490, 1050)],
    "Monitors": [("Monitor 24 FHD", 180, 120), ("Monitor 27 QHD", 320, 215), ("Monitor 34 Wide", 540, 360)],
    "Accessories": [("Wireless Mouse", 25, 11), ("Mechanical Keyboard", 85, 44), ("USB-C Dock", 140, 82), ("Headset", 70, 35)],
    "Networking": [("Wi-Fi Router AX", 160, 98), ("Access Point", 210, 130), ("Network Switch 24p", 290, 185)],
    "Printers": [("Laser Printer", 260, 170), ("Label Printer", 330, 210), ("Toner Cartridge", 75, 38)],
}
STORES = [
    ("Buenos Aires Centro", "Argentina", "South"), ("Córdoba", "Argentina", "South"), ("Rosario", "Argentina", "South"),
    ("Santiago", "Chile", "South"), ("Montevideo", "Uruguay", "South"),
    ("Bogotá", "Colombia", "North"), ("Medellín", "Colombia", "North"), ("Lima", "Peru", "North"),
    ("Ciudad de México", "Mexico", "Central"), ("Guadalajara", "Mexico", "Central"), ("San José", "Costa Rica", "Central"),
    ("Online Store", "LATAM", "Online"),
]
CHANNEL_BY_STORE = {name: ("Online" if name == "Online Store" else "In-store") for name, _, _ in STORES}

products = []
pk = 1
for cat, items in CATEGORIES.items():
    for name, price, cost in items:
        products.append({"ProductKey": pk, "Product": name, "Category": cat, "ListPrice": price, "UnitCost": cost})
        pk += 1
stores = [{"StoreKey": i + 1, "Store": s, "Country": c, "Region": r, "Channel": CHANNEL_BY_STORE[s]} for i, (s, c, r) in enumerate(STORES)]

start, end = date(2025, 1, 1), date(2026, 10, 31)
sales, order_id = [], 100000
d = start
while d <= end:
    season = 1.35 if d.month in (11, 12) else (0.85 if d.month in (1, 2) else 1.0)
    growth = 1 + 0.18 * ((d - start).days / 365)          # ~18% YoY growth
    weekday = 0.7 if d.weekday() >= 5 else 1.0
    n_orders = max(1, int(random.gauss(9, 3) * season * growth * weekday))
    for _ in range(n_orders):
        order_id += 1
        st = random.choices(stores, weights=[9, 4, 4, 5, 3, 5, 3, 4, 7, 3, 2, 10])[0]
        p = random.choices(products, weights=[6, 5, 2, 7, 5, 3, 12, 8, 6, 7, 4, 3, 3, 3, 2, 6])[0]
        qty = 1 if p["ListPrice"] > 500 else random.choice([1, 1, 2, 2, 3, 5])
        disc = random.choices([0, 0.05, 0.10, 0.15], weights=[70, 15, 10, 5])[0]
        sales.append({"OrderID": order_id, "OrderDate": d.isoformat(), "ProductKey": p["ProductKey"], "StoreKey": st["StoreKey"],
                      "Quantity": qty, "UnitPrice": p["ListPrice"], "UnitCost": p["UnitCost"], "DiscountPct": disc})
    d += timedelta(days=1)

# Monthly sales targets per region (used for "vs Target" measures)
targets = []
for y in (2025, 2026):
    for m in range(1, 13):
        if date(y, m, 1) > end:
            break
        for region, base in {"South": 47000, "North": 22500, "Central": 22500, "Online": 19000}.items():
            season = 1.3 if m in (11, 12) else (0.88 if m in (1, 2) else 1.0)
            targets.append({"Region": region, "MonthStart": date(y, m, 1).isoformat(),
                            "TargetAmount": round(base * season * (1.15 if y == 2026 else 1.0), -2)})


def write(name, rows):
    with open(OUT / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{name}: {len(rows)} rows")


write("Products.csv", products)
write("Stores.csv", stores)
write("Sales.csv", sales)
write("Targets.csv", targets)
