---
name: 126-img-gen
description: Generate, edit, poll, and download images through 126 API image endpoints. Use when the user asks to create images with 126 API, image2, gpt-image-2, gpt-image-2-2K, gpt-image-2-4K, /v1/images/generations, /v1/images/edits, or the async /v1/videos image task API; also use when converting prompts into ready-to-run image API calls or polling image tasks.
---

# 126 Img Gen

## Overview

Use this skill to call 126 API image-generation endpoints and save the resulting image locally. It covers synchronous `image2` OpenAI-compatible image endpoints and asynchronous `gpt-image-2` image tasks.

Default base URL is `https://chx126.xyz/v1`. Read the API key from `ONE_TWO_SIX_API_KEY`, `126_API_KEY`, `OPENAI_API_KEY`, or pass `--api-key`.

## Quick Start

Prefer the bundled script for real API calls. Resolve the script path from the installed skill directory:

```powershell
$env:ONE_TWO_SIX_API_KEY = "sk-..."
python ~/.codex/skills/126-img-gen/scripts/126_img_gen.py `
  --mode gpt-image-2 `
  --model gpt-image-2-2K `
  --prompt "一张2K高清写实风景摄影，美丽的北戴河海滨，清晨金色阳光洒在海面，无文字，无水印" `
  --aspect-ratio 16:9 `
  --out beidaihe-2k.png
```

For Claude Code installs, the equivalent script path is usually:

```text
~/.claude/skills/126-img-gen/scripts/126_img_gen.py
```

When running from inside the skill folder, use:

```powershell
python ./scripts/126_img_gen.py --mode image2 --prompt "生成一张电商主图，白色背景，主体是一只金属质感保温杯" --out output.png
```

## Choose The Endpoint

- Use `--mode image2` for synchronous text-to-image with `POST /v1/images/generations`.
- Use `--mode image2-edit` for synchronous image editing with `POST /v1/images/edits`.
- Use `--mode gpt-image-2` for asynchronous text-to-image or image-to-image with `POST /v1/videos` and polling `GET /v1/videos/{task_id}`.
- Use `--model gpt-image-2-2K` or `--model gpt-image-2-4K` when the user asks for higher-resolution async models. Keep `K` uppercase.

Do not use or document video-generation models for this skill. The async image endpoint uses the `/v1/videos` path, but the relevant object is an image task.

## Common Commands

Generate with `image2`:

```powershell
python ./scripts/126_img_gen.py `
  --mode image2 `
  --prompt "一张极简科技感海报，主题是 AI API 网关" `
  --size 1024x1024 `
  --out poster.png
```

Edit an existing image:

```powershell
python ./scripts/126_img_gen.py `
  --mode image2-edit `
  --prompt "把杯子改成磨砂黑色，保留背景和构图" `
  --image input.png `
  --out edited.png
```

Submit and poll an async `gpt-image-2` task:

```powershell
python ./scripts/126_img_gen.py `
  --mode gpt-image-2 `
  --model gpt-image-2-4K `
  --prompt "生成一张高端护肤品广告图，金色瓶身，黑色背景" `
  --aspect-ratio 9:16 `
  --out ad.png
```

Use reference images with async image-to-image:

```powershell
python ./scripts/126_img_gen.py `
  --mode gpt-image-2 `
  --prompt "将参考图改成油画风格" `
  --ref-image "https://example.com/reference.png" `
  --aspect-ratio 16:9 `
  --out oil.png
```

## Workflow

1. Ask for a prompt only if the user has not supplied enough visual intent.
2. Choose `image2` for immediate results, or `gpt-image-2` when the user asks for async, 2K, 4K, aspect ratio control, or reference-image arrays.
3. Save outputs to a concrete local path. Default to the current working directory if the user gives no location.
4. Never print or store the real API key in generated files, logs, docs, or final answers.
5. If the API returns a URL, download it immediately because generated image URLs may expire.

## Troubleshooting Notes

- If `POST /v1/videos` returns `HTTP 403` with `error code: 1010`, the request was likely blocked by edge protection because the client did not look like a normal HTTP client. The bundled script sends a browser-style `User-Agent`; keep it enabled.
- If polling or downloading fails with `WinError 10060`, this is usually a temporary network timeout. The bundled script retries JSON requests, multipart uploads, polling, and downloads with short exponential backoff.
- If the async task was already submitted before a timeout, poll `GET /v1/videos/{task_id}` instead of submitting the same prompt repeatedly.
- Do not include API keys in request body files, status JSON, logs, or saved examples. Use environment variables or `--api-key` only at runtime.

## Resources

- `scripts/126_img_gen.py`: CLI for generating/editing images and downloading the first result.
- `references/api.md`: concise endpoint and parameter reference. Read it when building custom requests or debugging API payloads.
