#!/usr/bin/env python3
"""逐字核验归于毛泽东的引文：在分层原文库里找出处，给出能否加引号、该怎么标注。

用法：
  python verify_quote.py "没有调查，没有发言权" "一切反动派都是纸老虎"
  python verify_quote.py --file quotes.txt          # 每行一条
  python verify_quote.py --tiers A,AW "……"           # 只查指定层级（默认查毛泽东文本 A A5 AW S Y AM B C）
  python verify_quote.py --json "……"                 # 机器可读输出
引文里的省略号（……）会被当作分段，各段须出现在同一篇里。比对前去掉标点并统一常见异体字。
"""
import argparse
import json
import sys

sys.dont_write_bytecode = True  # 不往 skill 目录里写 __pycache__

from kbcommon import (ELLIPSIS, KB_MISSING, MAO_TIERS, TIERS, context, iter_docs, kb_ready, load_blacklist,  # noqa: E402
                      norm, norm_map, parse_tiers, split_notes, utf8_stdout)

VERDICT = {
    'A': '可引用', 'A5': '可引用', 'AW': '可引用', 'S': '可引用（确认是诗句本身，不是注释）',
    'Y': '可引用（语录是摘句，最好回原篇核对上下文）', 'AM': '可引用（1949 年前原始版本，可能与后来选集文字不同）',
    'D': '需核对原件：官方汇编的 OCR 文本个别字可能有误',
    'P': '命中哲学批注集：可能是原书文字，必须确认是他的批注',
    'N': '命中年谱：只有引号里的摘引可能是他的话，叙述是编者的',
    'B': '需标注来源：只在谈话记录/散篇里找到', 'C': '需标注来源：只在非官方汇编里找到',
    'M': '这句出自马恩列原著或艾思奇，不是毛泽东的话（可能是转引或译本编者注，看上下文确定原作者和篇目）',
}
# 诗词合集里，每首诗前面是“返回目录”，后面跟着诗题；诗后的这些小标题是网页编者写的
POEM_NOTES = ('【注释】', '【题解】', '【题记】', '【作法】', '【赏析】')


def segments(q):
    segs = [norm(s) for s in ELLIPSIS.split(q)]
    return [s for s in segs if len(s) >= 4] or ([norm(q)] if norm(q) else [])


def load(tiers):
    """每篇拆成正文和编者注释：(层级, 路径, 正文, 正文规范化, 注释, 注释规范化)。"""
    docs = []
    for t, rel, raw in iter_docs(tiers):
        body, notes = split_notes(raw, t)
        docs.append((t, rel, body, norm(body), notes, norm(notes)))
    return docs


def poem_title(text, nidx):
    """诗词合集：取命中位置之前最近的诗题，并判断命中是否落在诗后的注释、题解里。"""
    _, pos = norm_map(text)
    if nidx >= len(pos):
        return '', False
    a = pos[nidx]
    k = text.rfind('返回目录', 0, a)
    if k < 0:
        return '', False
    seg = text[k:a]
    rows = [r.strip() for r in seg.split('\n')[1:] if r.strip()]
    return (rows[0] if rows else ''), any(m in seg for m in POEM_NOTES)


def find(segs, docs, max_hits, use_notes=False):
    hits = []
    for t, rel, body, nb, notes, nn in docs:
        text, ntext = (notes, nn) if use_notes else (body, nb)
        if segs and ntext and all(s in ntext for s in segs):
            i = ntext.find(segs[0])
            h = {'tier': t, 'source': TIERS[t][1], 'file': rel + ('（编者注释）' if use_notes else ''),
                 'context': context(text, i, len(segs[0]))}
            if t == 'S' and not use_notes:
                h['poem'], h['in_poem_notes'] = poem_title(text, i)
            hits.append(h)
            if len(hits) >= max_hits:
                break
    return hits


def coverage(nq, docs, k=6):
    grams = [nq[i:i + k] for i in range(max(len(nq) - k + 1, 1))]
    if not grams:
        return 0.0
    blob_hits = sum(1 for g in grams if any(g in d[3] for d in docs))  # d[3] 是正文规范化文本
    return round(blob_hits / len(grams), 2)


