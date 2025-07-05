"""main.py — Compatível com OpenAI versão antiga (API Key via .api_key)
────────────────────────────────────────────────────────────
• Corrige erro: Client.__init__() got unexpected keyword argument 'api_key'
• Usa método tradicional openai.api_key = "..."
"""

from fastapi import FastAPI, HTTPException
import openai
import os

app = FastAPI(title="AI Article Bot – Compatível")

# ─────────────────────────────────────────────────────────────
# Carregar chave da OpenAI
# ─────────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Falta definir OPENAI_API_KEY nas variáveis de ambiente.")
openai.api_key = OPENAI_API_KEY

# ─────────────────────────────────────────────────────────────
# Função para gerar artigo
# ─────────────────────────────────────────────────────────────

def generate_article(niche: str) -> dict:
    prompt = (
        f"Você é um redator profissional. Escreva um artigo de blog (~400 palavras) sobre '{niche}', com título H1 e subtítulos. Use markdown."
    )
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    content = response.choices[0].message.content.strip()
    title = content.split("\n")[0].lstrip("# ").strip()
    return {"title": title, "content": content}

# ─────────────────────────────────────────────────────────────
# Rotas
# ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "ok", "stage": "OpenAI funcionando"}

@app.get("/publish-now/")
async def publish_now(niche: str = "finanças"):
    article = generate_article(niche)
    return {"niche": niche, "generated": True, "article": article}
