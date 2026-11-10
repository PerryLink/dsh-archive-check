#!/usr/bin/env python3
"""README visuals for dsh-archive-check, derived from the shipped pipeline.

Two figures, both read off `rules/archive-check.yaml`, `src/check.ts`,
`src/view.ts` and the register contract in `src/model.ts` -- not from a generic
checker template.

  hero 1440x576 (Pillow, zh/en x light/dark, four WebP files)
      Left column: kicker / wordmark / two value lines / one subtitle / one meta
      line / footer.  Right side: the checker's own object graph, left to right
      and top to bottom -- ① the register (fonds, year, four items, two marked
      cells), ② the seven-rule checklist with its three real states (diff /
      clean / unset), ③ the located finding card and the skipped card.  The
      register row data is the shape `parseMaterial` produces; the finding is
      the exact `found`/`expected`/`fix` wording produced by `checkSequence`
      for 件号 1, 2, 4, 5.

  flow 1100x660 (hand-written SVG, light/dark)
      Grammar: a CLAUSE CROSS-REFERENCE -- seven rules on the left, the five
      documents they cite on the right, eleven clause links (solid = the rule's
      primary `basis`, dashed = `alsoBasis`).  The evidence kind caps severity
      (principle <= warn, local config <= info).  A status rail underneath shows
      one real run: AR-002 / AR-004 diff, AR-005 / AR-006 clean,
      AR-001 / AR-003 / AR-007 unset.  Nothing here is invented: the links,
      clause numbers, kinds, caps and states all come from the rule pack and
      `runCheck`'s output contract.

All labels are measured before they are drawn; a label that would overflow
aborts the run instead of shipping clipped text.

Run once:  python scripts/gen-readme-assets.py
Requires:  Pillow, Windows fonts msyh.ttc / msyhbd.ttc / consola.ttf.
"""
from __future__ import annotations

import math
import os
from html import escape

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "assets")
NAME = "dsh-archive-check"

FONT_FILES = {
    "cjk": r"C:\Windows\Fonts\msyh.ttc",
    "cjk_bold": r"C:\Windows\Fonts\msyhbd.ttc",
    "mono": r"C:\Windows\Fonts\consola.ttf",
    "mono_bold": r"C:\Windows\Fonts\consolab.ttf",
}
for _kind, _path in FONT_FILES.items():
    if not os.path.exists(_path):
        raise SystemExit(f"FATAL: font missing: {_path}")
os.makedirs(OUT, exist_ok=True)

RADIUS = 20
SHADOW = 24

SKIN = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        card="#ffffff", edge="#e6e2ef",
        text="#141419", sub="#4d5261", faint="#8f94a4",
        accent="#4B67B4", pill="#ece7f9", band="#f5f2fb",
        grid="#e7e4f0", mark="#b45309", mark_bg="#fdf3e9",
        ok="#15803d", ok_bg="#eaf6ee",
        shadow=(38, 30, 72), glow=34,
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        card="#1b2231", edge="#2e374b",
        text="#f0f3f9", sub="#a8b1c4", faint="#737b8d",
        accent="#8496f5", pill="#242d42", band="#202839",
        grid="#262f42", mark="#d9a441", mark_bg="#2a2216",
        ok="#3fb950", ok_bg="#16281c",
        shadow=(0, 0, 0), glow=48,
    ),
}


def font(size: int, kind: str = "cjk") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_FILES[kind], size)


def hx(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def gradient(w: int, h: int, top: str, bottom: str) -> Image.Image:
    base = Image.new("RGB", (w, h))
    draw = ImageDraw.Draw(base)
    a, b = hx(top), hx(bottom)
    for y in range(h):
        t = 0.12 * (y / h) + 0.88 * (y / h) ** 1.3
        draw.line([(0, y), (w, y)],
                  fill=tuple(int(p + (q - p) * t) for p, q in zip(a, b)))
    return base


def glow(img: Image.Image, cx: int, cy: int, r: int, color: str,
         alpha: int) -> Image.Image:
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    rgb = hx(color)
    for i in range(10, 0, -1):
        rr = r * i / 10
        d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr],
                  fill=rgb + (int(alpha * (1 - i / 11)),))
    return Image.alpha_composite(img.convert("RGBA"),
                                 layer.filter(ImageFilter.GaussianBlur(26))
                                 ).convert("RGB")


