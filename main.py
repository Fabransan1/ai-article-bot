"""main.py — AI Article Bot (Google Gemini Pro)
──────────────────────────────────────────────
• Usa API gratuita do Gemini (Google AI Studio)
• Gera artigos e devolve em JSON
• Variável obrigatória: GEMINI_API_KEY
"""

import os
from fastapi import FastAPI, HTTPException
import google.generativeai as genai

# ─────────────────────────────────────────────────────────────
# Configurar chave do Gemini
# ─────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY não definida no Environment.")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-pro")

app = FastAPI(title="AI Article Bot – Gemini Pro")

# ─────────────────────────────────────────────────────────────
# Função para gerar artigo
# ─────────────────────────────────────────────────────────────

def generate_article(niche: str) -> dict:
    prompt = (
        f"Você é um redator profissional. Escreva um artigo de blog (~400 palavras) "
        f"sobre '{niche}' em português, com título H1 e subtítulos H2."  # noqa: E501
    )
    try:
        response = model.generate_content(prompt)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    content = response.text.strip()
    title = content.split("\n")[0].lstrip("# ").strip()
    return {"title": title, "content": content}

# ─────────────────────────────────────────────────────────────
# Rotas FastAPI
# ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "running", "provider": "gemini-pro"}

@app.get("/publish-now/")
async def publish_now(niche: str = "finanças"):
    article = generate_article(niche)
    return {"generated": True, "niche": niche, "article": article}
