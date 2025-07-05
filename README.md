# AI Article Bot

Bot em Python que gera artigos com IA (OpenAI) e publica automaticamente em blog WordPress.

## Como funciona
1. **Gera artigo** com ChatGPT a partir de um nicho (ex.: pets, finanças).
2. **Publica** no seu blog WordPress via API REST / XML‑RPC.
3. Agenda uma postagem automática por dia (ajustável).

## Deploy rápido no Render
1. Faça fork ou clone deste repositório.
2. Defina estas variáveis de ambiente no Render (Settings ▸ Environment):
   - `OPENAI_API_KEY`
   - `WP_ACCESS_TOKEN`
   - `WP_BLOG_ID`
   - `WP_URL`
3. Clique em **Deploy to Render** (ou use o botão abaixo).

## Rotas
- `GET /` → Status online.
- `POST /publish-now/?niche=finance` → Gera e publica imediatamente.

## Ajustar frequência
Edite a variável `POST_INTERVAL_HOURS` em `main.py`.

---

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)