def judge(res, segs, docs, other_docs, max_hits):
    res['hits'] = find(segs, docs, max_hits)
    if res['hits']:
        best = res['hits'][0]
        t = best['tier']
        res['verdict'] = f'{VERDICT[t]}（最高层级 {t}：{TIERS[t][1]}；标注方式：{TIERS[t][2]}）'
        if t == 'S':
            title = f'；所在诗：{best["poem"]}' if best.get('poem') else ''
            if best.get('in_poem_notes'):
                res['verdict'] = f'只在诗词网页的注释或题解里找到：那是网页编者写的，不是毛泽东的诗句{title}'
            else:
                res['verdict'] += title.replace('所在诗', '诗题')
        return
    # 正文里没有：先看马恩列原著，再看是否只出现在选集、文集的编者注释里
    other = find(segs, other_docs, max_hits)
    in_notes = find(segs, docs, 2, use_notes=True)
    if other:
        t = other[0]['tier']
        res['hits'] = other + in_notes
        res['verdict'] = f'{VERDICT[t]}（{TIERS[t][1]}）'
        return
    if in_notes:
        res['hits'] = in_notes
        res['verdict'] = '只出现在编者注释里（多为编者引用他人或说明背景），不是毛泽东的话'
        return
    cov = coverage(''.join(segs), docs)
    res['coverage'] = cov
    hint = '；接近原文，可能有改字、拼接或语序变化，用 search_kb.py 查原句' if cov >= 0.6 else ''
    res['verdict'] = f'未核到：不要加引号，改为转述并注明“未核到原文”（6 字片段覆盖 {cov}{hint}）'


def check(q, docs, other_docs, blacklist, max_hits):
    segs = segments(q)
    res = {'quote': q, 'hits': [], 'verdict': '', 'notes': []}
    if sum(len(s) for s in segs) < 6:
        res['notes'].append('太短：几个字的词组到处都有，命中也证明不了出处')
    listed = False
    for word, fact, action in blacklist:
        nw = norm(word)
        if nw and (nw in norm(q) or (len(norm(q)) >= 6 and norm(q) in nw)):
            res['notes'].append(f'易错清单：「{word}」——{fact}；处理：{action}')
            listed = True
    judge(res, segs, docs, other_docs, max_hits)
    if listed:
        res['verdict'] = '命中易错清单，先按清单的处理意见办；脚本检索结果：' + res['verdict']
    return res


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description='核验毛泽东引文出处')
    ap.add_argument('quotes', nargs='*')
    ap.add_argument('--file', help='每行一条引文的 UTF-8 文本文件')
    ap.add_argument('--tiers', help='逗号分隔的层级，默认 A,A5,AW,S,Y,AM,B,C；all 表示全部')
    ap.add_argument('--max-hits', type=int, default=4)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--out', help='把结果另存为 UTF-8 文件')
    a = ap.parse_args()
    qs = list(a.quotes)
    if a.file:
        qs += [x.strip() for x in open(a.file, encoding='utf-8') if x.strip()]
    if not qs:
        ap.error('至少给一条引文')
    tiers = parse_tiers(a.tiers, MAO_TIERS)
    docs = load(tiers)
    others = load([t for t in ('M',) if t not in tiers])
    bl = load_blacklist()
    results = [check(q, docs, others, bl, a.max_hits) for q in qs]
    if a.json:
        text = json.dumps(results, ensure_ascii=False, indent=1)
    else:
        lines = []
        for r in results:
            lines.append(f'■ {r["quote"]}')
            lines.append(f'  结论：{r["verdict"]}')
            for n in r['notes']:
                lines.append(f'  注意：{n}')
            for h in r['hits']:
                extra = f'（诗题：{h["poem"]}）' if h.get('poem') else ''
                extra += '（命中在注释或题解里）' if h.get('in_poem_notes') else ''
                lines.append(f'  [{h["tier"]}] {h["file"]}{extra}')
                lines.append(f'      {h["context"]}')
        text = '\n'.join(lines)
    if not kb_ready():
        text = (KB_MISSING + '\n' + text) if not a.json else text
        sys.stderr.write(KB_MISSING + '\n')
    print(text)
    if a.out:
        open(a.out, 'w', encoding='utf-8').write(text)


if __name__ == '__main__':
    main()
