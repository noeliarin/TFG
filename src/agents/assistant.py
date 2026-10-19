import json
import os
import time
import logging
from dotenv import load_dotenv

# Carga automáticamente las variables de entorno desde el archivo .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

# =========================================================
# LOGGING — Para trazar las tool calls del agente
# =========================================================
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)-5s | %(message)s',
    datefmt='%H:%M:%S',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, 'tools.log'), encoding='utf-8'),
        logging.StreamHandler()  # También imprime en consola del servidor
    ]
)
logger = logging.getLogger('recommender')

triggers = {'webhook': True}

# =========================================================
# HERRAMIENTAS DEL AGENTE (Tools)
# Diseñadas para no sobrecargar la ventana de contexto del LLM.
# En lugar de cargar TODO el catálogo de golpe, el agente
# puede explorar el catálogo de forma selectiva y eficiente.
# =========================================================

# Diccionario rápido de equivalencias español -> inglés para el catálogo
SPANISH_TO_ENGLISH_TERMS = {
    "amplificador": "amplifier",
    "amplificadores": "amplifier",
    "ampli": "amp",
    "altavoz": "speaker",
    "altavoces": "speaker",
    "auricular": "headphone",
    "auriculares": "headphone",
    "cascos": "headphone",
    "guitarra": "guitar",
    "guitarras": "guitar",
    "bajo": "bass",
    "microfono": "microphone",
    "microfonos": "microphone",
    "micro": "mic",
    "micros": "mic",
    "teclado": "keyboard",
    "teclados": "keyboard",
    "cuerda": "string",
    "cuerdas": "strings",
    "soporte": "stand",
    "soportes": "stand",
    "luz": "light",
    "luces": "lighting",
    "bateria": "drum",
    "baterias": "drums",
    "directo": "live",
    "sonido": "sound"
}


def get_user_history(user_id: str) -> dict:
    """
    Retrieves the interaction history and past ratings for a specific user.
    Always use this tool FIRST to understand what the user likes and dislikes.
    Returns their purchase history with ratings and review text.
    """
    t0 = time.time()
    logger.info(f"🔧 TOOL CALL: get_user_history(user_id='{user_id}')")
    try:
        with open('data/db_users.json', 'r', encoding='utf-8') as f:
            users_db = json.load(f)
        result = users_db.get(user_id, {"error": "Usuario no encontrado en la base de datos"})
        dt = round(time.time() - t0, 3)
        if "error" in result:
            logger.warning(f"  ⚠ Usuario '{user_id}' NO encontrado ({dt}s)")
        else:
            n_items = len(result.get("history", []))
            logger.info(f"  ✅ Usuario encontrado: {n_items} items en historial ({dt}s)")
        return result
    except Exception as e:
        logger.error(f"  ❌ Error en get_user_history: {e}")
        return {"error": f"Database error: {e}"}


def list_item_titles(limit: int = 10) -> dict:
    """
    Returns a brief sample index of available products: ID and short title.
    Limit is capped at 10 items to prevent context overflow.
    Use search_items_by_keyword() for targeted queries instead.
    """
    t0 = time.time()
    capped_limit = min(limit, 10)
    logger.info(f"🔧 TOOL CALL: list_item_titles(limit={capped_limit})")
    try:
        with open('data/db_items.json', 'r', encoding='utf-8') as f:
            items_db = json.load(f)
        
        result = {}
        for i, (item_id, item_data) in enumerate(items_db.items()):
            if i >= capped_limit:
                break
            result[item_id] = {
                "title": item_data.get("title", "")[:50] + "...",
                "price": item_data.get("price", "Consultar")
            }
        dt = round(time.time() - t0, 3)
        logger.info(f"  ✅ Devueltos {len(result)} items ({dt}s)")
        return result
    except Exception as e:
        logger.error(f"  ❌ Error en list_item_titles: {e}")
        return {"error": f"Database error: {e}"}


