#!/usr/bin/env python3
"""按处境找思维模式：在 references/patterns/ 的 14 个领域、全部模式里打分排序，打印最合用的几个。

用法：
  python find_patterns.py 几条路要选 谈判让步 以弱对强 期限紧
  python find_patterns.py 带团队 有人拖后腿 内部分歧 --top 8
  python find_patterns.py 读书 读不进去 --domains JY,RZ --full 2
  python find_patterns.py --show ZZ-44 BZ-05            # 直接打印指定编号的模式
  加 --evidence 连跨期证据一起打印；加 --out 结果.txt 另存为 UTF-8 文件。

关键词写成抽象的处境（「几条路要选」「对手比我强」「做成以后怕松懈」），比写行业名词（「SaaS」「估值」）更容易找到。
打分只看字面：把关键词和模式的名字、一句话、触发、他常问的问题、推理链、可迁移拆成两字片段比对，越少见的片段分越高。
"""
import argparse
import math
import os
import re
import sys
from collections import Counter

sys.dont_write_bytecode = True

from kbcommon import SKILL_DIR, utf8_stdout  # noqa: E402

PAT_DIR = os.path.join(SKILL_DIR, 'references', 'patterns')
DOMAINS = [('RZ', '认识与求知'), ('BZ', '辩证法'), ('LS', '历史观'), ('ZR', '自然与科学'), ('SJ', '社会与经济'),
           ('ZZ', '组织与领导'), ('LC', '立场与群众'), ('DZ', '斗争与竞争'), ('GJ', '国际与世界'), ('JY', '教育与青年'),
           ('WY', '文艺与语言'), ('YZ', '意志与人生'), ('JX', '继续革命与防变质'), ('FP', '复盘与修正')]
FIELDS = ['一句话', '触发', '推理链', '他常问的问题', '跨期证据', '变化', '边界与失误', '可迁移', '相关', '来源簇']
WEIGHT = {'名字': 2.5, '触发': 3.0, '一句话': 2.0, '他常问的问题': 1.5, '可迁移': 2.0, '推理链': 1.0}
# 平常说法 → 模式里常用的说法（只做扩展，原词照样参与比对）
SYNONYMS = {
    '选择': '拍板 几条路 方案', '决定': '拍板 决心 方案', '纠结': '拍板 几条路', '犹豫': '下决心 拍板',
    '竞争': '对手 较量', '对手': '对手 较量', '大厂': '对手 力量', '同行': '对手 竞争者',
    '谈判': '谈判 让步 条件', '收购': '谈判 让步 条件 合作', '合作': '合作 联合 条件',
    '困难': '困难 挫折', '挫折': '挫折 失败 困难', '失败': '失败 挫折 复盘', '低谷': '困难 挫折 低潮',
    '团队': '队伍 组织 干部', '公司': '组织 队伍', '单位': '组织 队伍', '部门': '组织 队伍', '班级': '群众 骨干 中间',
    '同事': '团结 批评 内部', '上级': '上级 领导', '下属': '干部 下级', '老板': '领导 上级',
    '学习': '学习 读书', '读书': '读书 学习 书', '考试': '学习 分数', '学生': '青年 学习',
    '计划': '计划 阶段 目标', '规划': '计划 阶段 长期', '目标': '目标 计划', '期限': '时间 期限 阶段',
    '形势': '形势 趋势 前途', '趋势': '趋势 前途 形势', '行业': '形势 趋势', '前景': '前途 趋势',
    '冲突': '矛盾 斗争 团结', '矛盾': '矛盾 主要矛盾', '批评': '批评 团结', '吵架': '团结 批评 矛盾',
    '复盘': '复盘 总结 错误', '错误': '错误 改正 复盘', '失误': '错误 复盘',
    '说服': '说服 讲话 文章', '沟通': '说服 讲话', '写作': '文章 写法', '演讲': '讲话 说服',
    '动员': '发动 群众 骨干', '推动': '发动 推开 骨干', '带人': '骨干 干部 带动',
    '骄傲': '骄傲 防松懈 变质', '松懈': '松懈 骄傲', '成功': '胜利 骄傲 防变质', '胜利': '胜利 骄傲',
    '害怕': '怕 困难 藐视', '焦虑': '怕 困难', '压力': '困难 压力',
    '调查': '调查 情况 实际', '信息': '情况 调查 报告', '传言': '说法 根据 核实',
}
STOP = set('的了是在和与及或也都就而且但对把被从向到这那其之他她它我你们个些种样么什怎吗呢吧啊')


def bigrams(s):
    s = ''.join(ch for ch in s if '\u4e00' <= ch <= '\u9fff' or ch.isalnum())
    out = []
    for i in range(len(s) - 1):
        a, b = s[i], s[i + 1]
        if a in STOP and b in STOP:
            continue
        out.append(a + b)
    return out


