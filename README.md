# 126 Img Gen Skill

Codex / Claude Code skill for generating, editing, polling, and downloading images through 126 API image endpoints.

## One-Line Install

Windows PowerShell, installs to both Codex and Claude Code:

```powershell
iwr -UseB https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.ps1 | iex
```

macOS / Linux, installs to both Codex and Claude Code:

```bash
curl -fsSL https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.sh | bash
```

The default target installs to:

```text
~/.codex/skills/126-img-gen
~/.claude/skills/126-img-gen
```

## Install One Target Only

Windows PowerShell, Codex only:

```powershell
$p="$env:TEMP\install-126-img-gen.ps1"; iwr -UseB https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.ps1 -OutFile $p; powershell -ExecutionPolicy Bypass -File $p -Target codex
```

Windows PowerShell, Claude Code only:

```powershell
$p="$env:TEMP\install-126-img-gen.ps1"; iwr -UseB https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.ps1 -OutFile $p; powershell -ExecutionPolicy Bypass -File $p -Target claude
```

macOS / Linux, Codex only:

```bash
curl -fsSL https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.sh | TARGET=codex bash
```

macOS / Linux, Claude Code only:

```bash
curl -fsSL https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.sh | TARGET=claude bash
```

## Configure

Set your API key at runtime. Do not commit real keys.

PowerShell:

```powershell
$env:ONE_TWO_SIX_API_KEY = "sk-..."
```

Bash:

```bash
export ONE_TWO_SIX_API_KEY="sk-..."
```

Optional:

```bash
export ONE_TWO_SIX_BASE_URL="https://chx126.xyz/v1"
```

## Usage Example

After installation, ask Codex or Claude Code:

```text
Use $126-img-gen to generate a 2K image of beautiful Beidaihe beach at sunrise.
```

The skill will use the bundled script:

```bash
python ~/.codex/skills/126-img-gen/scripts/126_img_gen.py \
  --mode gpt-image-2 \
  --model gpt-image-2-2K \
  --prompt "A 2K realistic travel photo of beautiful Beidaihe beach at sunrise, no text, no watermark" \
  --aspect-ratio 16:9 \
  --out beidaihe-2k.png
```

## Notes

- Existing installs are backed up before replacement.
- The script sends a browser-style `User-Agent` to avoid edge protection blocks such as `HTTP 403 / error code: 1010`.
- The script retries temporary HTTP/network failures such as `WinError 10060`.
- If an async task has already been submitted and polling times out, query the existing task instead of creating a duplicate.
