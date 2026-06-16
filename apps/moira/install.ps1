# moira インストーラ（Windows / PowerShell 5+）
#
# 使い方:
#   irm https://raw.githubusercontent.com/kyarameru1005/claude-kyarameru-toolbox/main/apps/moira/install.ps1 | iex
#
# 環境変数:
#   $env:MOIRA_VERSION  インストールするタグ（既定: 最新リリース）

$ErrorActionPreference = 'Stop'

$repo = 'kyarameru1005/claude-kyarameru-toolbox'
$target = 'x86_64-pc-windows-msvc'

# --- バージョン決定（既定は最新リリース）---
$version = $env:MOIRA_VERSION
if (-not $version) {
    $release = Invoke-RestMethod "https://api.github.com/repos/$repo/releases/latest"
    $version = $release.tag_name
}
if (-not $version) {
    throw "moira-install: 最新リリースの取得に失敗（リポジトリが public か確認）"
}

$asset = "moira-$target.zip"
$url = "https://github.com/$repo/releases/download/$version/$asset"

# --- ダウンロード & 展開 ---
$installDir = Join-Path $env:LOCALAPPDATA 'Programs\moira'
New-Item -ItemType Directory -Force -Path $installDir | Out-Null
$tmp = Join-Path $env:TEMP $asset

Write-Host "moira-install: $version ($target) を取得中..."
Invoke-WebRequest -Uri $url -OutFile $tmp

# --- チェックサム検証（必須。取得失敗・不一致は中止）---
Write-Host "moira-install: チェックサムを検証中..."
try {
    $expected = (Invoke-RestMethod -Uri "$url.sha256").Trim().ToLower()
} catch {
    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
    throw "moira-install: チェックサム ($url.sha256) の取得に失敗。検証できないため中止します"
}
$actual = (Get-FileHash -Path $tmp -Algorithm SHA256).Hash.ToLower()
if (-not $expected -or $expected -ne $actual) {
    Remove-Item $tmp -Force -ErrorAction SilentlyContinue
    throw "moira-install: チェックサム不一致（期待: $expected / 実際: $actual）。中止します"
}

Expand-Archive -Path $tmp -DestinationPath $installDir -Force
Remove-Item $tmp -Force

# --- ユーザー環境変数 PATH に追加 ---
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($userPath -notlike "*$installDir*") {
    [Environment]::SetEnvironmentVariable('Path', "$userPath;$installDir", 'User')
    Write-Host "moira-install: PATH に $installDir を追加しました（新しいシェルで有効）"
}

Write-Host "moira-install: インストール完了 -> $installDir\moira.exe"
& "$installDir\moira.exe" --version