def card(img: Image.Image, box: tuple[int, int, int, int], s: dict,
         radius: int = RADIUS, shadow: int = SHADOW,
         fill: str | None = None, edge: str | None = None) -> Image.Image:
    x0, y0, x1, y1 = box
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    for i in range(shadow, 0, -2):
        sd.rounded_rectangle([x0 - i // 6, y0 + i // 2, x1 + i // 6, y1 + i],
                             radius=radius + i // 6,
                             fill=s["shadow"] + (int(10 * (1 - i / shadow)),))
    base = Image.alpha_composite(img.convert("RGBA"),
                                 sh.filter(ImageFilter.GaussianBlur(11)))
    d = ImageDraw.Draw(base)
    d.rounded_rectangle(box, radius=radius, fill=hx(fill or s["card"]),
                        outline=hx(edge or s["edge"]), width=2)
    return base.convert("RGB")


_MEASURE = ImageDraw.Draw(Image.new("RGB", (8, 8)))


def measure(text: str, size: int, kind: str) -> float:
    return _MEASURE.textlength(text, font=font(size, kind))


def require_w(text: str, size: int, kind: str, max_w: float, what: str) -> None:
    got = measure(text, size, kind)
    if got > max_w + 0.4:
        raise SystemExit(f"FATAL: {what} overflows: {text!r} needs "
                         f"{got:.1f}px > {max_w:.0f}px")


def fit(text: str, kind: str, max_w: float, start: int, minimum: int) -> int:
    size = start
    while size > minimum:
        if measure(text, size, kind) <= max_w:
            return size
        size -= 1
    raise SystemExit(f"FATAL: text does not fit {max_w}px at >= {minimum}px: "
                     f"{text!r}")


def fit_lines(lines: list[str], kind: str, max_w: float, start: int,
              minimum: int) -> int:
    return min(fit(t, kind, max_w, start, minimum) for t in lines)


def pill(img: Image.Image, xy: tuple[int, int], text: str, s: dict,
         size: int = 16, fg: str | None = None, bg: str | None = None,
         kind: str = "cjk_bold") -> int:
    d = ImageDraw.Draw(img)
    f = font(size, kind)
    w = d.textlength(text, font=f)
    x, y = xy
    h = size + 20
    d.rounded_rectangle([x, y, x + w + 30, y + h], radius=h // 2,
                        fill=hx(bg or s["pill"]))
    d.text((x + 15, y + h / 2), text, font=f, fill=hx(fg or s["accent"]),
           anchor="lm")
    return int(x + w + 30)


def chip_right(img: Image.Image, right: int, y: int, text: str, fg: str,
               bg: str, size: int = 10, height: int = 20,
               kind: str = "cjk_bold") -> int:
    d = ImageDraw.Draw(img)
    w = d.textlength(text, font=font(size, kind)) + 18
    x = right - w
    d.rounded_rectangle([x, y, right, y + height], radius=height / 2,
                        fill=hx(bg))
    d.text((x + 9, y + height / 2), text, font=font(size, kind),
           fill=hx(fg), anchor="lm")
    return int(x)


def badge(img: Image.Image, cx: int, cy: int, text: str, s: dict,
          size: int = 10) -> None:
    d = ImageDraw.Draw(img)
    d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=hx(s["pill"]))
    d.text((cx, cy), text, font=font(size, "cjk_bold"), fill=hx(s["accent"]),
           anchor="mm")


def dash_round_rect(d: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
                    color: str, radius: int = 8, width: int = 2) -> None:
    x0, y0, x1, y1 = box
    for xa, xb in ((x0 + radius, x1 - radius),):
        for yy in (y0, y1):
            for x in range(int(xa), int(xb), 10):
                d.line([(x, yy), (min(x + 6, xb), yy)], fill=hx(color),
                       width=width)
    for y in range(int(y0 + radius), int(y1 - radius), 10):
        for xx in (x0, x1):
            d.line([(xx, y), (xx, min(y + 6, y1 - radius))], fill=hx(color),
                   width=width)
    d.arc([x0, y0, x0 + 2 * radius, y0 + 2 * radius], 180, 270,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y0, x1, y0 + 2 * radius], 270, 360,
          fill=hx(color), width=width)
    d.arc([x0, y1 - 2 * radius, x0 + 2 * radius, y1], 90, 180,
          fill=hx(color), width=width)
    d.arc([x1 - 2 * radius, y1 - 2 * radius, x1, y1], 0, 90,
          fill=hx(color), width=width)


