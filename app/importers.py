import csv, urllib.request
from datetime import datetime

AIRPORTS_URL = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"
AIRPORTS_FILE = "/tmp/airports.dat"

def download_airports():
    urllib.request.urlretrieve(AIRPORTS_URL, AIRPORTS_FILE)

def parse_airports():
    data = {}
    with open(AIRPORTS_FILE, encoding="utf-8") as f:
        reader = csv.reader(f)
        for r in reader:
            code = r[4].strip('"')
            name = r[1].strip('"')
            try:
                lat = float(r[6]); lon = float(r[7])
            except:
                continue
            if code:
                data[code] = (name, lat, lon)
    return data

def import_openflights(csv_path, db, create_fn):
    download_airports()
    airport_map = parse_airports()
    with open(csv_path, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            frm, to = row["From"], row["To"]
            name_f, lat1, lon1 = airport_map.get(frm, (frm, None, None))
            name_t, lat2, lon2 = airport_map.get(to, (to, None, None))
            payload = {
                "type": "plane",
                "name": f"{frm} → {to}",
                "description": f"{row['Airline']} • {row['Distance']} mi • {row['Duration']}",
                "date": datetime.strptime(row["Date"], "%m/%d/%Y"),
                "origin_latitude": lat1,
                "origin_longitude": lon1,
                "destination_latitude": lat2,
                "destination_longitude": lon2,
                "extra": {
                    "distance": int(row["Distance"]),
                    "duration": row["Duration"],
                }
            }
            import asyncio
            asyncio.get_event_loop().run_until_complete(create_fn(db, **payload))
