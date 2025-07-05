"""
main.py — AI Article Bot (OpenAI v1)
────────────────────────────────────
• Gera artigo via openai.chat.completions.create
• Não usa mais a classe OpenAI (que causava conflito)
"""

import os
from fastapi import FastAPI, HTTPException
import openai

# ─────────────────────────────────────────────────────────────
# Chave da OpenAI
# ─────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY não definida no Environment.")

openai.api_key = OPENAI_API_KEY

app = FastAPI(title="AI Article Bot – OpenAI v1")

# ─────────────────────────────────────────────────────────────
# Função para gerar artigo
# ─────────────────────────────────────────────────────────────
def generate_article(niche: str) -> dict:
    prompt = (
        f"Você é um redator profissional. Escreva um artigo de blog (~400 palavras) "
        f"em português sobre '{niche}'. Use título H1 e subtítulos."
    )
    try:
        resp = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    content = resp.choices[0].message.content.strip()
    title = content.split("\n")[0].lstrip("# ").strip()
    return {"title": title, "content": content}

# ─────────────────────────────────────────────────────────────
# Rotas FastAPI
# ─────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return {"status": "running", "openai_version": openai.__version__}

@app.get("/publish-now/")
async def publish_now(niche: str = "finanças"):
    article = generate_article(niche)
    return {"generated": True, "niche": niche, "article": article}