# --------------------------------------------------------------------------- hero
HERO = {
    "zh": dict(
        kicker="DeepSeek Harness 插件 · 核查器",
        value=["七条规则，逐行核对登记表", "每条差异落到行号与栏名"],
        sub="只列字面差异，不下合规结论，绝不改动原件。",
        meta="archive_check · AR-001…AR-007 · issues + skipped",
        foot="Apache-2.0 · 只读 · 不联网 · 不调用模型",
        doc_title="归档登记表 · 只读",
        doc_meta="全宗 某单位 · 年度 2026 · 4 条",
        scroll_chip="JSON / YAML",
        headers=["档号", "题名", "保管期限", "件号", "形成日期"],
        rows=[
            ["A-2026-001", "通知", "永久", "1", "2026-03-15"],
            ["A-2026-001", "报告", "定期30年", "2", "2026-04-01"],
            ["A-2026-003", "函", "永久", "4", "2026-05-06"],
            ["A-2026-004", "批复", "定期10年", "5", "2026-06-11"],
        ],
        notes=["① 档号重复：第 2 行与第 1 行相同",
               "② 件号 1、2、4、5 中缺 3"],
        check_title="规则清单 · 7 条",
        check_sub="差异 / 无差异 / 未配置",
        rules=[
            ("AR-001", "著录栏目", "unset"),
            ("AR-002", "档号唯一", "diff"),
            ("AR-003", "期限用词", "unset"),
            ("AR-004", "件号连续", "diff"),
            ("AR-005", "日期年度", "clean"),
            ("AR-006", "表头声明", "clean"),
            ("AR-007", "移交期限", "unset"),
        ],
        issue_title="判定卡 · AR-004",
        issue_locator="第 3 行 · 件号",
        issue_found="件号范围 1~5 中缺 1 个号：3",
        issue_expected="同一盒内件号应连续",
        issue_fix="核对是否漏登记；件号不连续本身不构成问题，需人工确认",
        skip_title="未执行清单 · skipped",
        skip_lines=["AR-001 · requiredFields 未配置",
                    "AR-003 · retentionTerms 未配置",
                    "AR-007 · transferAfterYears 0"],
        strip_left="空 issues ≠ 没问题",
        strip_mid="每条差异带 行号 + 栏名 + 依据",
        strip_right="结论留给审核人",
        status_words={"diff": "差异", "clean": "无差异", "unset": "未配置"},
    ),
    "en": dict(
        kicker="DeepSeek Harness plugin · checker",
        value=["Seven rules, one register,", "each difference lands on a cell"],
        sub="Literal differences only — no compliance verdict.",
        meta="archive_check · AR-001…AR-007 · issues + skipped",
        foot="Apache-2.0 · read-only · no network · no model call",
        doc_title="Filing register · read-only",
        doc_meta="fonds Some Unit · year 2026 · 4 items",
        scroll_chip="JSON / YAML",
        headers=["No.", "Title", "Retention", "Item", "Date"],
        rows=[
            ["A-2026-001", "Notice", "Permanent", "1", "2026-03-15"],
            ["A-2026-001", "Report", "30 years", "2", "2026-04-01"],
            ["A-2026-003", "Letter", "Permanent", "4", "2026-05-06"],
            ["A-2026-004", "Reply", "10 years", "5", "2026-06-11"],
        ],
        notes=["① archive no. repeats on row 2",
               "② item nos. 1, 2, 4, 5 → 3 is missing"],
        check_title="Rule checklist · 7",
        check_sub="diff / clean / unset",
        rules=[
            ("AR-001", "required fields", "unset"),
            ("AR-002", "archive no.", "diff"),
            ("AR-003", "retention term", "unset"),
            ("AR-004", "item numbers", "diff"),
            ("AR-005", "date vs year", "clean"),
            ("AR-006", "register header", "clean"),
            ("AR-007", "transfer due", "unset"),
        ],
        issue_title="Finding · AR-004",
        issue_locator="row 3 · item no.",
        issue_found="item numbers 1~5: 3 is missing",
        issue_expected="item numbers run without gaps",
        issue_fix="check for an unregistered item; a gap is not itself a defect",
        skip_title="Not run · skipped",
        skip_lines=["AR-001 · requiredFields unset",
                    "AR-003 · retentionTerms unset",
                    "AR-007 · transferAfterYears 0"],
        strip_left="empty issues ≠ all clear",
        strip_mid="row + column + cited clause",
        strip_right="the reviewer decides",
        status_words={"diff": "diff", "clean": "clean", "unset": "unset"},
    ),
}


