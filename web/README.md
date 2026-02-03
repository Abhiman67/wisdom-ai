# Wisdom AI Web

Modern PWA frontend for Wisdom AI (FastAPI backend).

## Stack
- Next.js (App Router) + TypeScript
- Tailwind CSS + CSS variables (violet accent) + dark/light via `next-themes`
- React Query for server state
- Zod + React Hook Form for forms
- next-pwa for PWA

## Dev
- Install deps and run the dev server:

```bash
pnpm i # or npm i / yarn
pnpm dev
```

The dev server proxies `/api/*` to your backend at `http://localhost:8000` (configurable via `NEXT_PUBLIC_API_BASE_URL`).

## Env
- Create `.env.local` in `web/` if needed:

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Pages
- `/login`, `/signup`
- `/daily-verse` (primary)
- `/saved`
- `/chat`
- `/profile`
- `/admin`

## Auth
Client stores JWT in `localStorage` (simple mode). For production hardening, move to httpOnly cookies via Next Route Handlers.

## PWA
- Manifest at `public/manifest.json`
- Service worker via `next-pwa`

