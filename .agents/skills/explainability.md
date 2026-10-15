---
name: explainability
description: Explains why an Amazon product was recommended. Use this skill when the user asks "why", "how", or requests the reasoning behind a specific recommendation.
---

# Explainability Skill

## Purpose
This skill helps users understand why a specific Amazon product recommendation was generated, aiming to increase user trust, transparency, and decision-making effectiveness.

## When to use this skill
- Explain why a product was recommended to a user.
- Identify which factors (e.g., past purchases, product features, similar users) influenced a recommendation.
- Clarify the reasoning behind recommendation results.

## Current limitations
- Do not invent unrealistic features. Base your explanations strictly on the known features of the recommended products and the user's stated preferences.

## Explanation Styles
Formulate the explanation using one of these styles:
1. **Collaborative-based style**: Explain based on user similarities (e.g., "Customers who bought this item also bought...").
2. **Content-based style**: Explain based on product features (e.g., "We recommend this laptop because you prefer items with 16GB RAM and lightweight design")[cite: 100].

## Workflow
1. Identify the specific recommendation the user wants explained.
2. Identify the logical connection between the user's preferences and the product's features.
3. Determine the best Explanation Style (Collaborative or Content-based) based on the context.
4. Construct a human-understandable explanation avoiding overly technical jargon (unless requested).