def hero(lang: str, skin: str) -> None:
    s = SKIN[skin]
    h = HERO[lang]
    W, H = 1440, 576
    img = gradient(W, H, s["bg_from"], s["bg_to"])
    img = glow(img, 1120, 96, 400, s["accent"], s["glow"])
    img = glow(img, 180, 570, 300, s["accent"], max(8, s["glow"] // 3))
    d = ImageDraw.Draw(img)
    m = 56
    col_w = 556

    # ---- left column --------------------------------------------------------
    pill(img, (m, 72), h["kicker"], s, size=16)
    d = ImageDraw.Draw(img)

    title_size = fit(NAME, "mono_bold", col_w, 60, 50)
    d.text((m - 1, 132), NAME, font=font(title_size, "mono_bold"),
           fill=hx(s["text"]))
    require_w(NAME, title_size, "mono_bold", col_w, "hero title")

    value_size = fit_lines(h["value"], "cjk_bold", col_w,
                           38 if lang == "zh" else 36, 32)
    for i, line in enumerate(h["value"]):
        d.text((m, 234 + i * 54), line, font=font(value_size, "cjk_bold"),
               fill=hx(s["text"]))
        require_w(line, value_size, "cjk_bold", col_w, "hero value line")

    require_w(h["sub"], 22, "cjk", col_w, "hero subtitle")
    d.text((m, 352), h["sub"], font=font(22, "cjk"), fill=hx(s["sub"]))

    require_w(h["meta"], 19, "cjk", col_w, "hero meta")
    d.text((m + 1, 406), h["meta"], font=font(19, "cjk"), fill=hx(s["faint"]))

    d.line([m + 1, 458, m + col_w - 4, 458], fill=hx(s["grid"]), width=2)
    require_w(h["foot"], 16, "cjk", col_w, "hero footer")
    d.text((m + 1, 476), h["foot"], font=font(16, "cjk"), fill=hx(s["faint"]))

    # ---- ① register ---------------------------------------------------------
    img = card(img, (640, 48, 1056, 348), s, radius=20, shadow=26)
    d = ImageDraw.Draw(img)
    badge(img, 660, 66, "①", s)
    d = ImageDraw.Draw(img)
    d.text((678, 72), h["doc_title"], font=font(15, "cjk_bold"),
           fill=hx(s["text"]))
    require_w(h["doc_title"], 15, "cjk_bold", 260, "doc title")
    chip_right(img, 1034, 56, h["scroll_chip"], s["accent"], s["pill"], size=10.5)
    d = ImageDraw.Draw(img)
    require_w(h["doc_meta"], 12, "cjk", 360, "doc meta")
    d.text((660, 94), h["doc_meta"], font=font(12, "cjk"), fill=hx(s["sub"]))

    x0, x1 = 660, 1036
    widths = [108, 58, 100, 40, 74]
    xs, acc = [], x0
    for w in widths:
        xs.append(acc)
        acc += w
    d.rounded_rectangle([x0 - 7, 108, x1 + 7, 132], radius=8, fill=hx(s["band"]))
    for i, head in enumerate(h["headers"]):
        require_w(head, 11, "cjk_bold", widths[i] - 8, "table header")
        d.text((xs[i] + 7, 122), head, font=font(11, "cjk_bold"),
               fill=hx(s["sub"]))

    row_h = 38
    marked = {(1, 0), (2, 3)}
    for r, col in marked:  # fills first, so the cell value stays readable
        ry = 134 + r * row_h
        box = (xs[col] - 2, ry + 4, xs[col] + widths[col] - 5, ry + row_h - 4)
        d.rounded_rectangle(box, radius=8, fill=hx(s["mark_bg"]))
    for r, row in enumerate(h["rows"]):
        ry = 134 + r * row_h
        for i, value in enumerate(row):
            is_date = value.startswith("2026-")
            is_ref = i == 0
            cell_kind = "mono" if (is_date or is_ref or i == 3) else "cjk"
            cell_size = 10.5 if is_date else 12
            require_w(value, cell_size, cell_kind, widths[i] - 10, "table cell")
            d.text((xs[i] + 7, ry + 24), value, font=font(cell_size, cell_kind),
                   fill=hx(s["text"]))
        if r < len(h["rows"]) - 1:
            d.line([x0, ry + row_h, x1, ry + row_h], fill=hx(s["grid"]), width=1)

    # the two marked cells: duplicate 档号 (row 2) and missing 件号 (row 3)
    for r, col in marked:
        ry = 134 + r * row_h
        box = (xs[col] - 2, ry + 4, xs[col] + widths[col] - 5, ry + row_h - 4)
        dash_round_rect(d, box, s["mark"], radius=8, width=2)

    for i, note in enumerate(h["notes"]):
        require_w(note, 11, "cjk", 370, "register note")
        d.text((660, 304 + i * 19), note, font=font(11, "cjk"),
               fill=hx(s["mark"]))

    # ---- ② checklist --------------------------------------------------------
    img = card(img, (1072, 48, 1384, 348), s, radius=20, shadow=26)
    d = ImageDraw.Draw(img)
    badge(img, 1092, 66, "②", s)
    d = ImageDraw.Draw(img)
    d.text((1110, 72), h["check_title"], font=font(15, "cjk_bold"),
           fill=hx(s["text"]))
    require_w(h["check_title"], 15, "cjk_bold", 200, "checklist title")
    chip_right(img, 1368, 56, "7", s["accent"], s["pill"], size=10.5)
    d = ImageDraw.Draw(img)
    d.text((1092, 96), h["check_sub"], font=font(11, "cjk"), fill=hx(s["faint"]))
    require_w(h["check_sub"], 11, "cjk", 270, "checklist sub")

    status_style = {
        "diff": ("mark", "mark_bg"),
        "clean": ("ok", "ok_bg"),
        "unset": ("faint", "band"),
    }
    for i, (rid, label, state) in enumerate(h["rules"]):
        cy = 124 + i * 31
        if i < len(h["rules"]) - 1:
            d.line([1092, cy + 16, 1368, cy + 16], fill=hx(s["grid"]), width=1)
        d.text((1092, cy), rid, font=font(12, "mono_bold"), fill=hx(s["text"]),
               anchor="lm")
        d.text((1150, cy), label, font=font(12, "cjk"), fill=hx(s["sub"]),
               anchor="lm")
        require_w(label, 12, "cjk", 160, "rule checklist label")
        fg, bg = status_style[state]
        word = h["status_words"][state]
        chip_right(img, 1368, cy - 10, word, s[fg], s[bg], size=11)
        d = ImageDraw.Draw(img)

    # ---- ③ finding ----------------------------------------------------------
    img = card(img, (640, 364, 1056, 484), s, radius=18, shadow=20)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([648, 374, 652, 474], radius=2, fill=hx(s["mark"]))
    badge(img, 670, 382, "③", s)
    d = ImageDraw.Draw(img)
    d.text((688, 387), h["issue_title"], font=font(13.5, "cjk_bold"),
           fill=hx(s["text"]))
    require_w(h["issue_title"], 13.5, "cjk_bold", 150, "issue title")
    chip_right(img, 900, 375, "warn", s["mark"], s["mark_bg"], size=10)
    d = ImageDraw.Draw(img)
    require_w(h["issue_locator"], 11, "cjk", 120, "issue locator")
    d.text((1036, 388), h["issue_locator"], font=font(11, "cjk"),
           fill=hx(s["faint"]), anchor="ra")
    require_w(h["issue_found"], 13, "cjk", 360, "issue found")
    d.text((688, 414), h["issue_found"], font=font(13, "cjk"),
           fill=hx(s["text"]))
    require_w(h["issue_expected"], 12, "cjk", 360, "issue expected")
    d.text((688, 435), h["issue_expected"], font=font(12, "cjk"),
           fill=hx(s["sub"]))
    require_w(h["issue_fix"], 11.5, "cjk", 360, "issue fix")
    d.text((688, 454), h["issue_fix"], font=font(11.5, "cjk"),
           fill=hx(s["sub"]))
    basis = ("依据 DA/T 22—2015 5.4.3 e)" if lang == "zh"
             else "basis DA/T 22—2015 5.4.3 e)")
    require_w(basis, 11, "cjk", 360, "issue basis")
    d.text((688, 471), basis, font=font(11, "cjk"), fill=hx(s["faint"]))

    # ---- ③ skipped ----------------------------------------------------------
    img = card(img, (1072, 364, 1384, 484), s, radius=18, shadow=20)
    d = ImageDraw.Draw(img)
    badge(img, 1092, 382, "③", s)
    d = ImageDraw.Draw(img)
    d.text((1110, 387), h["skip_title"], font=font(13.5, "cjk_bold"),
           fill=hx(s["text"]))
    require_w(h["skip_title"], 13.5, "cjk_bold", 250, "skip title")
    for i, line in enumerate(h["skip_lines"]):
        require_w(line, 11, "cjk", 288, "skip line")
        d.text((1092, 413 + i * 21), line, font=font(11, "cjk"),
               fill=hx(s["sub"]))
    d.text((1092, 470), "原因逐条写明" if lang == "zh" else "reason recorded",
           font=font(10.5, "cjk"), fill=hx(s["faint"]))

    # ---- report strip -------------------------------------------------------
    img = card(img, (640, 500, 1384, 548), s, radius=18, shadow=16)
    d = ImageDraw.Draw(img)
    d.text((660, 524), h["strip_left"], font=font(14, "cjk_bold"),
           fill=hx(s["text"]), anchor="lm")
    require_w(h["strip_left"], 14, "cjk_bold", 240, "strip left")
    left_w = measure(h["strip_left"], 14, "cjk_bold")
    d.text((660 + left_w + 18, 524), h["strip_mid"], font=font(12, "cjk"),
           fill=hx(s["sub"]), anchor="lm")
    require_w(h["strip_mid"], 12, "cjk", 300, "strip mid")
    d.text((1364, 524), h["strip_right"], font=font(13, "cjk_bold"),
           fill=hx(s["ok"]), anchor="rm")
    require_w(h["strip_right"], 13, "cjk_bold", 180, "strip right")

    name = f"{NAME}-hero-{lang}-{skin}.webp"
    img.save(os.path.join(OUT, name), "WEBP", quality=92, method=6)
    print(f"wrote {name} ({W}x{H})")


# --------------------------------------------------------------------------- flow
FLOW = {
    "light": dict(
        bg_from="#f9f6fd", bg_to="#e4eaf8",
        panel="#ffffff", card="#ffffff", edge="#e6e2ef",
        band="#f5f2fb", pill="#ece7f9", text="#141419", sub="#4d5261",
        faint="#8f94a4",
        accent="#4B67B4", accent2="#16a34a",
        warn="#b45309", warn_bg="#fdf3e9",
        ok="#15803d", ok_bg="#eaf6ee",
        rule="#e7e4f0", shadow="#2b2440", shadow_op="0.13",
        dot="#cfc8e2", dot_op="0.55",
    ),
    "dark": dict(
        bg_from="#131a2a", bg_to="#0c1016",
        panel="#1b2231", card="#1b2231", edge="#2e374b",
        band="#202839", pill="#242d42", text="#f0f3f9", sub="#a8b1c4",
        faint="#737b8d",
        accent="#8496f5", accent2="#3fb950",
        warn="#d9a441", warn_bg="#2a2216",
        ok="#3fb950", ok_bg="#16281c",
        rule="#2b3348", shadow="#000000", shadow_op="0.50",
        dot="#2a3346", dot_op="0.55",
    ),
}

FONT_CSS_SANS = ("'Microsoft YaHei','Segoe UI','PingFang SC',"
                 "'Noto Sans CJK SC',sans-serif")
FONT_CSS_MONO = ("Consolas,'Microsoft YaHei',ui-monospace,monospace")

RULES = [
    # id, title, field read, primary clause, kind, severity cap
    ("AR-001", "required description fields", "requiredFields", "5.5.2",
     "local config", "info"),
    ("AR-002", "archive number unique", "reference", "5.4.1",
     "principle", "warn"),
    ("AR-003", "retention term in schedule", "retention", "art. 6",
     "local config", "info"),
    ("AR-004", "item numbers unique, gap-free", "sequence", "5.4.3 e)",
     "principle", "warn"),
    ("AR-005", "date parses, year matches", "formedAt", "5.3.1",
     "principle", "warn"),
    ("AR-006", "register declares fonds + year", "fonds · year", "5.2.2",
     "principle", "warn"),
    ("AR-007", "transfer deadline passed", "transferAfterYears", "art. 20(2)",
     "local config", "info"),
]

DOCS = [
    ("DAT", "DA/T 22—2015", "arrangement rules",
     ["5.2.2 · 5.3.1 · 5.4.1", "5.4.3 e) · 5.5.2"], 80),
    ("O772", "State Council Order No. 772", "implementation regs",
     ["19(1) · 19(2) · 20(2)"], 70),
    ("O8", "Order No. 8", "agency schedules", ["art. 6"], 52),
    ("O10", "Order No. 10", "enterprise schedules", ["art. 11"], 52),
    ("LAW", "Archives Law", "2020 revision", ["art. 15"], 52),
]

STATES = [
    ("AR-001", "unset"),
    ("AR-002", "diff"),
    ("AR-003", "unset"),
    ("AR-004", "diff"),
    ("AR-005", "clean"),
    ("AR-006", "clean"),
    ("AR-007", "unset"),
]


class Svg:
    """Small SVG writer that measures every label before it is emitted."""

    def __init__(self) -> None:
        self.parts: list[str] = []
        self.overflows: list[str] = []

    def add(self, markup: str) -> None:
        self.parts.append(markup)

    def _w(self, content: str, size: float, kind: str,
           tracking: float | None = None) -> float:
        path = FONT_FILES[kind]
        if not content.isascii():
            path = FONT_FILES["cjk_bold" if "bold" in kind else "cjk"]
        got = _MEASURE.textlength(content, font=ImageFont.truetype(path, size))
        if tracking:
            got += tracking * max(len(content) - 1, 0)
        return got

    def text(self, x: float, y: float, content: str, size: float, fill: str, *,
             anchor: str = "start", weight: int | None = None,
             mono: bool = False, max_w: float | None = None,
             opacity: float | None = None, tracking: float | None = None) -> None:
        kind = ("mono" if mono else "cjk") + ("_bold" if weight else "")
        if mono and weight:
            kind = "mono_bold"
        if max_w is not None:
            got = self._w(content, size, kind, tracking)
            if got > max_w + 0.4:
                self.overflows.append(f"{content!r} needs {got:.1f}px > "
                                      f"{max_w:.0f}px")
        family = FONT_CSS_MONO if mono else FONT_CSS_SANS
        attrs = [f'x="{x}"', f'y="{y}"', f'fill="{fill}"',
                 f'font-family="{family}"', f'font-size="{size}"']
        if anchor != "start":
            attrs.append(f'text-anchor="{anchor}"')
        if weight:
            attrs.append(f'font-weight="{weight}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        if tracking:
            attrs.append(f'letter-spacing="{tracking}"')
        self.add(f'<text {" ".join(attrs)}>{escape(content)}</text>')

    def rect(self, x: float, y: float, w: float, h: float, *, fill: str,
             rx: float = 0, stroke: str | None = None, sw: float = 1.5,
             shadow: bool = False, dash: str | None = None,
             opacity: float | None = None) -> None:
        attrs = [f'x="{x}"', f'y="{y}"', f'width="{w}"', f'height="{h}"']
        if rx:
            attrs.append(f'rx="{rx}"')
        attrs.append(f'fill="{fill}"')
        if stroke:
            attrs.append(f'stroke="{stroke}"')
            attrs.append(f'stroke-width="{sw}"')
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        if shadow:
            attrs.append('filter="url(#soft)"')
        self.add(f'<rect {" ".join(attrs)}/>')

    def line(self, x1: float, y1: float, x2: float, y2: float, *, stroke: str,
             sw: float = 1.5, dash: str | None = None,
             marker: str | None = None, opacity: float | None = None) -> None:
        attrs = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
                 f'stroke="{stroke}"', f'stroke-width="{sw}"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<line {" ".join(attrs)}/>')

    def path(self, d: str, *, stroke: str, sw: float = 1.5,
             marker: str | None = None, dash: str | None = None,
             opacity: float | None = None) -> None:
        attrs = [f'd="{d}"', 'fill="none"', f'stroke="{stroke}"',
                 f'stroke-width="{sw}"', 'stroke-linejoin="round"']
        if dash:
            attrs.append(f'stroke-dasharray="{dash}"')
        if marker:
            attrs.append(f'marker-end="url(#{marker})"')
        if opacity is not None:
            attrs.append(f'opacity="{opacity}"')
        self.add(f'<path {" ".join(attrs)}/>')

    def circle(self, cx: float, cy: float, r: float, *, fill: str,
               stroke: str | None = None, sw: float = 1.5) -> None:
        attrs = [f'cx="{cx}"', f'cy="{cy}"', f'r="{r}"', f'fill="{fill}"']
        if stroke:
            attrs.append(f'stroke="{stroke}"')
            attrs.append(f'stroke-width="{sw}"')
        self.add(f'<circle {" ".join(attrs)}/>')

    def chip_right(self, right: float, y: float, label: str, fg: str, bg: str,
                   *, size: float = 11, pad: float = 9, height: float = 22,
                   mono: bool = False, weight: int | None = None,
                   stroke: str | None = None, dash: str | None = None) -> float:
        kind = "mono" if mono else "cjk"
        if weight:
            kind += "_bold"
        w = self._w(label, size, kind) + pad * 2
        x = right - w
        self.rect(x, y, w, height, fill=bg, rx=height / 2, stroke=stroke,
                  sw=1.2, dash=dash)
        self.text(x + pad, y + height / 2 + size * 0.34, label, size, fg,
                  weight=weight, mono=mono)
        return x

    def svg(self, w: int, h: int, title: str, desc: str) -> str:
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" '
                f'height="{h}" viewBox="0 0 {w} {h}" role="img" '
                f'aria-labelledby="title desc">')
        return "\n".join([head, f'<title id="title">{escape(title)}</title>',
                          f'<desc id="desc">{escape(desc)}</desc>',
                          *self.parts, "</svg>"]) + "\n"


def flow_svg(skin: str) -> str:
    s = FLOW[skin]
    W, H = 1100, 660
    v = Svg()

    v.add("<defs>")
    v.add(f'<linearGradient id="bg" x1="0" y1="0" x2="0.2" y2="1">'
          f'<stop offset="0" stop-color="{s["bg_from"]}"/>'
          f'<stop offset="1" stop-color="{s["bg_to"]}"/>'
          f'</linearGradient>')
    v.add(f'<filter id="soft" x="-30%" y="-30%" width="160%" height="180%">'
          f'<feDropShadow dx="0" dy="8" stdDeviation="10" '
          f'flood-color="{s["shadow"]}" '
          f'flood-opacity="{s["shadow_op"]}"/></filter>')
    v.add('<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" '
          'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
          f'<path d="M0 0 L10 5 L0 10 z" fill="{s["accent"]}"/></marker>')
    v.add(f'<pattern id="dots" width="24" height="24" '
          f'patternUnits="userSpaceOnUse">'
          f'<circle cx="1.2" cy="1.2" r="1.2" fill="{s["dot"]}"/>'
          f'</pattern>')
    v.add("</defs>")

    v.rect(0, 0, W, H, fill=f'url(#bg)')
    v.rect(0, 0, W, H, fill="url(#dots)", opacity=s["dot_op"])

    # ---- header -------------------------------------------------------------
    v.text(44, 58, NAME, 30, s["text"], weight=700, mono=True, max_w=560)
    v.text(44, 86,
           "Seven rules, eleven verbatim clauses, five documents; the evidence "
           "kind caps the severity.", 14.5, s["sub"], max_w=760)
    v.chip_right(1056, 32, "rules/archive-check.yaml · v2026.1", s["accent"],
                 s["pill"], size=11.5, pad=12, height=28, mono=True)

    v.text(44, 112, "IN · register rows[] · fonds · year · JSON / YAML",
           11, s["faint"], mono=True, max_w=520)
    v.text(1056, 112, "OUT · issues[] + skipped[]", 11, s["faint"],
           mono=True, anchor="end", max_w=260)
    v.line(44, 126, 1056, 126, stroke=s["rule"], sw=1, opacity=0.75)

    # ---- rule panel ---------------------------------------------------------
    v.text(44, 150, "7 RULES · WHAT EACH ONE READS", 11, s["faint"],
           weight=700, tracking=1.1, max_w=480)
    v.text(800, 150, "5 DOCUMENTS · 11 CITED CLAUSES", 11, s["faint"],
           weight=700, tracking=1.1, max_w=256)
    v.rect(44, 160, 656, 350, fill=s["panel"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)

    row_centers = [193, 239, 285, 331, 377, 423, 469]
    for i, (rid, title, field, clause, kind, cap) in enumerate(RULES):
        cy = row_centers[i]
        top = cy - 23
        if i % 2 == 1:
            v.rect(56, top, 632, 46, fill=s["band"], rx=8, opacity=0.55)
        if i < len(RULES) - 1:
            v.line(56, cy + 23, 688, cy + 23, stroke=s["rule"], sw=1)

        v.text(64, cy + 4.5, rid, 13, s["text"], weight=700, mono=True)
        v.text(126, cy - 2, title, 13, s["text"], weight=700, max_w=276)
        v.text(126, cy + 13.5, field, 11, s["faint"], mono=True, max_w=276)

        v.rect(414, cy - 11, 88, 22, fill=s["band"], rx=11)
        v.text(458, cy + 4, clause, 11, s["sub"], mono=True, anchor="middle",
               max_w=80)

        cap_color = s["warn"] if cap == "warn" else s["accent"]
        v.text(514, cy - 1, kind, 11, s["faint"], max_w=166)
        v.text(514, cy + 15, f"≤ {cap}", 11.5, cap_color, weight=700,
               mono=True, max_w=166)
        v.circle(700, cy, 4.5, fill=s["accent"], stroke=s["panel"], sw=2)

    # ---- documents ----------------------------------------------------------
    doc_tops = [166, 254, 332, 392, 452]
    for i, (key, name, sub, clauses, height) in enumerate(DOCS):
        top = doc_tops[i]
        v.rect(800, top, 256, height, fill=s["card"], rx=18,
               stroke=s["edge"], sw=1.5, shadow=True)
        v.rect(800, top + 8, 3, height - 16, fill=s["accent"], rx=1.5)
        compact = height <= 52
        v.text(816, top + (19 if compact else 20), name, 13, s["text"],
               weight=700, max_w=228)
        if compact:
            v.text(816, top + 38, f"{sub} · {clauses[0]}", 11, s["faint"],
                   max_w=228)
        else:
            v.text(816, top + 35, sub, 11, s["faint"], max_w=228)
            for j, clause in enumerate(clauses):
                v.text(816, top + 52 + j * 15, clause, 11, s["sub"],
                       mono=True, max_w=228)

    # ---- clause links -------------------------------------------------------
    # (rule index, document key, document entry y, primary?)
    links = [
        (0, "DAT", 184, True), (0, "O772", 270, False),
        (1, "DAT", 196, True),
        (2, "O8", 358, True), (2, "O772", 288, False), (2, "O10", 418, False),
        (3, "DAT", 208, True),
        (4, "DAT", 220, True),
        (5, "DAT", 232, True),
        (6, "O772", 306, True), (6, "LAW", 478, False),
    ]
    lanes = [712 + i * 7 for i in range(len(links))]
    for i, (rule_i, doc_key, entry_y, primary) in enumerate(links):
        y0 = row_centers[rule_i]
        lane = lanes[i]
        path = f"M700 {y0} H{lane} V{entry_y} H797"
        v.path(path, stroke=s["accent"], sw=1.5 if primary else 1.1,
               marker="arr", dash=None if primary else "4 4",
               opacity=0.82 if primary else 0.45)

    # ---- one run ------------------------------------------------------------
    v.rect(44, 524, 1012, 70, fill=s["panel"], rx=18, stroke=s["edge"],
           sw=1.5, shadow=True)
    v.text(60, 550, "runCheck()", 11.5, s["accent"], weight=700, mono=True,
           max_w=90)
    state_style = {
        "diff": (s["warn"], s["warn_bg"], None),
        "clean": (s["ok"], s["ok_bg"], None),
        "unset": (s["faint"], s["band"], "4 3"),
    }
    for i, (rid, state) in enumerate(STATES):
        x = 152 + i * 126
        fg, bg, dash = state_style[state]
        v.rect(x, 534, 120, 30, fill=bg, rx=15, stroke=fg, sw=1.2, dash=dash)
        v.text(x + 10, 553, rid, 11, s["text"], weight=700, mono=True,
               max_w=48)
        v.text(x + 110, 553, state, 11, fg, anchor="end", mono=True,
               max_w=54)

    v.text(60, 582,
           "issues[] 2 · locator(row, column) · found / expected / fix · basis",
           11, s["sub"], max_w=690)
    v.text(1056, 582, "skipped[] · rule + reason", 11, s["faint"],
           anchor="end", max_w=240)

    # ---- footer -------------------------------------------------------------
    v.line(44, 610, 1056, 610, stroke=s["rule"], sw=1)
    v.text(44, 630,
           "solid = primary basis · dashed = alsoBasis · excerpt verbatim "
           "(≥ 8 chars) · severity follows the evidence", 11, s["sub"],
           max_w=1012)
    v.text(44, 648,
           "no adjudication · row + column + clause on every issue · original "
           "never modified · rulesFile / disabledRules / onlyRules / timeoutMs",
           11, s["faint"], max_w=1012)

    if v.overflows:
        raise SystemExit("FATAL: SVG label overflow:\n  " +
                         "\n  ".join(v.overflows))
    return v.svg(
        W, H,
        "dsh-archive-check clause cross-reference",
        "Seven archive checks mapped to the eleven verbatim clauses they cite "
        "in five documents. Solid links are primary bases, dashed links are "
        "alsoBasis. Evidence kind caps severity: principle at warn, local "
        "config at info. One run shows AR-002 and AR-004 differences, AR-005 "
        "and AR-006 clean, AR-001, AR-003 and AR-007 unset; the report lists "
        "issues with row, column and clause, and skipped rules with reasons.",
    )


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    for skin in ("light", "dark"):
        for lang in ("zh", "en"):
            hero(lang, skin)
        name = f"{NAME}-flow-v5-{skin}.svg"
        with open(os.path.join(OUT, name), "w", encoding="utf-8",
                  newline="\n") as fh:
            fh.write(flow_svg(skin))
        print(f"wrote {name} (1100x660)")


if __name__ == "__main__":
    main()
