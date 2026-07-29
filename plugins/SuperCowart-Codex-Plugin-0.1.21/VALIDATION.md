# Validation Record

Package version: `0.1.21`

Validation date: `2026-07-29`

The portable package was tested from a clean dependency installation:

```bash
npm ci
npm audit --json
npm run quality
```

Results:

- Codex plugin manifest validation: passed.
- JSON manifest and lockfile parsing: passed.
- npm security audit: 0 known vulnerabilities.
- JavaScript syntax checks: passed.
- Vite 8.1.5 production build: passed.
- SuperCowart MCP end-to-end probe: passed.
- Native widget resource and CSP checks: passed.
- Native flowchart shape creation: passed.
- AI Slides frame creation: passed.
- HTML page insertion into an AI-created Slides frame: passed.
- Final privacy scan: performed after generated caches were removed.

The production build reports a large single-chunk informational warning. SuperCowart intentionally produces a single inlined widget payload so the native Codex widget can satisfy its CSP and avoid remote runtime assets.
