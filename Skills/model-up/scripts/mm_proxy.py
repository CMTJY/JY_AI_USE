#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""model-up: multimodal proxy for text-only LLMs.

Commands:
  analyze <input>  Send image/audio/video to configured multimodal models
                   and print their analysis as text. On API errors, tries the
                   next model in the chain automatically.
  models           Manage the model registry (list/add/remove/enable/disable/
                   set-default).
  check            Validate config and report API key presence.

Configuration lives outside this script (default: <skill>/config/):
  models.json   Model registry + providers (no secrets)
  secrets.env   API keys, one KEY=VALUE per line

Override the config location with --config-dir or MODEL_UP_CONFIG_DIR.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_DIR = SKILL_DIR / "config"

MODES = {
    "general": (
        "Describe this input in detail. Include visible text, layout, objects, "
        "colors, and anything a reader must know."
    ),
    "ocr": (
        "Transcribe ALL visible text exactly as written, preserving line breaks "
        "and reading order. Output only the transcription."
    ),
    "ui": (
        "Analyze this UI screenshot: describe the layout, elements, and states, "
        "and highlight any error messages, dialogs, or warnings."
    ),
    "diagram": (
        "Describe this diagram or figure: structure, components, relationships, "
        "labels, and flow."
    ),
}

DEFAULT_MODELS = {
    "default_chain": ["qwen-vl-max", "gpt-4o-mini"],
    "default_generator": "agnes-image-2.0-flash",
    "providers": {
        "dashscope": {
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "env_key": "DASHSCOPE_API_KEY",
        },
        "openai": {
            "base_url": "https://api.openai.com/v1",
            "env_key": "OPENAI_API_KEY",
        },
        "zhipu": {
            "base_url": "https://open.bigmodel.cn/api/paas/v4",
            "env_key": "ZHIPU_API_KEY",
        },
        "google": {
            "base_url": "https://generativelanguage.googleapis.com/v1beta/openai",
            "env_key": "GOOGLE_API_KEY",
        },
        "agnes": {
            "base_url": "https://apihub.agnes-ai.com/v1",
            "env_key": "AGNES_API_KEY",
        },
        "ollama": {"base_url": "http://localhost:11434/v1", "env_key": ""},
    },
    "models": {
        "qwen-vl-max": {
            "provider": "dashscope",
            "model": "qwen-vl-max",
            "modalities": ["image"],
            "enabled": True,
        },
        "qwen3-vl-flash": {
            "provider": "dashscope",
            "model": "qwen3-vl-flash",
            "modalities": ["image"],
            "enabled": True,
        },
        "gpt-4o-mini": {
            "provider": "openai",
            "model": "gpt-4o-mini",
            "modalities": ["image"],
            "enabled": True,
        },
        "glm-4v-flash": {
            "provider": "zhipu",
            "model": "glm-4v-flash",
            "modalities": ["image"],
            "enabled": True,
        },
        "gemini-2.0-flash": {
            "provider": "google",
            "model": "gemini-2.0-flash",
            "modalities": ["image", "audio", "video"],
            "enabled": False,
        },
        "agnes-2.5-flash": {
            "provider": "agnes",
            "model": "agnes-2.5-flash",
            "modalities": ["image"],
            "enabled": True,
        },
        "agnes-2.0-flash": {
            "provider": "agnes",
            "model": "agnes-2.0-flash",
            "modalities": ["image"],
            "enabled": True,
        },
        "agnes-image-2.0-flash": {
            "provider": "agnes",
            "model": "agnes-image-2.0-flash",
            "generation": True,
            "enabled": True,
            "sizes": ["1024x1024", "1024x768", "768x1024"],
        },
        "llava": {
            "provider": "ollama",
            "model": "llava",
            "modalities": ["image"],
            "enabled": False,
        },
    },
}

SECRETS_TEMPLATE = """\
# model-up API keys
# One KEY=VALUE per line. Add/uncomment a line to load a key; comment it out or delete it to unload.
# Values must match the env_key referenced in config/models.json.
# OS environment variables with the same name override these values.
DASHSCOPE_API_KEY=
OPENAI_API_KEY=
ZHIPU_API_KEY=
GOOGLE_API_KEY=
AGNES_API_KEY=
"""

