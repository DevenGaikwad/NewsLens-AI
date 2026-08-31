# NewsLens AI presentation website

This directory is a lightweight Next.js presentation shell for Vercel. The functional application remains the Streamlit/Python product at the repository root.

```bash
cp .env.example .env.local
npm install
npm run dev
```

Set `NEXT_PUBLIC_STREAMLIT_APP_URL` to the public Streamlit Community Cloud URL without `?embed=true`; the `/app` route adds the supported embed parameter. This is the only browser-exposed environment variable. Configure Vercel with `web/` as the project root.

The value must be an HTTPS `*.streamlit.app` origin with no credentials, port, path, query, or fragment. Production responses include a restrictive Content Security Policy and standard browser security headers. The iframe is sandboxed while preserving the Streamlit functionality required for scripts, forms, downloads, and clearly useful external links.

NewsLens AI · Designed and developed by Deven Sachin Gaikwad  
© 2026 Deven Sachin Gaikwad. All Rights Reserved.
