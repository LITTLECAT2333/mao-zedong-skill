#!/usr/bin/env sh
# 把 skill 安装到本机（macOS / Linux）
# 用法：在仓库根目录运行
#   sh install/install.sh               # 标准版，装给 Codex（默认，$CODEX_HOME/skills 或 ~/.codex/skills）
#   sh install/install.sh codex full    # 完整版（两个版本的区别见 docs/VERSIONS.md）
#   sh install/install.sh agents        # 装到 ~/.agents/skills（新版 Codex 文档推荐的位置）
#   sh install/install.sh claude        # 装给 Claude Code（~/.claude/skills）
# 第一个参数是目标（codex / agents / claude），第二个是版本（standard / full）。
# 同一个工具只装一处、只装一个版本。已有旧版本会先移到 ~/.mao-skill-backups/ 备份，不会删除，也不会留在 skills 目录里被重复加载。
set -e
TARGET="${1:-codex}"
BASE=mao-lifelong-counsel
case "${2:-standard}" in
  standard) NAME=$BASE; OTHER=$BASE-full ;;
  full)     NAME=$BASE-full; OTHER=$BASE ;;
  *) echo "版本只能是 standard 或 full"; exit 1 ;;
esac
SRC="$(cd "$(dirname "$0")/.." && pwd)/skills/$NAME"
[ -f "$SRC/SKILL.md" ] || { echo "找不到 $SRC/SKILL.md"; exit 1; }
case "$TARGET" in
  codex)  ROOT="${CODEX_HOME:-$HOME/.codex}/skills" ;;
  agents) ROOT="$HOME/.agents/skills" ;;
  claude) ROOT="$HOME/.claude/skills" ;;
  *) echo "目标只能是 codex、agents 或 claude"; exit 1 ;;
esac
mkdir -p "$ROOT"
DST="$ROOT/$NAME"
if [ -e "$DST" ]; then
  BAKROOT="$HOME/.mao-skill-backups"
  mkdir -p "$BAKROOT"
  BAK="$BAKROOT/$NAME-$TARGET-$(date +%Y%m%d-%H%M%S)"
  mv "$DST" "$BAK"
  echo "旧版本已移到 $BAK"
fi
cp -R "$SRC" "$DST"
echo "已安装 $NAME 到 $DST"
if [ -e "$ROOT/$OTHER" ]; then
  echo "注意：$ROOT 里还装着另一个版本 $OTHER。两个版本会同时被触发，建议只留一个：把不用的那个文件夹移走即可。"
fi
echo "请重启 Codex 或 Claude Code。备份确认没用以后可以手动删除。"
