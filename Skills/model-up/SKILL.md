---
name: model-up
description: >-
  Relay multimodal inputs (images, audio, video) to external multimodal models
  and return their analysis as text. Use when the current model is text-only or
  otherwise cannot process multimodal content: a user asks you to read/describe
  a local image, screenshot, URL, chart, diagram, or error dialog; pasted images
  are rejected or replaced with "[Unsupported Image]"; visible text needs OCR;
  or audio/video needs understanding. Model registry and provider endpoints live
  in config/models.json, API keys live in config/secrets.env, and the proxy
  calls OpenAI-compatible chat endpoints with automatic multi-model fallback.
---

# Model Up

Give a text-only model multimodal sight through configurable external models.

## Quick start

```powershell
python scripts/mm_proxy.py analyze "C:\path\to\screenshot.png"
python scripts/mm_proxy.py analyze "C:\path\to\error.png" --mode ui
python scripts/mm_proxy.py analyze "C:\path\to\scan.png" --mode ocr
python scripts/mm_proxy.py analyze "https://example.com/chart.png" --prompt "Summarize this chart"
```

## Workflow

1. Identify the input: a local file path, an http(s) URL, or a `data:` URI.
2. Pick models: omit `--models` to use the configured default chain, or pass a
   comma-separated fallback chain, e.g. `--models qwen-vl-max,glm-4v-flash`.
3. Run `analyze`. On API errors the script automatically tries the next model
   in the chain and reports which model succeeded.
4. Return the resulting text to the user. Be explicit that the analysis came
   from the configured multimodal model; never claim you saw the input yourself.

For long results, add `--save result.md` and then read the file. Use `--json`
for the raw API response and `--dry-run` to preview the exact request that
would be sent (no network call).

## Local images

Local files and `data:` URIs are sent inline as base64 - no image host, no
upload, and nothing leaves the machine beyond the model API call itself.
All bundled image models accept this, including `agnes-2.5-flash` and
`agnes-2.0-flash` (verified by direct testing).

```powershell
python scripts\mm_proxy.py analyze "C:\path\to\screenshot.png" --models agnes-2.5-flash
```

## Choosing and managing models

Everything configurable lives in `config/`; the script contains no model or
provider details. `config/models.json` holds the registry, providers
(base URLs), and the `default_chain`. Manage it with:

```powershell
python scripts/mm_proxy.py models list
python scripts/mm_proxy.py models add --id my-vision --provider openai --model gpt-4o-mini --modalities image
python scripts/mm_proxy.py models remove --id my-vision
python scripts/mm_proxy.py models enable --id gemini-2.0-flash
python scripts/mm_proxy.py models disable --id glm-4v-flash
python scripts/mm_proxy.py models set-default --ids qwen-vl-max,gpt-4o-mini
```

To add a new OpenAI-compatible provider that is not in the registry, use
`models add` with `--base-url` and `--env-key`, or edit `config/models.json`
directly. See [providers.md](references/providers.md) for supported providers,
modality limits, and troubleshooting.

## API keys (secrets)

Keys live only in `config/secrets.env` (one `KEY=VALUE` per line):

- Load a key: uncomment or add its line.
- Unload a key: comment it out or delete the line.
- Reset: delete the file; the script recreates the template on next run.
- OS environment variables with the same name override the file.

Never print, log, or paste API keys into the conversation. The script masks key
presence in `check` output and never includes keys in printed requests.

## Diagnostics

```powershell
python scripts/mm_proxy.py check
```

`check` verifies the config, lists models, and reports which providers have
keys set. `--config-dir` (or the `MODEL_UP_CONFIG_DIR` env var) switches to a
different config location, useful for keeping separate key sets per project.

## Resources

- `scripts/mm_proxy.py` - the CLI (analyze / models / check), stdlib-only Python.
- `config/models.json` - model registry and providers, no secrets.
- `config/secrets.env` - API keys, loaded and unloaded by editing lines.
- `references/providers.md` - provider table, adding providers, modality notes,
  troubleshooting. Read it when adding a provider or debugging a failure.
