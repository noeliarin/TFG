import json
import os

# Rutas a los archivos masivos que acabas de descomprimir
reviews_path = "data/raw/Musical_Instruments.jsonl"
meta_path = "data/raw/meta_Musical_Instruments.jsonl"

target_users = {}
target_asins = set()
max_users = 5

print("1. Leyendo interacciones masivas (Reviews)...")
# Leemos línea a línea para no saturar la memoria RAM
with open(reviews_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        user_id = data.get("user_id")
        asin = data.get("parent_asin")
        rating = data.get("rating")
        text = data.get("text", "")
        
        # Filtramos para quedarnos solo con 5 usuarios distintos
        if user_id not in target_users:
            if len(target_users) >= max_users:
                break
            target_users[user_id] = {"history": []}
            
        target_users[user_id]["history"].append({
            "parent_asin": asin,
            "rating": rating,
            "text": text
        })
        target_asins.add(asin)

print(f"✅ Extraídos {len(target_users)} usuarios con {len(target_asins)} productos únicos.")

print("2. Buscando metadatos del catálogo para esos productos...")
db_items = {}
with open(meta_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        asin = data.get("parent_asin")
        
        # Solo guardamos los atributos de los items que tienen nuestros 5 usuarios
        if asin in target_asins:
            db_items[asin] = {
                "title": data.get("title", "Producto sin título"),
                "price": data.get("price", "No disponible"),
                "features": data.get("features", []),
                "description": data.get("description", [])
            }
            if len(db_items) == len(target_asins):
                break # Terminamos de buscar

print("3. Guardando el micro-dataset optimizado...")
os.makedirs("data", exist_ok=True)

with open("data/db_users.json", "w", encoding="utf-8") as f:
    json.dump(target_users, f, indent=4)

with open("data/db_items.json", "w", encoding="utf-8") as f:
    json.dump(db_items, f, indent=4)

print("🚀 ¡Completado! Revisa los archivos en la carpeta data/")