def get_item_details(item_id: str) -> dict:
    """
    Retrieves key specifications and description for ONE specific product.
    Args:
        item_id: The product's unique identifier.
    """
    t0 = time.time()
    logger.info(f"🔧 TOOL CALL: get_item_details(item_id='{item_id}')")
    try:
        with open('data/db_items.json', 'r', encoding='utf-8') as f:
            items_db = json.load(f)
        item = items_db.get(item_id)
        if item:
            # Mantener contenido conciso para evitar el error 413 (Payload Too Large)
            raw_features = item.get("features", [])
            clean_features = [f[:100] for f in raw_features[:2]]
            raw_desc = item.get("description", [])
            clean_desc = [d[:150] for d in raw_desc[:1]]

            result = {
                "title": item.get("title", "")[:80],
                "price": item.get("price"),
                "features": clean_features,
                "description": clean_desc
            }
            dt = round(time.time() - t0, 3)
            logger.info(f"  ✅ Item encontrado: '{result['title'][:40]}' ({dt}s)")
            return result
        dt = round(time.time() - t0, 3)
        logger.warning(f"  ⚠ Item '{item_id}' NO encontrado ({dt}s)")
        return {"error": f"Producto '{item_id}' no encontrado."}
    except Exception as e:
        logger.error(f"  ❌ Error en get_item_details: {e}")
        return {"error": f"Database error: {e}"}


def search_items_by_keyword(keyword: str, max_results: int = 4) -> dict:
    """
    Searches the product catalog for items matching a keyword or phrase.
    NOTE: The catalog database is in English. Always provide the keyword in English (e.g., 'cable', 'stand', 'amplifier', 'keyboard').
    Returns at most 'max_results' (max 4) items.
    """
    t0 = time.time()
    capped_max = min(max_results, 4)
    logger.info(f"🔧 TOOL CALL: search_items_by_keyword(keyword='{keyword}', max_results={capped_max})")
    try:
        with open('data/db_items.json', 'r', encoding='utf-8') as f:
            items_db = json.load(f)
        
        kw_clean = keyword.lower().strip()
        # Traducir si hay término directo en el diccionario
        translated_kw = SPANISH_TO_ENGLISH_TERMS.get(kw_clean, kw_clean)

        # Extraer palabras individuales (tokens)
        query_words = set(translated_kw.split() + kw_clean.split())
        query_words = {w for w in query_words if len(w) > 2}  # Ignorar palabras de 1 o 2 letras

        scored_items = []
        for item_id, item_data in items_db.items():
            searchable_text = " ".join([
                item_data.get("title", ""),
                " ".join(item_data.get("categories", [])),
                " ".join(item_data.get("features", [])),
                " ".join(item_data.get("description", []))
            ]).lower()
            
            # Puntuación: frase exacta (5 pts), palabras individuales que coinciden (1 pt cada una)
            score = 0
            if kw_clean in searchable_text or translated_kw in searchable_text:
                score += 5
            
            matched_words = sum(1 for w in query_words if w in searchable_text)
            score += matched_words

            # Si contiene todas las palabras o la frase exacta, es un match fuerte
            if score > 0 and (matched_words == len(query_words) or score >= 5):
                scored_items.append((score, item_id, item_data))
        
        # Ordenar por relevancia descendente
        scored_items.sort(key=lambda x: x[0], reverse=True)

        matches = {}
        for _, item_id, item_data in scored_items[:capped_max]:
            matches[item_id] = {
                "title": item_data.get("title", "")[:60] + "...",
                "price": item_data.get("price", "Consultar")
            }
        
        dt = round(time.time() - t0, 3)
        if not matches:
            logger.info(f"  ⚠ Sin resultados para '{keyword}' ({dt}s)")
            return {"message": f"No hay coincidencias para '{keyword}'."}
        logger.info(f"  ✅ {len(matches)} resultados para '{keyword}': {list(matches.keys())} ({dt}s)")
        return matches
    except Exception as e:
        logger.error(f"  ❌ Error en search_items_by_keyword: {e}")
        return {"error": f"Database error: {e}"}


async def default(context):
    user_prompt = context.payload.get('prompt', '')
    session_id = context.agent_id
    
    logger.info(f"{'='*60}")
    logger.info(f"📩 NUEVA PETICIÓN | sesión={session_id}")
    logger.info(f"   Prompt: {user_prompt[:150]}{'...' if len(user_prompt) > 150 else ''}")
    logger.info(f"{'='*60}")
    
    t0 = time.time()
    
    # Registramos las 4 herramientas disponibles para el agente
    agent = await context.init(tools=[
        get_user_history,
        list_item_titles,
        get_item_details,
        search_items_by_keyword
    ])
    
    session = await agent.session(session_id)
    result = await session.prompt(user_prompt)
    
    dt = round(time.time() - t0, 1)
    logger.info(f"✅ RESPUESTA GENERADA | {dt}s | {len(result.text)} chars")
    logger.info(f"{'='*60}\n")
    
    return {'text': result.text, 'metadata': result.metadata}