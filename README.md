# 126 Img Gen Skill

Codex skill for generating, editing, polling, and downloading images through 126 API image endpoints.

## Install

Copy this directory into your Codex skills directory:

```powershell
Copy-Item -Recurse .\126-img-gen C:\Users\$env:USERNAME\.codex\skills\126-img-gen
```

Then restart Codex.

## Configure

Set your API key at runtime. Do not commit real keys.

```powershell
$env:ONE_TWO_SIX_API_KEY = "sk-..."
```

Optional:

```powershell
$env:ONE_TWO_SIX_BASE_URL = "https://chx126.xyz/v1"
```

## Example

```powershell
python .\126-img-gen\scripts\126_img_gen.py `
  --mode gpt-image-2 `
  --model gpt-image-2-2K `
  --prompt "一张2K高清写实风景摄影，美丽的北戴河海滨，无文字，无水印" `
  --aspect-ratio 16:9 `
  --out beidaihe-2k.png
```

## Notes

- The script sends a browser-style `User-Agent` to avoid edge protection blocks such as `HTTP 403 / error code: 1010`.
- The script retries temporary HTTP/network failures such as `WinError 10060`.
- If an async task has already been submitted and polling times out, query the existing task instead of creating a duplicate.
