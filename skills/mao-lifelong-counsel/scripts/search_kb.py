#!/usr/bin/env python3
"""在分层原文库里按关键词查段落、查篇名、看原文。

用法：
  python search_kb.py 调查 发言权                    # 同一段里同时出现所有关键词（忽略标点和常见异体字）
  python search_kb.py 庐山 彭德怀 --tiers AW,B,C     # 限定层级
  python search_kb.py 实践 真理 --any                # 任一关键词即可
  python search_kb.py --titles 十大关系              # 只查篇名/路径
  python search_kb.py --show "A5_选集第五卷/209-论十大关系.md" --lines 1-40
默认查毛泽东文本（A A5 AW S Y AM B C）；M=马恩列原著需用 --tiers M 指定，或用 --tiers all。
"""
import argparse
import os
import sys

sys.dont_write_bytecode = True  # 不往 skill 目录里写 __pycache__

from kbcommon import (KB_DIR, KB_MISSING, MAO_TIERS, TIERS, iter_docs, kb_ready, norm, parse_tiers,  # noqa: E402
                      split_notes, utf8_stdout)


class Tee:
    """同时写屏幕和文件。"""

    def __init__(self, *streams):
        self.streams = streams

    def write(self, s):
        for st in self.streams:
            st.write(s)

    def flush(self):
        for st in self.streams:
            st.flush()


def show(rel, lines):
    p = os.path.join(KB_DIR, *rel.replace('\\', '/').split('/'))
    if not os.path.exists(p):
        # 写到 stdout，这样 --out 文件里也能看到失败原因，而不是一个空文件
        print(f'找不到：{rel}（先用 --titles 查准路径）')
        return 1
    rows = open(p, encoding='utf-8', errors='ignore').read().split('\n')
    a, b = 1, len(rows)
    if lines:
        x, _, y = lines.partition('-')
        a, b = int(x), int(y or x)
    for i in range(a, min(b, len(rows)) + 1):
        print(f'{i:5d}  {rows[i - 1]}')


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description='检索毛泽东原文库')
    ap.add_argument('keywords', nargs='*')
    ap.add_argument('--tiers', help='逗号分隔的层级，默认 A,A5,AW,S,Y,AM,B,C；all 表示全部')
    ap.add_argument('--any', action='store_true', help='任一关键词命中即可（默认要求全部命中）')
    ap.add_argument('--titles', action='store_true', help='只匹配篇名/路径')
    ap.add_argument('--limit', type=int, default=30)
    ap.add_argument('--width', type=int, default=120, help='每条结果显示的字数')
    ap.add_argument('--notes', action='store_true', help='同时检索静火版编者注释（.notes.md）')
    ap.add_argument('--show', help='显示 kb 内某个文件')
    ap.add_argument('--lines', help='配合 --show，例如 10-60')
    ap.add_argument('--out', help='把结果另存为 UTF-8 文件')
    a = ap.parse_args()
    if not a.show and not a.keywords:
        ap.error('至少给一个关键词，或用 --show')
    out_file = open(a.out, 'w', encoding='utf-8') if a.out else None
    if out_file:
        sys.stdout = Tee(sys.stdout, out_file)
    try:
        code = show(a.show, a.lines) if a.show else search(a)
    finally:
        if out_file:
            sys.stdout = sys.stdout.streams[0]
            out_file.close()
    sys.exit(code or 0)


def search(a):
    if not kb_ready():
        print(KB_MISSING)
        return 1
    tiers = parse_tiers(a.tiers, MAO_TIERS)
    kws = [norm(k) for k in a.keywords if norm(k)]
    ok = any if a.any else all
    n = 0
    for t, rel, raw in iter_docs(tiers, include_notes=a.notes):
        if a.titles:
            if ok(k in norm(rel) for k in kws):
                print(f'[{t}] {rel}')
                n += 1
        else:
            body_lines = split_notes(raw, t)[0].count('\n') + 1  # 之后的行属于编者注释
            for i, line in enumerate(raw.split('\n'), 1):
                nl = norm(line)
                if nl and ok(k in nl for k in kws):
                    s = line.strip()
                    first = min((s.find(k0) for k0 in a.keywords if s.find(k0) >= 0), default=0)
                    start = max(0, first - a.width // 3)
                    snippet = s[start:start + a.width]
                    tag = '（编者注释，不是毛的话）' if i > body_lines else ''
                    print(f'[{t}] {rel}:{i}{tag}  {"…" if start else ""}{snippet}{"…" if start + a.width < len(s) else ""}')
                    n += 1
                    if n >= a.limit:
                        break
        if n >= a.limit:
            print(f'（已达 --limit {a.limit}，可加大或缩小层级/关键词）')
            break
    if n == 0:
        print('没有命中。可以换同义词、减少关键词、加 --any，或用 --tiers all 扩大范围。')
    print('层级：' + '；'.join(f'{k}={v[1]}' for k, v in TIERS.items() if k in tiers))


if __name__ == '__main__':
    main()
