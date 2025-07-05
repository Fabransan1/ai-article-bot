import os, datetime, requests, openai
from fastapi import FastAPI, BackgroundTasks
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WP_ACCESS_TOKEN = os.getenv("WP_ACCESS_TOKEN")
WP_BLOG_ID = os.getenv("WP_BLOG_ID")
WP_URL = os.getenv("WP_URL")
POST_INTERVAL_HOURS = int(os.getenv("POST_INTERVAL_HOURS", 24))

openai.api_key = OPENAI_API_KEY

app = FastAPI(title="AI Article Bot")

def generate_article(niche: str) -> tuple[str, str]:
    prompt = f"Write a 600-word blog article in Portuguese about {niche}. Include engaging headings and a short conclusion. Return only plain markdown content."
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role":"user","content":prompt}],
        max_tokens=900,
        temperature=0.7,
    )
    content = resp.choices[0].message.content.strip()
    title = content.split("\n")[0].strip("# ").strip()
    return title, content

def publish_to_wordpress(title: str, content: str):
    url = f"https://public-api.wordpress.com/rest/v1.1/sites/{WP_BLOG_ID}/posts/new"
    headers = {"Authorization": f"Bearer {WP_ACCESS_TOKEN}"}
    data = {"title": title, "content": content, "status": "publish"}
    r = requests.post(url, headers=headers, data=data, timeout=30)
    r.raise_for_status()
    return r.json()
# ────────────────────────────────────────────────
# Permite chamar a publicação via GET no navegador
@app.get("/publish-now/")
def publish_now_get(niche: str = "finanças"):
    title, content = generate_article(niche)
    publish_to_wordpress(title, content)
    return {"published": True, "niche": niche}
# ────────────────────────────────────────────────

def job(niche: str="finanças"):
    try:
        title, content = generate_article(niche)
        publish_to_wordpress(title, content)
        print(f"[{datetime.datetime.now()}] Published: {title}")
    except Exception as e:
        print("Error in job:", e)

scheduler = BackgroundScheduler()
scheduler.add_job(job, "interval", hours=POST_INTERVAL_HOURS)
scheduler.start()

@app.get("/")
def root():
    return {"status":"running"}

@app.post("/publish-now/")
def publish_now(niche: str="finanças", background_tasks: BackgroundTasks = None):
    if background_tasks:
        background_tasks.add_task(job, niche)
    else:
        job(niche)
    return {"queued": True, "niche": niche}
