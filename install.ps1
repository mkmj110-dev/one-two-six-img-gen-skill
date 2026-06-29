param(
  [ValidateSet("all", "codex", "claude")]
  [string]$Target = "all",
  [string]$Repo = "mkmj110-dev/one-two-six-img-gen-skill",
  [string]$Ref = "main",
  [string]$InstallHome = [Environment]::GetFolderPath("UserProfile")
)

$ErrorActionPreference = "Stop"

function Install-Skill($DestinationRoot) {
  $skillName = "126-img-gen"
  $destination = Join-Path $DestinationRoot $skillName
  New-Item -ItemType Directory -Force -Path $DestinationRoot | Out-Null

  if (Test-Path $destination) {
    $timestamp = Get-Date -Format "yyyyMMddHHmmss"
    $backup = "$destination.bak-$timestamp"
    Move-Item -Path $destination -Destination $backup
    Write-Host "Backed up existing skill: $backup"
  }

  Copy-Item -Recurse -Force -Path $script:SkillSource -Destination $destination
  Write-Host "Installed $skillName -> $destination"
}

$tempRoot = Join-Path ([System.IO.Path]::GetTempPath()) ("126-img-gen-skill-" + [System.Guid]::NewGuid().ToString("N"))
$zipPath = Join-Path $tempRoot "skill.zip"
$extractPath = Join-Path $tempRoot "extract"

New-Item -ItemType Directory -Force -Path $tempRoot, $extractPath | Out-Null

try {
  $url = "https://codeload.github.com/$Repo/zip/refs/heads/$Ref"
  Write-Host "Downloading $url"
  Invoke-WebRequest -Uri $url -OutFile $zipPath -UseBasicParsing
  Expand-Archive -Path $zipPath -DestinationPath $extractPath -Force

  $script:SkillSource = Get-ChildItem -Path $extractPath -Directory -Recurse |
    Where-Object { $_.Name -eq "126-img-gen" -and (Test-Path (Join-Path $_.FullName "SKILL.md")) } |
    Select-Object -First 1 -ExpandProperty FullName

  if (-not $script:SkillSource) {
    throw "Could not find 126-img-gen/SKILL.md in downloaded archive."
  }

  $homeDir = $InstallHome
  if ($Target -eq "all" -or $Target -eq "codex") {
    Install-Skill (Join-Path $homeDir ".codex\skills")
  }
  if ($Target -eq "all" -or $Target -eq "claude") {
    Install-Skill (Join-Path $homeDir ".claude\skills")
  }

  Write-Host ""
  Write-Host "Done. Restart Codex if it was already open. Claude Code usually detects skill changes automatically."
  Write-Host "Set ONE_TWO_SIX_API_KEY before using the skill."
} finally {
  Remove-Item -Recurse -Force $tempRoot -ErrorAction SilentlyContinue
}
