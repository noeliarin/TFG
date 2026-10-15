import json
import os
from dotenv import load_dotenv

# Carga automáticamente las variables de entorno desde el archivo .env
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '..', '..', '.env'))

triggers = {'webhook': True}

# =========================================================
# HERRAMIENTAS DEL AGENTE (Tools)
# Diseñadas para no sobrecargar la ventana de contexto del LLM.
# En lugar de cargar TODO el catálogo de golpe, el agente
# puede explorar el catálogo de forma selectiva y eficiente.
# =========================================================

def get_user_history(user_id: str) -> dict:
    """
    Retrieves the interaction history and past ratings for a specific user.
    Always use this tool FIRST to understand what the user likes and dislikes.
    Returns their purchase history with ratings and review text.
    """
    try:
        with open('data/db_users.json', 'r', encoding='utf-8') as f:
            users_db = json.load(f)
        return users_db.get(user_id, {"error": "Usuario no encontrado en la base de datos"})
    except Exception as e:
        return {"error": f"Database error: {e}"}


def list_item_titles(limit: int = 15) -> dict:
    """
    Returns a lightweight sample index of available products: ID, short title, and price.
    Returns at most 'limit' items (default 15) to keep the context window small and efficient.
    Use search_items_by_keyword() if you want to find items related to a specific category.
    """
    try:
        with open('data/db_items.json', 'r', encoding='utf-8') as f:
            items_db = json.load(f)
        
        result = {}
        for i, (item_id, item_data) in enumerate(items_db.items()):
            if i >= limit:
                break
            result[item_id] = {
                "title": item_data.get("title", "")[:60] + "...",
                "price": item_data.get("price", "Consultar")
            }
        return result
    except Exception as e:
        return {"error": f"Database error: {e}"}


def get_item_details(item_id: str) -> dict:
    """
    Retrieves the full technical specifications and description for ONE specific product.
    Use this after search_items_by_keyword() to deep-dive into a product you consider relevant.
    Args:
        item_id: The product's unique identifier.
    """
    try:
        with open('data/db_items.json', 'r', encoding='utf-8') as f:
            items_db = json.load(f)
        item = items_db.get(item_id)
        if item:
            return {
                "title": item.get("title"),
                "price": item.get("price"),
                "features": item.get("features", [])[:4],
                "description": item.get("description", [])[:2]
            }
        return {"error": f"Producto con ID '{item_id}' no encontrado en el catálogo."}
    except Exception as e:
        return {"error": f"Database error: {e}"}


def search_items_by_keyword(keyword: str, max_results: int = 6) -> dict:
    """
    Searches the product catalog for items matching a keyword (e.g., 'headphones', 'piano', 'pedal', 'cable').
    Returns at most 'max_results' (default 6) to be token-efficient.
    Args:
        keyword: A word or short phrase to search for.
        max_results: Max number of matching items to return.
    """
    try:
        with open('data/db_items.json', 'r', encoding='utf-8') as f:
            items_db = json.load(f)
        
        keyword_lower = keyword.lower()
        matches = {}
        for item_id, item_data in items_db.items():
            # Buscamos en título, categorías, características y descripción
            searchable_text = " ".join([
                item_data.get("title", ""),
                " ".join(item_data.get("categories", [])),
                " ".join(item_data.get("features", [])),
                " ".join(item_data.get("description", []))
            ]).lower()
            
            if keyword_lower in searchable_text:
                matches[item_id] = {
                    "title": item_data.get("title", "")[:65] + "...",
                    "price": item_data.get("price", "Consultar")
                }
                if len(matches) >= max_results:
                    break
        
        if not matches:
            return {"message": f"No se encontraron productos para '{keyword}'. Prueba con otro término."}
        return matches
    except Exception as e:
        return {"error": f"Database error: {e}"}


async def default(context):
    # Registramos las 4 herramientas disponibles para el agente
    agent = await context.init(tools=[
        get_user_history,
        list_item_titles,
        get_item_details,
        search_items_by_keyword
    ])
    
    session = await agent.session(context.agent_id)
    user_prompt = context.payload.get('prompt', '')
    result = await session.prompt(user_prompt)
    
    return {'text': result.text, 'metadata': result.metadata}