import os
import json
import base64
from typing import Optional, List
import httpx
from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

SYSTEM_PROMPT = """Tu es KOKORIKO, un assistant avicole intelligent pour les éleveurs africains de poules pondeuses.
Tu aides à identifier les problèmes de production, santé, alimentation, température, biosécurité et rentabilité.
Tu donnes des conseils simples, pratiques et adaptés au contexte rural africain (Burkina Faso, Mali, Sénégal, Côte d'Ivoire, etc.).
Tu utilises un langage simple, accessible, sans jargon technique complexe.
Tu ne remplaces jamais un vétérinaire.
En cas de maladie grave, forte mortalité, symptômes respiratoires sévères ou doute, tu recommandes toujours de contacter rapidement un vétérinaire.
Tu ne donnes JAMAIS de dosages médicaux précis sans validation vétérinaire.

Quand tu diagnostiques un problème, structure ta réponse avec:
- DIAGNOSTIC: (diagnostic probable)
- GRAVITE: (faible / moyen / urgent)
- CAUSES: (liste des causes possibles)
- ACTIONS IMMEDIATES: (ce que l'éleveur doit faire maintenant)
- BIOSECURITE: (conseils de prévention)
- TRAITEMENT: (traitement général non dangereux si applicable)
- VETERINAIRE: (recommander oui/non et pourquoi)

Réponds toujours en français simple et clair."""

async def ask_ai(
    question: str,
    images_base64: Optional[List[str]] = None,
    context: Optional[str] = None
) -> dict:
    """
    Envoie une question à l'IA (OpenAI ou Gemini) et retourne la réponse structurée.
    """
    full_question = question
    if context:
        full_question = f"Contexte de l'élevage: {context}\n\nQuestion: {question}"

    if AI_PROVIDER == "gemini" and GEMINI_API_KEY:
        return await _ask_gemini(full_question, images_base64)
    elif AI_PROVIDER == "openai" and OPENAI_API_KEY:
        return await _ask_openai(full_question, images_base64)
    else:
        # Mode démo si pas d'API key
        return _demo_response(question)


async def _ask_openai(question: str, images_base64: Optional[List[str]] = None) -> dict:
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    if images_base64:
        content = [{"type": "text", "text": question}]
        for img in images_base64:
            content.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img}"}
            })
        messages.append({"role": "user", "content": content})
    else:
        messages.append({"role": "user", "content": question})
    
    payload = {
        "model": "gpt-4o",
        "messages": messages,
        "max_tokens": 1000,
        "temperature": 0.7
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        
    raw_response = data["choices"][0]["message"]["content"]
    tokens = data.get("usage", {}).get("total_tokens", 0)
    
    return {
        "reponse": raw_response,
        "tokens": tokens,
        "provider": "openai",
        **_parse_ai_response(raw_response)
    }


async def _ask_gemini(question: str, images_base64: Optional[List[str]] = None) -> dict:
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    parts = [{"text": f"{SYSTEM_PROMPT}\n\n{question}"}]
    
    if images_base64:
        for img in images_base64:
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": img
                }
            })
    
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 1000
        }
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
    
    raw_response = data["candidates"][0]["content"]["parts"][0]["text"]
    
    return {
        "reponse": raw_response,
        "tokens": 0,
        "provider": "gemini",
        **_parse_ai_response(raw_response)
    }


def _parse_ai_response(text: str) -> dict:
    """Parse la réponse IA pour extraire les sections structurées."""
    result = {
        "diagnostic_probable": None,
        "niveau_gravite": "moyen",
        "causes_possibles": [],
        "actions_immediates": [],
        "conseils_biosecurite": [],
        "traitement_propose": None,
        "recommande_veterinaire": False
    }
    
    lines = text.split('\n')
    current_section = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if "DIAGNOSTIC:" in line.upper():
            result["diagnostic_probable"] = line.split(":", 1)[-1].strip()
        elif "GRAVITE:" in line.upper() or "GRAVITÉ:" in line.upper():
            gravite = line.split(":", 1)[-1].strip().lower()
            if "urgent" in gravite:
                result["niveau_gravite"] = "urgent"
            elif "faible" in gravite:
                result["niveau_gravite"] = "faible"
            else:
                result["niveau_gravite"] = "moyen"
        elif "CAUSES:" in line.upper():
            current_section = "causes"
        elif "ACTIONS" in line.upper():
            current_section = "actions"
        elif "BIOSECURITE:" in line.upper() or "BIOSÉCURITÉ:" in line.upper():
            current_section = "biosecurite"
        elif "TRAITEMENT:" in line.upper():
            result["traitement_propose"] = line.split(":", 1)[-1].strip()
            current_section = "traitement"
        elif "VETERINAIRE:" in line.upper() or "VÉTÉRINAIRE:" in line.upper():
            vet_text = line.split(":", 1)[-1].strip().lower()
            result["recommande_veterinaire"] = "oui" in vet_text or "contacter" in vet_text
            current_section = None
        elif line.startswith(("-", "•", "*")) and current_section:
            item = line.lstrip("-•* ").strip()
            if current_section == "causes":
                result["causes_possibles"].append(item)
            elif current_section == "actions":
                result["actions_immediates"].append(item)
            elif current_section == "biosecurite":
                result["conseils_biosecurite"].append(item)
    
    # Si urgent -> toujours recommander vétérinaire
    if result["niveau_gravite"] == "urgent":
        result["recommande_veterinaire"] = True
    
    return result


def _demo_response(question: str) -> dict:
    """Réponse de démonstration si aucune clé API n'est configurée."""
    return {
        "reponse": f"""🐔 KOKORIKO IA - Mode Démonstration

DIAGNOSTIC: Analyse de votre question: "{question[:100]}..."

GRAVITE: moyen

CAUSES:
- Cause possible 1 (mode démo)
- Cause possible 2 (mode démo)

ACTIONS IMMEDIATES:
- Surveiller de près vos poules
- Noter les observations quotidiennement
- Vérifier l'alimentation et l'eau

BIOSECURITE:
- Nettoyer régulièrement le poulailler
- Isoler les poules malades

TRAITEMENT: Consultez un vétérinaire pour un traitement adapté

VETERINAIRE: Oui - Configurez votre clé API OpenAI ou Gemini dans le fichier .env pour un diagnostic complet.""",
        "diagnostic_probable": "Mode démonstration - configurez API_KEY",
        "niveau_gravite": "moyen",
        "causes_possibles": ["Clé API non configurée", "Mode démonstration actif"],
        "actions_immediates": ["Configurer OPENAI_API_KEY ou GEMINI_API_KEY dans .env"],
        "conseils_biosecurite": ["Surveillance régulière", "Hygiène du poulailler"],
        "traitement_propose": "Configurer l'IA pour des conseils réels",
        "recommande_veterinaire": True,
        "tokens": 0,
        "provider": "demo"
    }
