import json
import os

reviews_path = "data/raw/Musical_Instruments.jsonl"
meta_path = "data/raw/meta_Musical_Instruments.jsonl"

print("1. Extrayendo usuarios con buen historial (2 a 5 compras)...")

# Aseguramos que incluimos al usuario de prueba actual
CURRENT_TEST_USER = "AGCI7FAH4GL5FI65HYLKWTMFZ2CQ"

user_counts = {}
user_reviews = {}
target_asins = set()
desired_users = 15

with open(reviews_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        user_id = data.get("user_id")
        asin = data.get("parent_asin")
        rating = data.get("rating")
        text = data.get("text", "")

        if not user_id or not asin:
            continue

        if user_id not in user_reviews:
            user_reviews[user_id] = []

        user_reviews[user_id].append({
            "parent_asin": asin,
            "rating": rating,
            "text": text[:300] # Limitar texto para ahorrar espacio
        })

        # Parar si ya tenemos suficientes usuarios con múltiples compras
        if len(user_reviews) > 20000:
            break

# Seleccionar usuarios con 2 a 5 compras
final_users = {}

# Meter primero al usuario de prueba si está
if CURRENT_TEST_USER in user_reviews:
    final_users[CURRENT_TEST_USER] = {"history": user_reviews[CURRENT_TEST_USER]}
    for r in user_reviews[CURRENT_TEST_USER]:
        target_asins.add(r["parent_asin"])

for uid, revs in user_reviews.items():
    if len(final_users) >= desired_users:
        break
    if uid == CURRENT_TEST_USER:
        continue
    if 2 <= len(revs) <= 5:
        final_users[uid] = {"history": revs}
        for r in revs:
            target_asins.add(r["parent_asin"])

print(f"✅ Seleccionados {len(final_users)} usuarios con {len(target_asins)} productos en sus historiales.")

print("2. Construyendo catálogo ampliado (historial + productos nuevos para recomendar)...")
db_items = {}
extra_catalog_limit = 50 # 50 productos extra de distintas categorías
extra_count = 0

with open(meta_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        asin = data.get("parent_asin")
        title = data.get("title", "")
        
        # Saltar items sin título
        if not title or title == "Producto sin título":
            continue

        # Limpiar features y descripción para no meter paja
        features = data.get("features", [])[:4]
        desc = data.get("description", [])[:2]
        price = data.get("price")
        cats = data.get("categories", [])

        # 1. Si es un producto del historial de los usuarios, lo guardamos obligatoriamente
        if asin in target_asins and asin not in db_items:
            db_items[asin] = {
                "title": title,
                "price": price if price else "Consultar",
                "categories": cats,
                "features": features,
                "description": desc
            }

        # 2. Si no es del historial, guardamos hasta 50 productos variados para que el catálogo tenga oferta
        elif extra_count < extra_catalog_limit and asin not in db_items:
            if price and len(features) > 0: # Solo productos con precio e información técnica
                db_items[asin] = {
                    "title": title,
                    "price": price,
                    "categories": cats,
                    "features": features,
                    "description": desc
                }
                extra_count += 1

        if len(db_items) >= (len(target_asins) + extra_catalog_limit):
            break

print(f"✅ Catálogo finalizado: {len(db_items)} productos en total ({extra_count} productos nuevos para recomendar).")

print("3. Guardando archivos en data/...")
with open("data/db_users.json", "w", encoding="utf-8") as f:
    json.dump(final_users, f, indent=2, ensure_ascii=False)

with open("data/db_items.json", "w", encoding="utf-8") as f:
    json.dump(db_items, f, indent=2, ensure_ascii=False)

print("🚀 ¡Completado con éxito!")

