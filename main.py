"""main.py — versão mínima para garantir deploy
-------------------------------------------------
• Apenas verifica se a aplicação sobe no Render.
• Oferece dois endpoints simples: root / e /publish-now/?niche=.
• Ainda NÃO publica em WordPress nem chama OpenAI (adicionaremos depois que o deploy estiver estável).
"""

from fastapi import FastAPI

app = FastAPI(title="AI Article Bot (Versão Mínima)")

@app.get("/")
async def root():
    """Endpoint de status: retorna se a API está online."""
    return {"status": "running", "message": "Versão mínima funcionando!"}

@app.get("/publish-now/")
async def publish_now(niche: str = "finanças"):
    """Endpoint de teste: simplesmente confirma que recebeu o pedido."""
    return {"published": False, "niche": niche, "info": "Versão mínima — geração de artigo ainda não habilitada."}
