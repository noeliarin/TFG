---
name: explore-items
description: Explores the product catalog efficiently using targeted tools to avoid overloading the LLM context window.
---

# Explore Items Skill

## Purpose
Obtener información del catálogo de productos de forma **eficiente y escalable**, sin cargar todos los datos en el contexto del LLM de una vez.

## El Problema que Resuelve
Los LLMs tienen una ventana de contexto limitada. Si cargamos todo el catálogo de golpe, se consume espacio valioso. En su lugar, este skill define un flujo de exploración progresiva.

## Herramientas Disponibles

| Herramienta | Cuándo usarla | Datos que devuelve |
|---|---|---|
| `list_item_titles()` | **Primero siempre** | Solo ID + título + precio de todos los productos (ligero) |
| `search_items_by_keyword(keyword)` | Para buscar por categoría o necesidad | IDs + títulos de los productos que coincidan |
| `get_item_details(item_id)` | Cuando ya sabes qué producto quieres analizar | Especificaciones completas de UN producto |

## Workflow Recomendado

1. **Llama a `list_item_titles()`** para ver qué productos hay disponibles (índice ligero).
2. **Llama a `search_items_by_keyword(keyword)`** si buscas algo concreto (ej: "piano", "headphones").
3. **Llama a `get_item_details(item_id)`** solo para los productos candidatos que quieras analizar en profundidad.
4. Combina esa información con el historial del usuario para hacer la recomendación.

## Ejemplo de Flujo
```
list_item_titles() → ve que hay auriculares, pianos, cables...
search_items_by_keyword("headphones") → encuentra 2 auriculares relevantes
get_item_details("B001234") → lee especificaciones completas del auricular candidato
→ Recomienda ese auricular justificando con los datos técnicos
```