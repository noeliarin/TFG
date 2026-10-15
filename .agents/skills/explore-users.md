---
name: explore-users
description: Retrieves a user's interaction history and past ratings from the local database.
---

# Explore Users Skill

## Purpose
Obtiene el historial de interacciones de un usuario para modelar sus preferencias antes de generar una recomendación.

## Workflow
Para obtener los datos, NO uses la herramienta bash. En su lugar, invoca directamente la herramienta nativa `get_user_history` proporcionando el ID del usuario.
Analiza la salida de esa herramienta para identificar qué productos ha consumido el usuario, su rating y las reseñas asociadas.