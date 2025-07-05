"""main.py — Etapa 2: Geração de artigo com OpenAI (ainda sem publicar)
────────────────────────────────────────────────────────────────
• Mantém API simples, mas já gera artigo via ChatGPT.
• Requer somente a variável OPENAI_API_KEY.
• Rota GET /publish-now/?niche= devolve título + corpo do artigo em JSON.
"""

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from openai import OpenAI
import os

# ─────────────────────────────────────────────────────────────
# Carregar chave da OpenAI
# ─────────────────────────────────────────────────────────────
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("Falta definir OPENAI_API_KEY nas variáveis de ambiente.")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(title="AI Article Bot – etapa 2")

# ─────────────────────────────────────────────────────────────
# Função geradora de artigo
# ─────────────────────────────────────────────────────────────

def generate_article(niche: str) -> dict:
    prompt = (
        "Você é um redator profissional. Escreva um artigo de blog em português, com ~400 palavras, "
        f"sobre {niche}. Use título em H1 e alguns subtítulos. Forneça apenas Markdown."
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=600,
            temperature=0.7,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

    content = resp.choices[0].message.content.strip()
    title = content.split("\n")[0].lstrip("# ").strip()
    return {"title": title, "content": content}

# ─────────────────────────────────────────────────────────────
# Rotas
# ─────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "running", "stage": 2}

@app.get("/publish-now/")
async def publish_now(niche: str = "finanças"):
    """Gera o artigo e retorna JSON (ainda não publica no WordPress)."""
    article = generate_article(niche)
    return {"generated": True, "niche": niche, "article": article}
