# Wisdom AI Web

This is the Next.js frontend for Wisdom AI.

## What it is

- Next.js App Router app
- TypeScript + Tailwind
- light/dark theme support
- PWA support
- routes for chat, daily verse, saved verses, profile, and admin pages

## Run it locally

```bash
pnpm i
pnpm dev
```

If you prefer npm or yarn, that works too.

## Backend connection

The frontend talks to the FastAPI backend through `/api/*` route handlers.

By default, it expects:

```text
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Main pages

- `/login`
- `/signup`
- `/daily-verse`
- `/saved`
- `/chat`
- `/profile`
- `/admin`

## Auth

Auth is still lightweight. The current flow uses mock cookies set by the Next.js route handlers, which is fine for local development but not enough for production.

## PWA

- manifest: `public/manifest.json`
- service worker: `next-pwa`

## Good to know

- The UI is styled to feel like a real product.
- Some backend features are still mock or seeded data.
- The frontend is best understood together with the FastAPI backend in the repo root.
