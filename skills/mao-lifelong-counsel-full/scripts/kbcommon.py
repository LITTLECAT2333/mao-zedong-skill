"""kb 公共函数：层级定义、文本规范化、文档遍历、原文定位。只用标准库。"""
import os
import re
import sys
from collections import OrderedDict

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KB_DIR = os.path.join(SKILL_DIR, 'kb')
BLACKLIST_MD = os.path.join(SKILL_DIR, 'references', 'quote-blacklist.md')

# 层级代码 -> (kb 下的目录前缀, 说明, 引用时的标注方式)
TIERS = OrderedDict([
    ('A', ('A_选集', '《毛泽东选集》第一至四卷', '官方')),
    ('A5', ('A5_选集第五卷', '《毛泽东选集》第五卷（1977 年版）', '官方（1977 年版，后停止发行）')),
    ('AW', ('AW_文集', '《毛泽东文集》第一至八卷', '官方')),
    ('D', ('D_', '中共中央文献研究室等编：建国以来文稿、军事文集、外交文选、书信选集、早期文稿（多为 OCR 文本）', '官方；OCR 文本个别字可能有误')),
    ('S', ('S_诗词', '毛泽东诗词（网页转录，含注释）', '诗词正文可引；注释不是毛的话')),
    ('Y', ('Y_语录', '《毛主席语录》', '官方摘编（语录是摘句，引用时最好回原篇）')),
    ('AM', ('AM_毛泽东集', '《毛泽东集》正编和补卷（竹内实等编），含原有第一卷、1937 年讲授提纲', '1949 年前原始版本，学术整理')),
    ('B', ('B_谈话与散篇', '谈话记录、批示、外交谈话、讲话稿', '来源不一，注明“据某年某月谈话记录”')),
    ('C', ('C_', '静火版第六、七卷；《毛泽东思想万岁》', '非官方汇编，注明“据非官方汇编，未经官方文本核对”')),
    ('P', ('P_哲学批注集', '《毛泽东哲学批注集》（OCR，批注与原书文字混排）', '命中的可能是原书文字，必须确认是他的批注')),
    ('N', ('N_年谱', '《毛泽东年谱》（编者叙述加摘引）', '只有引号里的摘引可能是他的话，叙述是编者的')),
    ('M', ('M_马恩列', '马恩列原著、艾思奇《大众哲学》', '理论来源，不是毛泽东的话')),
])
MAO_TIERS = ['A', 'A5', 'AW', 'D', 'S', 'Y', 'AM', 'B', 'C', 'P', 'N']
ALL_TIERS = list(TIERS.keys())

# 规范化：去掉注码与标点，只留汉字、字母、数字，再统一常见异体/旧写法（都是等长替换，便于回映原文位置）
FOOTNOTE = re.compile(r'〔\d+〕|\[\d+\]|【\d+】|[⑴-⒇①-⑳]')
# 〇（U+3007）和 ○（U+25CB）在旧文本里都当“零”用，必须保留，否则“一〇七〇万吨”会变成“一七万吨”
KEEP = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\u3007\u25cb0-9A-Za-z]')
VAR = [('○', '〇'), ('那末', '那么'), ('甚么', '什么'), ('象', '像'), ('份', '分'), ('惟', '唯'), ('藉', '借'), ('徧', '遍'),
       ('地', '的'), ('得', '的'), ('底', '的'), ('他', '它'), ('她', '它'), ('哪', '那'), ('澈', '彻'), ('决', '绝'),
       ('馀', '余')]
ELLIPSIS = re.compile(r'…+|\.{3,}|⋯+')


def utf8_stdout():
    """Windows 管道输出默认不是 UTF-8，统一改成 UTF-8，避免中文乱码或编码报错。"""
    for s in (sys.stdout, sys.stderr):
        try:
            s.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass


# 选集篇末是“------”加“注　　释”，文集篇末是单独一行“注释”；之后是编者注释，不是毛泽东的话
NOTES_HEAD = re.compile(r'\n[ \t\u3000]*-{6,}[ \t\u3000]*\n[ \t\u3000]*注[ \t\u3000]*释[ \t\u3000]*\n'
                        r'|\n[ \t\u3000#]*注[ \t\u3000]*释[ \t\u3000]*\n')


NOTES_TIERS = {'A', 'A5', 'AW', 'AM', 'B'}  # 这些层的注释集中在篇末；诗词合集里注释与正文交错，不能这样切


