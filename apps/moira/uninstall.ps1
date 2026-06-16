# moira アンインストーラ（Windows / PowerShell 5+）
#
# 使い方:
#   irm https://raw.githubusercontent.com/kyarameru1005/claude-kyarameru-toolbox/main/apps/moira/uninstall.ps1 | iex

$ErrorActionPreference = 'Stop'

$installDir = Join-Path $env:LOCALAPPDATA 'Programs\moira'

if (Test-Path $installDir) {
    Remove-Item -Recurse -Force $installDir
    Write-Host "moira-uninstall: 削除しました -> $installDir"
} else {
    Write-Host "moira-uninstall: $installDir が見つかりません"
}

# ユーザー環境変数 PATH から除去
$userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
if ($userPath -like "*$installDir*") {
    $newPath = ($userPath -split ';' | Where-Object { $_ -and $_ -ne $installDir }) -join ';'
    [Environment]::SetEnvironmentVariable('Path', $newPath, 'User')
    Write-Host "moira-uninstall: PATH から $installDir を除去しました（新しいシェルで有効）"
}

Write-Host "moira-uninstall: 各リポジトリの .ai\moira.json（タスク台帳）は残ります。必要なら手動で削除してください。"
