# 🚀 Deploying to Vercel

The `web` folder contains a Next.js application ready for Vercel.

## ⚡ Setup Architecture
- **Framework**: Next.js 14 (App Router)
- **AI Provider**: Google Gemini 1.5 Flash (Free Tier)
- **Data**: Embedded directly in the app (No external database needed!)

## 🛠️ Deployment Steps

1.  **Go to Vercel Dashboard**: [vercel.com/new](https://vercel.com/new)
2.  **Import Project**:
    - Select the root repository.
    - **IMPORTANT**: Change the **Root Directory** to `web`. (Click "Edit" next to Root Directory).
3.  **Environment Variables**:
    - Add `GEMINI_API_KEY`: Get one from [aistudio.google.com](https://aistudio.google.com) (Free).
4.  **Deploy**: Click "Deploy".

## 🧪 Local Testing
1.  Navigate to web folder: `cd web`
2.  Install dependencies: `npm install`
3.  Set key: `export GEMINI_API_KEY="your-key"`
4.  Run: `npm run dev`
5.  Open: `http://localhost:3000`

That's it! Your site will be up in < 1 minute.
