# Providers and models

Read this reference when adding a provider, choosing a model for a modality,
or debugging a failed call. `config/models.json` is the live registry; the
script never hard-codes providers or models.

## Bundled providers (OpenAI-compatible chat endpoints)

| Provider | base_url | env_key | Example models | Notes |
|---|---|---|---|---|
| Alibaba DashScope | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `DASHSCOPE_API_KEY` | `qwen-vl-max`, `qwen3-vl-flash` | Reliable in CN networks; free quota available |
| OpenAI | `https://api.openai.com/v1` | `OPENAI_API_KEY` | `gpt-4o-mini`, `gpt-4o` | Standard OpenAI-compatible vision |
| Zhipu | `https://open.bigmodel.cn/api/paas/v4` | `ZHIPU_API_KEY` | `glm-4v-flash` | `glm-4v-flash` is free; key format `{id}.{secret}` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/openai` | `GOOGLE_API_KEY` | `gemini-2.0-flash` | Image, audio, and video via OpenAI-compatible parts |
| Agnes AI | `https://apihub.agnes-ai.com/v1` | `AGNES_API_KEY` | `agnes-2.5-flash`, `agnes-2.0-flash` | OpenAI-compatible; docs say public image URLs, base64 `data:` URIs verified working; 512K context |
| Ollama (local) | `http://localhost:11434/v1` | (none) | `llava` | No API key; runs fully local |

## Modality support

- **Image** - supported by every OpenAI-compatible vision model via
  `image_url` (URL or `data:` URI). Universal.
- **Audio / video** - only models that declare `image`, `audio`, or `video`
  in their `modalities` list can handle those inputs. The script sends them as
  `input_audio` / `input_video` data URIs and skips models that cannot handle
  the detected modality.
- If no configured model supports the input modality, `analyze` lists the
  models that do and exits with an error. Add or enable a matching model
  (for example `gemini-2.0-flash` for audio/video).

## Adding a new provider

Any OpenAI-compatible `/chat/completions` endpoint works:

```powershell
python scripts/mm_proxy.py models add --id my-vision --provider myprovider --model my-vl-model --base-url "https://api.example.com/v1" --env-key MYPROVIDER_API_KEY
```

Or edit `config/models.json` directly: add a `providers` entry (base_url +
env_key) and a `models` entry referencing it. A model may also override
`base_url` or `env_key` per entry for custom endpoints.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| HTTP 401/403 | Key missing or wrong in `config/secrets.env`, or provider account not enabled for the model. Run `check` to verify key presence. |
| HTTP 404 / "model not found" | The `model` name in the registry does not match the provider's model id. Check the provider console/docs. |
| HTTP 429 | Rate limit or quota. Add more models to the chain (`--models a,b,c`) so fallback kicks in. |
| "no model supports X" | No enabled model declares the input modality. `models enable --id gemini-2.0-flash` for audio/video. |
| Connection refused | Wrong `base_url` or (for Ollama) the local server is not running. |
| Proxy environment | `urllib` honors `HTTP_PROXY`/`HTTPS_PROXY` env vars automatically. |
