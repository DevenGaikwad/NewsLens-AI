# Deployment values to fill after approval

Do not add credentials, tokens, recovery codes, private keys, or passwords to
this file. Replace only the public identifiers below immediately before the
approved publication/deployment phase.

| Value | Required public value | Where it is applied |
|---|---|---|
| `GITHUB_USERNAME` | `DevenGaikwad` — authenticated through the connected GitHub application on 24 August 2026 | `.github/CODEOWNERS`, canonical repository ownership |
| Intended repository URL | `https://github.com/DevenGaikwad/NewsLens-AI` — **not created or live** | Create the empty public repository, then verify before adding it to `CITATION.cff` or presenting it as canonical |
| Public Streamlit URL | `[STREAMLIT_URL — TO BE PROVIDED]` | README and Vercel `NEXT_PUBLIC_STREAMLIT_APP_URL` |
| Public Vercel URL | `[VERCEL_URL — TO BE PROVIDED]` | README and deployment record |
| Optional security contact | `[OPTIONAL_SECURITY_CONTACT — TO BE PROVIDED]` | `SECURITY.md` only if the owner intentionally publishes it |

The GitHub identity is resolved, but the intended repository does not yet
exist. Current source files use non-live sentinel URLs only where needed to make
a build deterministic. The release scanner treats the remaining unresolved
values as publication gates. Do not present the intended repository or hosting
URLs as live links until each target is created and verified.
