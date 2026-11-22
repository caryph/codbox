#!/usr/bin/env python3
"""Contrast sanity check for theme blocks in editor/ColorConfig.ts.

Usage: python3 tools/check_theme_contrast.py [theme-name ...]
Prints WCAG contrast ratios for the pairs that matter in the track view and UI.
Flags anything under 2:1 (channel colors are decorative-ish, but under ~2 the
notes disappear into the row background).
"""
import re
import sys

SRC = "editor/ColorConfig.ts"

# pairs to check: (label, var-with-channel-slot-templates)
PAIRS = [
    ("text on page",        ("--primary-text", "--page-margin")),
    ("text on editor bg",   ("--primary-text", "--editor-background")),
    ("text on widget",      ("--primary-text", "--ui-widget-background")),
    ("secondary text",      ("--secondary-text", "--editor-background")),
    ("link accent",         ("--link-accent", "--ui-widget-background")),
    ("loop accent",         ("--loop-accent", "--editor-background")),
    ("mute button",         ("--mute-button-normal", "--ui-widget-background")),
]

CHANNEL_PAIRS = [
    ("pitch channel", ("--pitch%d-primary-channel", "--track-editor-bg-pitch")),
    ("pitch note",    ("--pitch%d-primary-note", "--track-editor-bg-pitch")),
    ("pitch note/dim", ("--pitch%d-primary-note", "--track-editor-bg-pitch-dim")),
    ("noise channel", ("--noise%d-primary-channel", "--track-editor-bg-noise")),
    ("noise note",    ("--noise%d-primary-note", "--track-editor-bg-noise")),
    ("mod channel",   ("--mod%d-primary-channel", "--track-editor-bg-mod")),
    ("mod note",      ("--mod%d-primary-note", "--track-editor-bg-mod")),
]

SLOT_COUNT = {"pitch": 8, "noise": 5, "mod": 4}


def parse_themes(src: str):
    """Split the `themes` object into {name: css} using the backtick literals."""
    body = src[src.index("public static readonly themes"):]
    out = {}
    for m in re.finditer(r'"([^"\n]+)"\s*:\s*`', body):
        name = m.group(1)
        end = body.index("`", m.end())
        out[name] = body[m.end():end]
    return out


def parse_vars(css: str):
    vals = {}
    for m in re.finditer(r"(--[a-zA-Z0-9-]+)\s*:\s*([^;{}]+);", css):
        vals[m.group(1)] = m.group(2).strip()
    return vals


def rgb(value: str):
    value = value.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{6})", value)
    if m:
        h = m.group(1)
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
    m = re.fullmatch(r"#([0-9a-fA-F]{3})", value)
    if m:
        return tuple(int(c * 2, 16) for c in m.group(1))
    m = re.fullmatch(r"rgba?\(([^)]+)\)", value)
    if m:
        parts = [p.strip() for p in m.group(1).split(",")]
        r, g, b = (float(parts[0]), float(parts[1]), float(parts[2]))
        a = float(parts[3]) if len(parts) > 3 else 1.0
        return None if a < 0.99 else (r, g, b)
    return None


def lum(c):
    def ch(v):
        v /= 255.0
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = c
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def ratio(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def check(name, css, warn_at=2.0):
    v = parse_vars(css)
    print(f"\n== {name} ==")
    worst = []
    for label, (fg, bg) in PAIRS:
        a, b = rgb(v.get(fg, "")), rgb(v.get(bg, ""))
        if a is None or b is None:
            continue
        r = ratio(a, b)
        worst.append((r, f"{label}: {fg} on {bg}"))
        print(f"  {r:5.2f}  {label}")
    for label, (fg_tpl, bg) in CHANNEL_PAIRS:
        kind = fg_tpl.lstrip("-").split("%")[0]
        b = rgb(v.get(bg, ""))
        if b is None:
            continue
        vals = []
        for i in range(1, SLOT_COUNT[kind] + 1):
            c = rgb(v.get(fg_tpl % i, ""))
            if c is not None:
                vals.append(ratio(c, b))
        if not vals:
            continue
        worst.append((min(vals), f"{label} (worst of {len(vals)})"))
        print(f"  {min(vals):5.2f}  {label}  min of [{', '.join(f'{x:.1f}' for x in vals)}]")
    bad = sorted(w for w in worst if w[0] < warn_at)
    for r, label in bad:
        print(f"  !! under {warn_at}:1 -> {label} ({r:.2f})")
    return bad


if __name__ == "__main__":
    src = open(SRC).read()
    themes = parse_themes(src)
    wanted = sys.argv[1:] or [t for t in ("viridescent", "solarized osaka", "gruvbox dark", "watermelon", "cod salmon") if t in themes]
    bad = []
    for t in wanted:
        if t not in themes:
            print(f"missing theme: {t}")
            continue
        bad += check(t, themes[t])
    sys.exit(1 if bad else 0)
