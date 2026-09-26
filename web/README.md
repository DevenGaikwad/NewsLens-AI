# NewsLens AI presentation website

This directory is a reference Next.js presentation source. The deployed functional application is the Streamlit/Python product at the repository root; no Vercel deployment is required for Phase 5S.

```bash
cp .env.example .env.local
npm install
npm run dev
```

For an optional local presentation preview, set `NEXT_PUBLIC_STREAMLIT_APP_URL` to the public Streamlit Community Cloud URL without `?embed=true`; the `/app` route adds the supported embed parameter. This is the only browser-exposed environment variable.

The value must be an HTTPS `*.streamlit.app` origin with no credentials, port, path, query, or fragment. Production responses include a restrictive Content Security Policy and standard browser security headers. The iframe is sandboxed while preserving the Streamlit functionality required for scripts, forms, downloads, and clearly useful external links.

NewsLens AI · Designed and developed by Deven Sachin Gaikwad  
© 2026 Deven Sachin Gaikwad. All Rights Reserved.