def split_notes(raw, tier=None):
    """把一篇文本拆成 (正文, 编者注释)。只在篇末（全文 30% 以后）出现注释标题时才切分。"""
    if tier is not None and tier not in NOTES_TIERS:
        return raw, ''
    for m in NOTES_HEAD.finditer(raw):
        if m.start() >= len(raw) * 0.3:
            return raw[:m.start()], raw[m.start():]
    return raw, ''


def norm(s):
    s = ''.join(KEEP.findall(FOOTNOTE.sub('', s)))
    for a, b in VAR:
        s = s.replace(a, b)
    return s


def norm_map(raw):
    """返回 (规范化文本, 每个规范化字符在 raw 中的位置)。只在命中的文档上调用。"""
    skip = set()
    for m in FOOTNOTE.finditer(raw):
        skip.update(range(m.start(), m.end()))
    chars, pos = [], []
    for i, ch in enumerate(raw):
        if i in skip or not KEEP.match(ch):
            continue
        chars.append(ch)
        pos.append(i)
    s = ''.join(chars)
    for a, b in VAR:
        s = s.replace(a, b)
    return s, pos


def tier_of(top_dir):
    for code, (prefix, _, _) in TIERS.items():
        if code in ('C', 'D'):
            if top_dir.startswith(prefix):
                return code
        elif code == 'AM' and top_dir == 'AM_毛泽东集补卷':
            return 'AM'
        elif top_dir == prefix:
            return code
    return None


KB_MISSING = ('注意：原文库没有安装或是空的（kb/ 下没有层级目录，安装方法见 kb/README.md）。'
              '装好之前，所有引文一律按「未核到」处理：不加引号，改为转述。')


def kb_ready():
    """kb/ 下至少有一个能识别层级的目录。公开发布的仓库可能不带原文库，这时脚本给出提示，而不是报错退出。"""
    if not os.path.isdir(KB_DIR):
        return False
    return any(os.path.isdir(os.path.join(KB_DIR, d)) and tier_of(d) for d in os.listdir(KB_DIR))


def parse_tiers(arg, default):
    if not arg:
        return list(default)
    if arg.lower() == 'all':
        return list(ALL_TIERS)
    out = [t.strip().upper() for t in arg.split(',') if t.strip()]
    bad = [t for t in out if t not in TIERS]
    if bad:
        raise SystemExit(f'未知层级: {bad}；可用: {",".join(ALL_TIERS)}')
    return out


def iter_docs(tiers, include_notes=False):
    """按层级优先级遍历文档，产出 (tier, kb 内相对路径, 原文)。*.notes.md 是编者注释，默认跳过。"""
    order = {t: i for i, t in enumerate(ALL_TIERS)}
    tops = []
    if not os.path.isdir(KB_DIR):
        return
    for d in sorted(os.listdir(KB_DIR)):
        full = os.path.join(KB_DIR, d)
        t = tier_of(d)
        if os.path.isdir(full) and t in tiers:
            tops.append((order[t], d, t))
    for _, d, t in sorted(tops):
        for dp, dn, fn in os.walk(os.path.join(KB_DIR, d)):
            dn.sort()
            for f in sorted(fn):
                if not f.endswith(('.md', '.txt')):
                    continue
                if f.endswith('.notes.md') and not include_notes:
                    continue
                p = os.path.join(dp, f)
                with open(p, encoding='utf-8', errors='ignore') as fh:
                    yield t, os.path.relpath(p, KB_DIR).replace('\\', '/'), fh.read()


def context(raw, nidx, nlen, width=40):
    """把规范化文本中的命中位置映射回原文，取前后各 width 个字符。"""
    _, pos = norm_map(raw)
    if not pos or nidx >= len(pos):
        return ''
    a = pos[nidx]
    b = pos[min(nidx + nlen - 1, len(pos) - 1)] + 1
    left = raw[max(0, a - width):a].replace('\n', ' ')
    right = raw[b:b + width].replace('\n', ' ')
    return f'…{left}【{raw[a:b]}】{right}…'.replace('\r', '')


def load_blacklist():
    """读取 references/quote-blacklist.md 表格第一列（「」内的句子）及处理意见。"""
    items = []
    if not os.path.exists(BLACKLIST_MD):
        return items
    for line in open(BLACKLIST_MD, encoding='utf-8'):
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        m = re.search(r'「(.+?)」', cells[0]) if cells else None
        if m and len(cells) >= 3:
            items.append((m.group(1), cells[1], cells[2]))
    return items
