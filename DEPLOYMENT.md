## Deploying Wisdom AI

This guide walks you through two supported deployment paths:

- Simple split deploy: Frontend on Vercel, Backend on a PaaS (Railway/Render/Fly/Azure)
- All‑in‑one Docker: Caddy (TLS) + Next.js + FastAPI + Postgres on a single server

---

### Option A — Vercel (frontend) + PaaS (backend)

1) Deploy backend (FastAPI)
- Choose a PaaS (Railway, Render, Fly.io, Azure App Service, etc.)
- Build command (if needed): `uvicorn main:app --host 0.0.0.0 --port 8000`
- Env vars:
  - `DATABASE_URL` → managed Postgres URL from the provider
  - `JWT_SECRET` → long random string
  - `MEDIA_ROOT` → `./media` (or a mounted volume if supported)
- Expose port 8000 and note the public base URL (e.g., `https://api.example.com`)

2) Deploy frontend (Next.js) on Vercel
- Import `web/` as the project root
- Build command: `npm run build` (default)
- Output: Next.js app (Node runtime)
- Env vars in Vercel:
  - `NEXT_PUBLIC_SITE_URL` → your site domain (e.g., `https://wisdom.example.com`)
  - `NEXT_PUBLIC_API_BASE_URL` → your FastAPI URL (e.g., `https://api.example.com`)

3) CORS + Cookies
- FastAPI already allows `allow_origins=["*"]` in dev. For production, consider restricting this to your frontend domain.
- Auth cookies are set by Next route handlers; since the browser calls the Next server, you avoid cross‑site cookie issues.

4) Media hosting
- FastAPI serves `/media/*` (images/audio). The Next server rewrites `/media/*` to the backend based on `NEXT_PUBLIC_API_BASE_URL`.

---

### Option B — Single server with Docker Compose (production)

This repo includes `docker-compose.prod.yml` and a `web/Dockerfile` to run the full stack behind Caddy with automatic TLS.

1) DNS
- Create a DNS A record for your domain (e.g., `wisdom.example.com`) pointing to your server’s IP.

2) Prepare environment
```
export DOMAIN=wisdom.example.com
export JWT_SECRET="change_me_to_a_long_random_string"
```

3) Bring up the stack
```
docker compose -f docker-compose.prod.yml up -d --build
```

Services:
- `proxy` (Caddy): terminates TLS for `${DOMAIN}` and proxies to `web:3000`
- `web` (Next.js): runs `next start` and forwards API calls/media to `app` using internal URL
- `app` (FastAPI): serves API and `/media/*`
- `db` (Postgres): persistent storage

4) Configuration wiring
- `web` service uses env vars:
  - `NEXT_PUBLIC_SITE_URL=https://${DOMAIN}` (used by metadata/PWA)
  - `NEXT_PUBLIC_API_BASE_URL=http://app:8000` (internal service name for backend)
- `app` service uses:
  - `DATABASE_URL=postgresql://godai:godai_password@db:5432/godai_db`
  - `JWT_SECRET` (from your env)
  - `MEDIA_ROOT=/app/media` (mounted volume)

5) Logs and status
```
docker compose -f docker-compose.prod.yml logs -f proxy web app
```

6) Updating
```
git pull
docker compose -f docker-compose.prod.yml up -d --build
```

---

### Health checks
- Frontend: `https://$DOMAIN/` should load the landing page
- Backend via proxy route: `https://$DOMAIN/api/health` (Next route handler forwards to FastAPI)
- Direct backend (internal): not exposed to the internet; use `docker compose exec app curl -s http://localhost:8000/health`

### Common pitfalls
- PWA caching: hard refresh or incognito if UI changes don’t show up
- Wrong API base: ensure `NEXT_PUBLIC_API_BASE_URL` points to the backend (`app` inside Compose, or public FastAPI URL on PaaS)
- Cookies: use the site domain (no mismatched subdomains) so auth cookie works across protected pages

### Security notes
- Rotate `JWT_SECRET` for production and store it securely
- Restrict CORS to your domain in `main.py` when you’re not using the Next proxy
- Use strong DB credentials; consider a managed Postgres for reliability
