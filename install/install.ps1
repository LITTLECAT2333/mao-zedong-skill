# 把 skill 安装到本机（Windows PowerShell）
# 用法：在仓库根目录运行
#   powershell -ExecutionPolicy Bypass -File install\install.ps1                  # 标准版，装给 Codex（默认，$CODEX_HOME\skills 或 ~\.codex\skills）
#   powershell -ExecutionPolicy Bypass -File install\install.ps1 -Edition full    # 完整版（两个版本的区别见 docs/VERSIONS.md）
#   powershell -ExecutionPolicy Bypass -File install\install.ps1 -Target agents   # 装到 ~\.agents\skills（新版 Codex 文档推荐的位置）
#   powershell -ExecutionPolicy Bypass -File install\install.ps1 -Target claude   # 装给 Claude Code（~\.claude\skills）
# 同一个工具只装一处、只装一个版本。已有旧版本会先移到 ~\.mao-skill-backups\ 备份，不会删除，也不会留在 skills 目录里被重复加载。
param(
  [ValidateSet('codex', 'agents', 'claude')][string]$Target = 'codex',
  [ValidateSet('standard', 'full')][string]$Edition = 'standard'
)

$base = 'mao-lifelong-counsel'
$name = if ($Edition -eq 'full') { "$base-full" } else { $base }
$other = if ($Edition -eq 'full') { $base } else { "$base-full" }
$src = Join-Path (Split-Path $PSScriptRoot -Parent) "skills\$name"
if (-not (Test-Path (Join-Path $src 'SKILL.md'))) { Write-Error "找不到 $src\SKILL.md"; exit 1 }

switch ($Target) {
  'codex'  { $root = if ($env:CODEX_HOME) { Join-Path $env:CODEX_HOME 'skills' } else { Join-Path $HOME '.codex\skills' } }
  'agents' { $root = Join-Path $HOME '.agents\skills' }
  'claude' { $root = Join-Path $HOME '.claude\skills' }
}
New-Item -ItemType Directory -Force $root | Out-Null
$dst = Join-Path $root $name
if (Test-Path $dst) {
  $bakRoot = Join-Path $HOME '.mao-skill-backups'
  New-Item -ItemType Directory -Force $bakRoot | Out-Null
  $bak = Join-Path $bakRoot ("{0}-{1}-{2}" -f $name, $Target, (Get-Date -Format 'yyyyMMdd-HHmmss'))
  Move-Item $dst $bak
  Write-Host "旧版本已移到 $bak"
}
Copy-Item -Recurse $src $dst
Write-Host "已安装 $name 到 $dst"
if (Test-Path (Join-Path $root $other)) {
  Write-Warning "$root 里还装着另一个版本 $other。两个版本会同时被触发，建议只留一个：把不用的那个文件夹移走即可。"
}
Write-Host '请重启 Codex 或 Claude Code。备份确认没用以后可以手动删除。'
