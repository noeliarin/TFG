---
name: explore-items
description: Explores the product catalog efficiently using targeted tools to avoid overloading the LLM context window.
---

# Explore Items Skill

## Purpose
Obtener información del catálogo de productos de forma **eficiente y escalable**, sin sobrecargar la ventana de contexto ni agotar la tasa de peticiones (rate limit).

## Reglas Críticas de Exploración
1. **Evita la sobre-búsqueda (Spam de sinónimos):**
   - Usa como máximo **1 o 2 keywords** por consulta (ej: si buscas "auriculares", busca "headphone" una sola vez). No hagas búsquedas repetidas con sinónimos (headphone, earphone, headset, earbuds) en la misma interacción.
2. **Verifica siempre antes de concluir o descartar:**
   - Si `search_items_by_keyword()` te devuelve candidatos, **llama a `get_item_details(item_id)` para los 2-3 más prometedores** para ver qué son exactamente.
   - Si tras verificar ves que ningún producto coincide con lo que el usuario pide (o el catálogo no tiene esa categoría), **admítelo con claridad**: explica qué productos relacionados hay en el catálogo y NUNCA te inventes modelos externos.
3. **Catálogo cerrado:**
   - Todo producto que recomiendes con precio y ficha técnica DEBE provenir de las herramientas (`db_items.json`). Jamás menciones modelos externos inventados como sugerencias de compra directas.

## Herramientas Disponibles

| Herramienta | Cuándo usarla | Datos que devuelve |
|---|---|---|
| `search_items_by_keyword(keyword)` | Para buscar por categoría o necesidad | IDs + títulos de los productos coincidentes |
| `get_item_details(item_id)` | Para inspeccionar especificaciones técnicas reales | Título, precio, features y descripción de UN producto |
| `list_item_titles()` | Solo para exploración panorámica inicial cuando no hay palabra clave | Muestra primeros 15 títulos del catálogo |

## Workflow Recomendado
1. Identifica qué busca el usuario o qué se desprende de su historial.
2. Haz **UNA única búsqueda concisa** con `search_items_by_keyword(keyword)`.
3. Revisa los resultados devueltos:
   - Si hay candidatos: llama a `get_item_details(item_id)` de los 2 más relevantes.
   - Si no hay coincidencias: informa al usuario de qué categorías/alternativas existen en el catálogo en base a lo que sabes.
4. Genera la respuesta sin inventar productos.