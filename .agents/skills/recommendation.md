---
name: recommendation
description: Handles recommendation-related requests for the Amazon e-commerce domain. Use this skill to generate, analyse, rank, or suggest products for a user based on their preferences or context.
---

# Recommendation Skill

## Purpose
This skill handles tasks related to generating e-commerce product recommendations.

## When to use this skill
- When the user asks for product suggestions (e.g., "What laptop should I buy?").
- When the user wants to see items similar to a specific product.
- To rank a list of Amazon products based on user preferences.

## Current limitations
- **Catálogo cerrado estricto:** El agente SOLO puede recomendar productos existentes en `db_items.json`. Está TERMINANTEMENTE PROHIBIDO inventar o recomendar marcas y modelos que no estén en la base de datos (por ejemplo, inventar Sennheiser, Sony o Audio-Technica si no existen en los resultados de las herramientas).
- Si no hay productos del tipo pedido en el catálogo, comunícaselo honestamente al usuario y pregúntale si prefiere explorar categorías relacionadas que sí estén disponibles.
- Si se requiere explicación, apóyate en la skill `explainability`.

## Mandatory Preconditions
First, use the user's interaction history (obtained via `explore-users`) to infer their preferences, favorite categories, and needs. ONLY ask the user for more details if their history is empty or you cannot infer what they might like.

## Presentation Formats
Depending on the user's request, present the results in one of these formats:
1. **Top N-items**: Present a ranked list of the best items for the user, assuming they just want to find some good items[cite: 100].
2. **Similar to top item**: If the user mentions a specific product, recommend alternative or complementary items[cite: 100].

## Workflow
1. **Identidad:** Identifica el `user_id` del usuario que hace la petición.
2. **Datos del usuario:** Utiliza el historial del usuario obtenido por la skill `explore-users`.
3. **Datos del catálogo:** Utiliza el catálogo obtenido por la skill `explore-items`.
4. **Análisis:** Cruza los atributos del perfil de usuario con los atributos de los ítems para encontrar la mejor sugerencia.
5. **Generación:** Presenta la recomendación final. Si el usuario pide explicación, invoca la skill `explainability`.