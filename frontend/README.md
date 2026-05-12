# Frontend — JobMatcher Web

Vue 3 + TypeScript + Pinia + TailwindCSS.

## Run locally

```bash
cp .env.example .env
npm install
npm run dev
```

App at http://localhost:5173.

## Build

```bash
npm run build      # outputs to ./dist
npm run preview    # serves dist locally
```

## Deploy to Vercel

```bash
npm i -g vercel
vercel --prod
```

Set `VITE_API_URL` in Vercel project settings to the Cloud Run backend URL.
