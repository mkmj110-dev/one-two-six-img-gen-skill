# 126 图像生成 Skill

这是一个适用于 Codex / Claude Code 的 skill，用于通过 126 API 图像接口生成、编辑、轮询并下载图片。

## 一行安装

Windows PowerShell，会同时安装到 Codex 和 Claude Code：

```powershell
iwr -UseB https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.ps1 | iex
```

macOS / Linux，会同时安装到 Codex 和 Claude Code：

```bash
curl -fsSL https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.sh | bash
```

默认安装目录为：

```text
~/.codex/skills/126-img-gen
~/.claude/skills/126-img-gen
```

## 只安装到一个目标

Windows PowerShell，仅安装到 Codex：

```powershell
$p="$env:TEMP\install-126-img-gen.ps1"; iwr -UseB https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.ps1 -OutFile $p; powershell -ExecutionPolicy Bypass -File $p -Target codex
```

Windows PowerShell，仅安装到 Claude Code：

```powershell
$p="$env:TEMP\install-126-img-gen.ps1"; iwr -UseB https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.ps1 -OutFile $p; powershell -ExecutionPolicy Bypass -File $p -Target claude
```

macOS / Linux，仅安装到 Codex：

```bash
curl -fsSL https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.sh | TARGET=codex bash
```

macOS / Linux，仅安装到 Claude Code：

```bash
curl -fsSL https://raw.githubusercontent.com/mkmj110-dev/one-two-six-img-gen-skill/main/install.sh | TARGET=claude bash
```

## 配置

运行时设置你的 API key。不要把真实 key 提交到仓库。

PowerShell，仅当前窗口生效：

```powershell
$env:ONE_TWO_SIX_API_KEY = "sk-..."
```

PowerShell，持久保存到用户环境变量，适用于没有从同一个窗口启动的 Codex / Claude 会话：

```powershell
[Environment]::SetEnvironmentVariable("ONE_TWO_SIX_API_KEY", "sk-...", "User")
[Environment]::GetEnvironmentVariable("ONE_TWO_SIX_API_KEY", "User").Length
```

上面的长度检查可以确认 key 已存在，同时不会打印真实 key。

Bash：

```bash
export ONE_TWO_SIX_API_KEY="sk-..."
```

可选配置：

```bash
export ONE_TWO_SIX_BASE_URL="https://chx126.xyz/v1"
```

## 使用示例

安装完成后，可以直接向 Codex 或 Claude Code 提出需求：

```text
Use $126-img-gen to generate a 2K image of beautiful Beidaihe beach at sunrise.
```

skill 会调用内置脚本，例如：

```bash
python ~/.codex/skills/126-img-gen/scripts/126_img_gen.py \
  --mode gpt-image-2 \
  --model gpt-image-2-2K \
  --prompt "A 2K realistic travel photo of beautiful Beidaihe beach at sunrise, no text, no watermark" \
  --aspect-ratio 16:9 \
  --out beidaihe-2k.png
```

## 说明

- 替换已有安装前，会先备份旧版本。
- 脚本会发送浏览器风格的 `User-Agent`，用于减少边缘防护拦截，例如 `HTTP 403 / error code: 1010`。
- 脚本会重试临时 HTTP / 网络失败，例如 `WinError 10060`、`RemoteDisconnected` 和其他瞬时 HTTP 连接错误。
- 如果异步任务已经提交，但轮询超时，应查询已有任务，而不是重复创建新任务。
