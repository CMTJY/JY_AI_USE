# SuperCowart Portable Package

Version: `0.1.21`

Marketplace: `supercowart-portable`

Plugin: `cowart`

Structure:

```text
SuperCowart-Codex-Plugin-0.1.21/
├── .agents/plugins/marketplace.json
├── INSTALL_PROMPT.txt
├── INSTALL_WITH_CODEX.md
├── PACKAGE_CONTENTS.md
└── plugins/supercowart/
    ├── .codex-plugin/plugin.json
    ├── .mcp.json
    ├── mcp/
    ├── public/
    ├── scripts/
    ├── skills/
    ├── src/
    ├── LICENSE
    ├── README.md
    ├── README.en.md
    ├── package.json
    ├── package-lock.json
    └── vite.config.js
```

`node_modules/`, production build caches, Git history, user data, and development logs are not shipped. They are recreated or stored outside the plugin package as appropriate.
