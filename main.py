import os
import datetime
from typing import Tuple

import requests
from fastapi import FastAPI, BackgroundTasks, HTTPException
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
from openai import OpenAI

# ─────────────────────────────────────────────────────────────
# Carrega variáveis do .env ou do ambiente do Render
# ─────────────────────────────────────────────────────────────
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WP_ACCESS_TOKEN = os.getenv("WP_ACCESS_TOKEN")
WP_BLOG_ID = os.getenv("WP_BLOG_ID")  # ex.: "246150668"
WP_URL = os.getenv("WP_URL", "https://rumoariqueza29.wordpress.com")
POST_INTERVAL_HOURS = int(os.getenv("POST_INTERVAL_HOURS", 24))
DEFAULT_NICHE = os.getenv("DEFAULT_NICHE", "finanças")

if not all([OPENAI_API_KEY, WP_ACCESS_TOKEN, WP_BLOG_ID]):
    raise RuntimeError("Faltam variáveis de ambiente obrigatórias. Confira OPENAI_API_KEY, WP_ACCESS_TOKEN e WP_BLOG_ID.")

# Cliente OpenAI (versão 1.x da biblioteca)
client = OpenAI(api_key=OPENAI_API_KEY)

# ─────────────────────────────────────────────────────────────
# Funções utilitárias
# ─────────────────────────────────────────────────────────────

def generate_article(niche: str) -> Tuple[str, str]:
    """Gera um artigo ~600 palavras em Markdown sobre o nicho desejado"""
    prompt = (
        "Você é um redator profissional. Escreva um artigo de blog em português com cerca de 600 palavras sobre o tema: "
        f"\"{niche}\". Use título cativante (H1), subtítulos (H2/H3) e conclua com um call‑to‑action."
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=900,
    )
    content = response.choices[0].message.content.strip()
    # Primeiro heading vira título
    title = content.split("\n")[0].lstrip("# ").strip()
    return title, content


def publish_to_wordpress(title: str, content: str) -> str:
    """Publica o artigo via REST na conta WordPress.com"""
    url = f"https://public-api.wordpress.com/rest/v1.1/sites/{WP_BLOG_ID}/posts/new"
    headers = {"Authorization": f"Bearer {WP_ACCESS_TOKEN}"}
    data = {"title": title, "content": content, "status": "publish"}
    r = requests.post(url, headers=headers, data=data, timeout=30)
    if r.status_code != 201:
        raise HTTPException(status_code=500, detail=f"Falha ao publicar: {r.text}")
    post_id = r.json().get("ID")
    return f"{WP_URL}/?p={post_id}"


def job(niche: str = DEFAULT_NICHE):
    """Gera e publica imediatamente"""
    try:
        title, content = generate_article(niche)
        link = publish_to_wordpress(title, content)
        print(f"[{datetime.datetime.now()}] Publicado: {title} → {link}")
    except Exception as e:
        print("Erro no job:", e)

# ─────────────────────────────────────────────────────────────
# FastAPI + Scheduler
# ─────────────────────────────────────────────────────────────
app = FastAPI(title="AI Article Bot")

scheduler = BackgroundScheduler()
scheduler.add_job(job, "interval", hours=POST_INTERVAL_HOURS)
scheduler.start()

@app.get("/")
async def root():
    return {"status": "running"}

# POST (para ferramentas ou hooks)
@app.post("/publish-now/")
async def publish_now_post(niche: str = DEFAULT_NICHE, background_tasks: BackgroundTasks | None = None):
    if background_tasks:
        background_tasks.add_task(job, niche)
    else:
        job(niche)
    return {"queued": True, "niche": niche}

# GET (para acionar via navegador)
@app.get("/publish-now/")
async def publish_now_get(niche: str = DEFAULT_NICHE):
    job(niche)
    return {"published": True, "niche": niche}

# ─────────────────────────────────────────────────────────────
# Fim do arquivo
# ─────────────────────────────────────────────────────────────
