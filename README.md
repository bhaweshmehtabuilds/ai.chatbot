# noteapp

Agentic AI chat demo: static frontend + Flask backend that calls OpenRouter with tool use (calculator, get time).

## Architecture

- **Frontend** — `index.html`, hosted on **Netlify**
- **Backend** — `python.py` (Flask), hosted on **Render**
- Netlify proxies `/api/*` to the Render service (see `netlify.toml`), so the browser stays same-origin and no CORS setup is needed.

## Local development

```bash
pip install -r requirements.txt

# Either export the key:
export OPENROUTER_API_KEY=sk-...

# Or keep using the local api.gitignore file (first line starting with sk-)

python3 python.py   # http://localhost:5000
```

## Production

### Backend (Render)

1. Push this repo to GitHub.
2. In Render: **New → Blueprint** and select the repo — `render.yaml` defines the service (`gunicorn python:app`).
3. Set the `OPENROUTER_API_KEY` env var in the Render dashboard (synced as `sync: false` in the blueprint).
4. Note the service URL, e.g. `https://noteapp-api.onrender.com`.

### Frontend (Netlify)

1. In Netlify: **Add new site → Import an existing project** and select the repo.
2. `netlify.toml` sets the publish directory and proxies `/api/*` to Render.
3. After your Render service is live, update the target URL in `netlify.toml` if it differs from `https://noteapp-api.onrender.com`, then redeploy.

## Notes

- Chat history (`HISTORY`) is in-memory on the server; it resets when the Render service restarts or sleeps (single-worker gunicorn keeps it consistent per instance).
- `api.gitignore` is gitignored — never commit your API key.
