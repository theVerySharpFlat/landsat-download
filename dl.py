import csv
from datetime import datetime
import json
import sys
from landsatxplore.earthexplorer import EarthExplorer

START_YEAR = 2022
END_YEAR   = 2023

START_MONTH = 4
END_MONTH   = 10

VALID_GRIDS = [(i, j) for i in range(25, 29) for j in range(30, 33)]
VALID_GRIDS.remove((28, 32))

# VALID_MONTH_STRINGS = [f"{m:02}" for m in range(START_MONTH, END_MONTH + 1)]
# VALID_YEAR_STRINGS = [str(y) for y in range(START_YEAR, END_YEAR + 1)]

product_map = {}

for y in range(START_YEAR, END_YEAR + 1):
    product_map[y] = {}
    for m in range(START_MONTH, END_MONTH + 1):
        product_map[y][m] = []

count = 0
seen = []

with open("products.csv", "r", encoding="iso-8859-1") as f:
    KEYS = []
    for i, row in enumerate(csv.reader(f)):
        if i == 0:
            KEYS = row
            continue

        date = row[KEYS.index("Date Acquired")]
        wrs = (int(row[KEYS.index("WRS Path")]), int(row[KEYS.index("WRS Row")]))

        date_object = datetime.strptime(date, "%Y/%m/%d")
        
        if not (date_object.year >= START_YEAR and date_object.year <= END_YEAR):
            continue

        if not (date_object.month >= START_MONTH and date_object.month <= END_MONTH):
            continue

        if not wrs in VALID_GRIDS:
            continue

        uid = str(date_object.year) + "/" + str(date_object.month) + "_" + str(wrs)
        if uid in seen:
            continue
        else:
            seen.append(uid)

        scene_identifier = row[KEYS.index("Landsat Scene Identifier")]

        if not scene_identifier in product_map[date_object.year][date_object.month]:
            product_map[date_object.year][date_object.month].append(scene_identifier)
            count += 1


print(json.dumps(product_map, indent=4))
print("count:", count)

ee = EarthExplorer(sys.argv[1], sys.argv[2])

for (y, months) in product_map.items():
    for (m, products) in months.items():
        for product in products:
            print(f"downloading {m}/{y}: {product}")
            ee.download(product, output_dir=f'./data/{y}/{m}', dataset="landsat_ot_c2_l2")

ee.logout()