EXTRA_MIME = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
    ".bmp": "image/bmp",
    ".svg": "image/svg+xml",
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".m4a": "audio/mp4",
    ".aac": "audio/aac",
    ".flac": "audio/flac",
    ".opus": "audio/opus",
    ".mp4": "video/mp4",
    ".webm": "video/webm",
    ".mov": "video/quicktime",
    ".mpeg": "video/mpeg",
}

FORMAT_BY_MIME = {
    "audio/wav": "wav",
    "audio/mpeg": "mp3",
    "audio/mp4": "m4a",
    "audio/aac": "aac",
    "audio/flac": "flac",
    "audio/opus": "opus",
    "video/mp4": "mp4",
    "video/webm": "webm",
    "video/quicktime": "mov",
    "video/mpeg": "mpeg",
}

class ModelUpError(Exception):
    """Expected failure with a user-facing message."""


class ApiError(Exception):
    def __init__(self, status, detail, model_id=None):
        self.status = status
        self.detail = detail
        self.model_id = model_id
        super().__init__(f"HTTP {status}: {detail}")


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


# ---------------------------------------------------------------- config I/O


def load_config(cfg_dir):
    path = Path(cfg_dir) / "models.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        save_json(path, DEFAULT_MODELS)
        eprint(f"[model-up] Created default config: {path}")
    with open(path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    if "models" not in cfg or "providers" not in cfg:
        raise ModelUpError(f"Invalid config {path}: missing 'models' or 'providers'")
    return cfg


def load_secrets(cfg_dir):
    secrets = {}
    path = Path(cfg_dir) / "secrets.env"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(SECRETS_TEMPLATE, encoding="utf-8")
        eprint(f"[model-up] Created secrets template: {path}")
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        secrets[key.strip()] = value.strip().strip("\"'")
    return secrets


def save_json(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def config_dir_from(args):
    if args.config_dir:
        return Path(args.config_dir)
    env_dir = os.environ.get("MODEL_UP_CONFIG_DIR")
    return Path(env_dir) if env_dir else DEFAULT_CONFIG_DIR


def api_key_for(model_def, provider_def, secrets):
    env_name = model_def.get("env_key") or provider_def.get("env_key", "")
    if not env_name:
        return None  # provider requires no auth (e.g. local Ollama)
    if os.environ.get(env_name):
        return os.environ[env_name]
    return secrets.get(env_name) or None


def base_url_for(model_def, provider_def, args):
    if getattr(args, "base_url", None):
        return args.base_url
    return model_def.get("base_url") or provider_def.get("base_url", "")


def resolve_chain(ids, cfg):
    registry = cfg["models"]
    chain = []
    for mid in ids:
        if mid not in registry:
            raise ModelUpError(
                f"Unknown model id '{mid}'. Run 'models list' to see available ids."
            )
        entry = registry[mid]
        if not entry.get("enabled", True):
            eprint(f"[model-up] Skipping disabled model '{mid}'.")
            continue
        chain.append((mid, entry))
    if not chain:
        raise ModelUpError("The model chain is empty (all models disabled or unknown).")
    return chain


# ---------------------------------------------------------------- payloads


def detect_input(input_ref):
    """Return (mime, modality, ref) where ref is a URL or data: URI."""
    if input_ref.startswith("data:"):
        mime = input_ref[5:].split(";", 1)[0] or "application/octet-stream"
        return mime, mime.split("/", 1)[0], input_ref
    if input_ref.startswith(("http://", "https://")):
        mime = mimetypes.guess_type(input_ref.split("?")[0])[0] or "application/octet-stream"
        return mime, mime.split("/", 1)[0], input_ref
    path = Path(input_ref)
    if not path.is_file():
        raise ModelUpError(f"Input not found: {input_ref}")
    suffix = path.suffix.lower()
    mime = mimetypes.guess_type(str(path))[0] or EXTRA_MIME.get(suffix, "application/octet-stream")
    if mime == "application/octet-stream":
        raise ModelUpError(
            f"Cannot detect type of {input_ref}. Use a known extension or pass a data: URI."
        )
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return mime, mime.split("/", 1)[0], f"data:{mime};base64,{data}"


def content_part(mime, modality, ref, timeout):
    if modality == "image":
        return {"type": "image_url", "image_url": {"url": ref}}
    # Audio/video: providers expect inline base64 data; download URLs first.
    if ref.startswith("data:"):
        data = ref.split(",", 1)[1]
    else:
        with urllib.request.urlopen(ref, timeout=timeout) as resp:
            data = base64.b64encode(resp.read()).decode("ascii")
    fmt = FORMAT_BY_MIME.get(mime, mime.split("/", 1)[1])
    if modality == "audio":
        return {"type": "input_audio", "input_audio": {"data": data, "format": fmt}}
    return {"type": "input_video", "input_video": {"data": data, "format": fmt}}


def build_payload(input_ref, prompt, max_tokens, temperature, timeout):
    mime, modality, ref = detect_input(input_ref)
    return {
        "model": None,  # filled per model at request time
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    content_part(mime, modality, ref, timeout),
                ],
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }, modality


# ---------------------------------------------------------------- transport


def post_chat(base_url, api_key, payload, timeout):
    url = base_url.rstrip("/") + "/chat/completions"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")
        raise ApiError(exc.code, detail[:500]) from exc
    except urllib.error.URLError as exc:
        raise ApiError(0, str(exc.reason)) from exc
    except TimeoutError as exc:
        raise ApiError(0, "request timed out") from exc


def extract_content(resp):
    try:
        return resp["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return json.dumps(resp, ensure_ascii=False)


# ---------------------------------------------------------------- commands


def cmd_analyze(args):
    cfg_dir = config_dir_from(args)
    cfg = load_config(cfg_dir)
    secrets = load_secrets(cfg_dir)
    chain_ids = args.models.split(",") if args.models else cfg.get("default_chain", [])
    chain = resolve_chain(chain_ids, cfg)
    prompt = args.prompt or MODES.get(args.mode, MODES["general"])

    mime, modality, _ = detect_input(args.input_ref)
    compatible = [(mid, entry) for mid, entry in chain if modality in entry.get("modalities", ["image"])]
    skipped = [(mid, entry) for mid, entry in chain if mid not in [m for m, _ in compatible]]
    for mid, _entry in skipped:
        eprint(f"[model-up] Skipping '{mid}': no {modality} support.")
    if not compatible:
        options = [mid for mid, entry in cfg["models"].items() if modality in entry.get("modalities", [])]
        raise ModelUpError(
            f"No model in the chain supports '{modality}'. Available: "
            + (", ".join(options) if options else "none configured")
        )

    payload, _ = build_payload(args.input_ref, prompt, args.max_tokens, args.temperature, args.timeout)

    if args.dry_run:
        print(f"# dry-run: chain = {', '.join(mid for mid, _ in chain)}")
        for mid, entry in compatible:
            provider = cfg["providers"][entry["provider"]]
            print(f"#   -> {mid} @ {base_url_for(entry, provider, args)} (model={entry['model']})")
        payload["model"] = compatible[0][0]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    last_error = None
    for mid, entry in compatible:
        provider = cfg["providers"][entry["provider"]]
        api_key = api_key_for(entry, provider, secrets)
        if api_key is None and provider.get("env_key"):
            raise ModelUpError(
                f"API key missing for provider '{entry['provider']}'. "
                f"Add {provider['env_key']}=<key> to {cfg_dir / 'secrets.env'}."
            )
        payload["model"] = entry["model"]
        try:
            resp = post_chat(base_url_for(entry, provider, args), api_key, payload, args.timeout)
        except ApiError as exc:
            exc.model_id = mid
            last_error = exc
            eprint(f"[model-up] {mid} failed: HTTP {exc.status} - {exc.detail}")
            continue
        content = extract_content(resp)
        if args.verbose:
            eprint(f"[model-up] Succeeded with model: {mid}")
        if args.save:
            out = Path(args.save)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(content + "\n", encoding="utf-8")
            eprint(f"[model-up] Saved result to: {out}")
        if args.json_out:
            print(json.dumps(resp, ensure_ascii=False, indent=2))
        else:
            print(content)
        return 0

    eprint("[model-up] All models in the chain failed.")
    if last_error:
        eprint(f"[model-up] Last error: HTTP {last_error.status} - {last_error.detail}")
    return 1


def cmd_generate(args):
    cfg_dir = config_dir_from(args)
    cfg = load_config(cfg_dir)
    secrets = load_secrets(cfg_dir)
    generators = [
        mid for mid, entry in cfg["models"].items()
        if entry.get("generation") and entry.get("enabled", True)
    ]
    if not generators:
        raise ModelUpError(
            "No enabled generation model. Add one with "
            "'models add --id <id> --provider <p> --model <m> --generation'."
        )
    mid = args.model or cfg.get("default_generator") or generators[0]
    entry = cfg["models"].get(mid)
    if not entry or not entry.get("generation"):
        raise ModelUpError(
            f"'{mid}' is not a generation model. Available generators: {', '.join(generators)}"
        )
    provider = cfg["providers"][entry["provider"]]
    api_key = api_key_for(entry, provider, secrets)
    if api_key is None and provider.get("env_key"):
        raise ModelUpError(
            f"API key missing for provider '{entry['provider']}'. "
            f"Add {provider['env_key']}=<key> to {cfg_dir / 'secrets.env'}."
        )

    payload = {
        "model": entry["model"],
        "prompt": args.prompt,
        "size": args.size,
        "extra_body": {"response_format": "url" if args.url_output else "b64_json"},
    }
    if args.input:
        images = []
        for ref in [r.strip() for r in args.input.split(",") if r.strip()]:
            if ref.startswith(("http://", "https://", "data:")):
                images.append(ref)
                continue
            path = Path(ref)
            if not path.is_file():
                raise ModelUpError(f"Input image not found: {ref}")
            mime = mimetypes.guess_type(str(path))[0] or EXTRA_MIME.get(
                path.suffix.lower(), "application/octet-stream"
            )
            images.append(f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}")
        payload["extra_body"]["image"] = images

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    url = provider["base_url"].rstrip("/") + "/images/generations"
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            resp_obj = json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise ApiError(exc.code, exc.read().decode("utf-8", "replace")[:500]) from exc
    except urllib.error.URLError as exc:
        raise ApiError(0, str(exc.reason)) from exc

    data = (resp_obj.get("data") or [{}])[0]
    if args.json_out:
        print(json.dumps(resp_obj, ensure_ascii=False, indent=2))
    out_path = Path(args.out) if args.out else Path.cwd() / f"generated-{int(time.time())}.png"
    b64 = data.get("b64_json")
    if b64:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(base64.b64decode(b64))
        print(f"Saved generated image to: {out_path}")
        return 0
    img_url = data.get("url")
    if img_url:
        with urllib.request.urlopen(img_url, timeout=args.timeout) as resp:
            raw = resp.read()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(raw)
        print(f"Saved generated image (from URL) to: {out_path}")
        return 0
    raise ModelUpError(f"Generation response missing image data: {str(resp_obj)[:300]}")


def print_models_table(cfg):
    default_set = set(cfg.get("default_chain", []))
    header = f"{'ID':<22}{'PROVIDER':<12}{'MODEL':<22}{'MODALITIES':<18}{'ENABLED':<8}DEFAULT"
    print(header)
    print("-" * len(header))
    for mid, entry in cfg["models"].items():
        mods = "generation" if entry.get("generation") else ",".join(entry.get("modalities", ["image"]))
        enabled = "yes" if entry.get("enabled", True) else "no"
        mark = "*" if mid in default_set else ""
        print(f"{mid:<22}{entry['provider']:<12}{entry['model']:<22}{mods:<18}{enabled:<8}{mark}")
    print()
    print(f"default_chain: {', '.join(cfg.get('default_chain', []))}")


def cmd_models(args):
    cfg_dir = config_dir_from(args)
    cfg = load_config(cfg_dir)
    sub = args.models_command
    registry = cfg["models"]
    providers = cfg["providers"]

    if sub == "list":
        print_models_table(cfg)
        return 0

    if sub == "set-default":
        ids = [i.strip() for i in args.ids.split(",") if i.strip()]
        missing = [i for i in ids if i not in registry]
        if missing:
            raise ModelUpError(f"Unknown model ids: {', '.join(missing)}")
        cfg["default_chain"] = ids
        save_json(Path(cfg_dir) / "models.json", cfg)
        print(f"default_chain -> {', '.join(ids)}")
        return 0

    mid = args.id
    if mid not in registry and sub != "add":
        raise ModelUpError(f"Unknown model id '{mid}'. Run 'models list' to see available ids.")

    if sub == "add":
        provider_id = args.provider
        if provider_id not in providers:
            if not args.base_url:
                raise ModelUpError(
                    f"Provider '{provider_id}' is new; pass --base-url (and optionally --env-key)."
                )
            providers[provider_id] = {
                "base_url": args.base_url,
                "env_key": args.env_key or "",
            }
        entry = {
            "provider": provider_id,
            "model": args.model,
            "modalities": [m.strip() for m in args.modalities.split(",") if m.strip()],
            "enabled": args.enabled,
        }
        if args.generation:
            entry["generation"] = True
        if args.base_url and provider_id in providers:
            entry["base_url"] = args.base_url  # per-model override
        if args.env_key and provider_id in providers:
            entry["env_key"] = args.env_key  # per-model override
        registry[mid] = entry
        save_json(Path(cfg_dir) / "models.json", cfg)
        print(f"Added model '{mid}' (provider={provider_id}, model={args.model}).")
        return 0

    if sub == "remove":
        removed = registry.pop(mid)
        save_json(Path(cfg_dir) / "models.json", cfg)
        print(f"Removed model '{mid}' ({removed['model']}).")
        return 0

    if sub == "enable":
        registry[mid]["enabled"] = True
        save_json(Path(cfg_dir) / "models.json", cfg)
        print(f"Enabled '{mid}'.")
        return 0

    if sub == "disable":
        registry[mid]["enabled"] = False
        save_json(Path(cfg_dir) / "models.json", cfg)
        print(f"Disabled '{mid}'.")
        return 0

    raise ModelUpError(f"Unknown models subcommand: {sub}")


def mask_key(value):
    if not value:
        return "missing"
    if len(value) <= 8:
        return "set"
    return f"set (…{value[-4:]})"


def cmd_check(args):
    cfg_dir = config_dir_from(args)
    cfg = load_config(cfg_dir)
    secrets = load_secrets(cfg_dir)
    print(f"config_dir: {cfg_dir}")
    print(f"models.json: {cfg_dir / 'models.json'}")
    print(f"secrets.env: {cfg_dir / 'secrets.env'}")
    print()
    print_models_table(cfg)
    print()
    print(f"default_generator: {cfg.get('default_generator', '(none)')}")
    print()
    print("Providers:")
    for pid, pdef in cfg["providers"].items():
        key_state = mask_key(api_key_for({}, pdef, secrets)) if pdef.get("env_key") else "no key required"
        print(f"  {pid:<12} {pdef.get('base_url', ''):<55} key={key_state}")
    print()
    print()
    for mid in cfg.get("default_chain", []):
        if mid not in cfg["models"]:
            print(f"  WARNING: default_chain references unknown model '{mid}'")
        elif not cfg["models"][mid].get("enabled", True):
            print(f"  WARNING: default_chain references disabled model '{mid}'")
    return 0


# ---------------------------------------------------------------- CLI


def build_parser():
    parser = argparse.ArgumentParser(
        prog="mm_proxy.py",
        description="Multimodal proxy for text-only LLMs (model-up skill).",
    )
    parser.add_argument(
        "--config-dir",
        default=None,
        help="Config directory (default: <skill>/config, or $MODEL_UP_CONFIG_DIR).",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    pa = sub.add_parser("analyze", help="Send multimodal input to configured models.")
    pa.add_argument("input_ref", help="Local path, http(s) URL, or data: URI.")
    pa.add_argument(
        "--models",
        default=None,
        help="Comma-separated model ids, tried in order as fallback (default: config default_chain).",
    )
    pa.add_argument("--prompt", default=None, help="Question for the multimodal model.")
    pa.add_argument(
        "--mode",
        choices=list(MODES),
        default="general",
        help="Preset prompt (general|ocr|ui|diagram). Ignored when --prompt is set.",
    )
    pa.add_argument("--max-tokens", type=int, default=2048)
    pa.add_argument("--temperature", type=float, default=0.3)
    pa.add_argument("--timeout", type=int, default=90)
    pa.add_argument("--dry-run", action="store_true", help="Print the request instead of sending it.")
    pa.add_argument("--json", action="store_true", dest="json_out", help="Print the raw API response.")
    pa.add_argument("--save", default=None, help="Write the result text to a file.")
    pa.add_argument("--base-url", default=None, help="Override the provider base URL (debug/testing).")
    pa.add_argument("--verbose", action="store_true", help="Print which model succeeded.")
    pa.set_defaults(func=cmd_analyze)

    pm = sub.add_parser("models", help="Manage the model registry.")
    pms = pm.add_subparsers(dest="models_command", required=True)
    pl = pms.add_parser("list", help="List configured models.")
    pl.set_defaults(func=cmd_models)
    pa2 = pms.add_parser("add", help="Add a model (and optionally a new provider).")
    pa2.add_argument("--id", required=True)
    pa2.add_argument("--provider", required=True)
    pa2.add_argument("--model", required=True)
    pa2.add_argument("--modalities", default="image", help="Comma-separated: image,audio,video")
    pa2.add_argument("--base-url", default=None)
    pa2.add_argument("--env-key", default=None)
    pa2.add_argument("--disabled", action="store_false", dest="enabled")
    pa2.add_argument("--generation", action="store_true", help="Mark as a generation model (used by 'generate').")
    pa2.set_defaults(enabled=True, func=cmd_models)
    for name in ("remove", "enable", "disable"):
        pcmd = pms.add_parser(name)
        pcmd.add_argument("--id", required=True)
        pcmd.set_defaults(func=cmd_models)
    psd = pms.add_parser("set-default", help="Set the default fallback chain.")
    psd.add_argument("--ids", required=True, help="Comma-separated model ids.")
    psd.set_defaults(func=cmd_models)

    pg = sub.add_parser("generate", help="Generate an image with a generation model.")
    pg.add_argument("prompt", help="Text prompt describing the image to generate or edit.")
    pg.add_argument("--model", default=None, help="Generator model id (default: config default_generator).")
    pg.add_argument("--size", default="1024x1024", help="Output size, e.g. 1024x768, 1024x1024, 768x1024.")
    pg.add_argument(
        "--input",
        default=None,
        help="Comma-separated reference images for img2img / multi-image composition "
        "(path, URL, or data URI).",
    )
    pg.add_argument("--out", default=None, help="Save path for the generated image.")
    pg.add_argument("--url-output", action="store_true", help="Ask the API for a URL instead of base64.")
    pg.add_argument("--timeout", type=int, default=180, help="Timeout in seconds (docs recommend 60-360).")
    pg.add_argument("--dry-run", action="store_true", help="Print the request instead of sending it.")
    pg.add_argument("--json", action="store_true", dest="json_out", help="Print the raw API response.")
    pg.set_defaults(func=cmd_generate)

    pc = sub.add_parser("check", help="Validate config and key presence.")
    pc.set_defaults(func=cmd_check)
    return parser


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = build_parser().parse_args()
    try:
        return args.func(args)
    except ModelUpError as exc:
        eprint(f"[model-up] {exc}")
        return 2
    except KeyboardInterrupt:
        eprint("[model-up] Interrupted.")
        return 130


if __name__ == "__main__":
    sys.exit(main())