def parse_file(code):
    p = os.path.join(PAT_DIR, f'{code}.md')
    if not os.path.isfile(p):
        return []
    lines = open(p, encoding='utf-8', errors='ignore').read().split('\n')
    pats, cur, field = [], None, None
    head = re.compile(rf'^## ({code}-\d+)\s+(.+)$')
    fld = re.compile(r'^- (' + '|'.join(FIELDS) + r')[：:]\s*(.*)$')
    for i, line in enumerate(lines, 1):
        m = head.match(line)
        if m:
            cur = {'id': m.group(1), 'name': m.group(2).strip(), 'code': code, 'line': i, 'f': {}, 'raw': [line]}
            pats.append(cur)
            field = None
            continue
        if line.startswith('## '):  # 本领域小结等
            cur, field = None, None
            continue
        if cur is None:
            continue
        cur['raw'].append(line)
        m = fld.match(line)
        if m:
            field = m.group(1)
            cur['f'][field] = m.group(2)
        elif field and line.strip():
            cur['f'][field] += '\n' + line
    for pt in pats:
        while pt['raw'] and not pt['raw'][-1].strip():
            pt['raw'].pop()
    return pats


def load(domains):
    allp = []
    for code, _ in DOMAINS:
        if domains and code not in domains:
            continue
        allp += parse_file(code)
    return allp


def score_all(pats, query):
    texts = []
    for pt in pats:
        per = {'名字': set(bigrams(pt['name']))}
        for k in WEIGHT:
            if k != '名字':
                per[k] = set(bigrams(pt['f'].get(k, '')))
        texts.append(per)
    df = Counter()
    for per in texts:
        df.update(set().union(*per.values()))
    n = len(pats)
    q = Counter(bigrams(query))
    res = []
    for pt, per in zip(pats, texts):
        s = 0.0
        for g, c in q.items():
            if g not in df:
                continue
            idf = math.log(1 + n / df[g])
            for k, w in WEIGHT.items():
                if g in per[k]:
                    s += w * idf * min(c, 2)
        res.append((s, pt))
    res.sort(key=lambda x: -x[0])
    return res


def show_pattern(pt, evidence):
    out = []
    skip = False
    for line in pt['raw']:
        if line.startswith('- 跨期证据'):
            skip = not evidence
            if skip:
                out.append('- 跨期证据：（略；加 --evidence 显示。证据行里的锚点构建时都核过）')
                continue
        elif line.startswith('- 来源簇'):
            skip = not evidence  # 来源簇只对维护有用，回答时不需要
            if skip:
                continue
        elif line.startswith('- ') and skip:
            skip = False
        if not skip:
            out.append(line)
    return '\n'.join(out)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser(description='按处境找思维模式')
    ap.add_argument('keywords', nargs='*', help='处境关键词，可以写多组')
    ap.add_argument('--top', type=int, default=8, help='列出前几个候选（默认 8）')
    ap.add_argument('--full', type=int, default=3, help='打印前几个候选的全文（默认 3）')
    ap.add_argument('--domains', help='只在这些领域里找，逗号分隔，如 ZZ,BZ')
    ap.add_argument('--show', nargs='+', help='直接打印指定编号的模式，如 ZZ-44')
    ap.add_argument('--evidence', action='store_true', help='连跨期证据一起打印')
    ap.add_argument('--out', help='把结果另存为 UTF-8 文件')
    a = ap.parse_args()
    if not a.keywords and not a.show:
        ap.error('至少给一个处境关键词，或用 --show 编号')
    lines = []
    say = lines.append
    domains = [d.strip().upper() for d in a.domains.split(',')] if a.domains else None
    pats = load(domains)
    if not pats:
        say(f'没有读到模式文件：{PAT_DIR}')
    elif a.show:
        idx = {pt['id']: pt for pt in pats}
        for pid in a.show:
            pt = idx.get(pid.upper())
            say(show_pattern(pt, a.evidence) if pt else f'找不到 {pid}')
            say('')
    else:
        query = ' '.join(a.keywords)
        extra = [SYNONYMS[k] for k in SYNONYMS if k in query]
        res = score_all(pats, query + ' ' + ' '.join(extra))
        res = [r for r in res if r[0] > 0][:max(a.top, a.full)]
        dn = dict(DOMAINS)
        say(f'处境词：{query}' + (f'（扩展：{" ".join(extra)}）' if extra else ''))
        if not res:
            say('没有找到相关模式。换成更抽象的处境词，或读 references/thinking-patterns.md 的分组。')
        for i, (s, pt) in enumerate(res[:a.top], 1):
            say(f'{i}. {pt["id"]} {pt["name"]}  ［{dn[pt["code"]]}，patterns/{pt["code"]}.md 第 {pt["line"]} 行；得分 {s:.1f}］')
            say(f'   一句话：{pt["f"].get("一句话", "").strip()}')
            say(f'   触发：{pt["f"].get("触发", "").strip()}')
        if res and a.full > 0:
            say('')
            say(f'===== 前 {min(a.full, len(res))} 个模式全文 =====')
            for s, pt in res[:a.full]:
                say('')
                say(show_pattern(pt, a.evidence))
        say('')
        say('提示：只挑一到三个真正合用的模式；不合用的不要硬套。候选里的其他模式可用 --show 编号 查看全文。')
        say('模式只给想法和问法，分析仍按 thinking-engine.md 的主线走完；引用证据行以外的原话，先用 verify_quote.py 核验。')
    text = '\n'.join(lines) + '\n'
    sys.stdout.write(text)
    if a.out:
        with open(a.out, 'w', encoding='utf-8') as fh:
            fh.write(text)


if __name__ == '__main__':
    main()
