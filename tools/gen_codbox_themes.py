#!/usr/bin/env python3
"""Generate the "codbox" theme blocks (viridescent, solarized osaka, gruvbox dark,
watermelon) for editor/ColorConfig.ts.

Base palettes come from monkeytype (frontend/src/ts/constants/themes.ts):
  viridescent     bg #2c3333  caret #f0d3c9  main #95d5b2  sub #84a98c  text #e9f5db
  solarized_osaka bg #00141a  caret #b58900  main #859900  sub #2aa198  text #eee8d5
  gruvbox_dark    bg #282828  caret #fabd2f  main #d79921  sub #665c54  text #ebdbb2
  watermelon      bg #1f4437  caret #d6686f  main #d6686f  sub #3e7a65  text #cdc6bc

Channel colors follow the dark-theme convention used by the other themes in this
file: secondary channel = dark, primary channel = bright, secondary note = mid,
primary note = light.
"""

def hsl(h: float, s: float, l: float) -> str:
    h %= 360.0
    s /= 100.0
    l /= 100.0
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60.0) % 2 - 1))
    m = l - c / 2
    r, g, b = {
        0: (c, x, 0), 1: (x, c, 0), 2: (0, c, x), 3: (0, x, c),
        4: (x, 0, c), 5: (c, 0, x),
    }[int(h // 60) % 6]
    return "#%02x%02x%02x" % tuple(round((v + m) * 255) for v in (r, g, b))


# lightness ladder per channel kind, per theme (dark themes: channel bright > note light)
LADDER = (30, 66, 46, 80)  # sec-channel, prim-channel, sec-note, prim-note


def _rgb(hx: str):
    hx = hx.lstrip("#")
    return tuple(int(hx[i:i + 2], 16) for i in (0, 2, 4))


def mix(a: str, b: str, t: float) -> str:
    """Linear blend of two hex colors, t = weight of b."""
    ra, ga, ba = _rgb(a)
    rb, gb, bb = _rgb(b)
    return "#%02x%02x%02x" % (round(ra + (rb - ra) * t), round(ga + (gb - ga) * t), round(ba + (bb - ba) * t))


def channel_block(prefix: str, slots, ladder=LADDER, accents=None):
    """slots: list of (hue, sat) for the HSL ladder, or hex strings for the
    "accents" mode -- one real palette hex per channel, used verbatim for the
    primary channel + secondary note, darkened toward `dark_to` for the
    secondary channel and lightened toward `light_to` for the primary note.
    accents = dict(dark_t, dark_to, light_t, light_to)."""
    sc, pc, sn, pn = ladder
    out = []
    for i, slot in enumerate(slots, start=1):
        if isinstance(slot, str):
            quad = (mix(slot, accents["dark_to"], accents["dark_t"]),
                    slot,
                    slot,
                    mix(slot, accents["light_to"], accents["light_t"]))
        else:
            h, s = slot
            quad = (hsl(h, s, sc), hsl(h, s, pc), hsl(h, s, sn), hsl(h, s * 0.85, pn))
        names = ("secondary-channel", "primary-channel", "secondary-note", "primary-note")
        for name, hexv in zip(names, quad):
            out.append(f"\t\t\t\t--{prefix}{i}-{name}: {' ' * (18 - len(name))}{hexv};")
    return "\n".join(out)


def theme(name: str, comment: str, vars: dict, pitch, noise, mod, ladder=LADDER, accents=None):
    lines = [f'\t\t"{name}": `', "\t\t\t:root {", f"\t\t\t\t/* {comment} */"]
    for k, v in vars:
        lines.append(f"\t\t\t\t--{k.replace('_', '-')}: {v};")
    if accents:
        lines.append("\t\t\t\t/* channel colors: one palette hex per channel, darkened toward "
                     f"{accents['dark_to']} and lightened toward {accents['light_to']} */")
    else:
        sc, pc, sn, pn = ladder
        lines.append(f"\t\t\t\t/* channel colors: dark {sc}% -> light {pn}% lightness ladder */")
    lines.append(channel_block("pitch", pitch, ladder, accents))
    lines.append("")
    lines.append(channel_block("noise", noise, ladder, accents))
    lines.append("")
    lines.append(channel_block("mod", mod, ladder, accents))
    lines += ["\t\t\t}", "\t\t\t.beepboxEditor button, .beepboxEditor select {",
              "\t\t\t\tbox-shadow: inset 0 0 0 1px var(--input-box-outline);",
              "\t\t\t}", "\t\t\t`,", ""]
    return "\n".join(lines)


# ---------------------------------------------------------------- viridescent
# monkeytype "viridescent": a muted green/sage set (main #95d5b2, sub #84a98c,
# caret #f0d3c9). Hues wander through green/teal, caret peach for the accents.
VIRIDESCENT = dict(
	name="viridescent",
	comment="monkeytype 'viridescent' — sage/green on slate, peach accents",
	vars=dict(
		page_margin="#232828", editor_background="#2c3333",
		hover_preview="#b7c9b8", playhead="rgba(233, 245, 219, 0.65)",
		primary_text="#e9f5db", secondary_text="#8fae95", inverted_text="#232828",
		error_text="#ff4646", text_selection="rgba(132, 169, 140, 0.55)",
		box_selection_fill="rgba(149, 213, 178, 0.18)",
		loop_accent="#95d5b2", link_accent="#f0d3c9",
		ui_widget_background="#343c3a", ui_widget_focus="#3e4a46",
		pitch_background="#384340", tonic="#4d6b5c", fifth_note="#3c5654",
		white_piano_key="#e9f5db", black_piano_key="#61796a",
		scrollbar_background="#232828", scrollbar_color="#84a98c",
		track_editor_bg_pitch="#394744", track_editor_bg_pitch_dim="#2f3b39",
		track_editor_bg_noise="#3b433d", track_editor_bg_noise_dim="#313833",
		track_editor_bg_mod="#39424c", track_editor_bg_mod_dim="#2f363f",
		multiplicative_mod_slider="#84a98c", overwriting_mod_slider="#bd4141",
		indicator_primary="#95d5b2", indicator_secondary="#5f8f78",
		select2_opt_group="#343c3a", input_box_outline="#1e2323",
		mute_button_normal="#f0d3c9", comment_marker="var(--mute-button-normal)",
		mute_button_mod="#7fb0c9",
		note_flash="#ffffff", note_flash_secondary="rgba(255, 255, 255, 0.6)",
		oscilloscope_line_L="#e9f5db", oscilloscope_line_R="#95d5b2",
		pitch_channel_limit=8, noise_channel_limit=5, mod_channel_limit=4,
		disabled_note_primary="#6a7570", disabled_note_secondary="#4a534f",
	).items(),
	pitch=[(150, 45), (168, 40), (135, 42), (185, 38), (95, 40), (205, 38), (120, 30), (160, 25)],
	noise=[(160, 12), (30, 14), (210, 12), (100, 10), (0, 8)],
	mod=[(200, 32), (140, 28), (170, 26), (110, 26)],
)

# ------------------------------------------------------------- solarized osaka
# monkeytype "solarized_osaka": solarized's dark wheel pushed onto a near-black
# teal page (bg #00141a, sub-alt #00222b). Kept faithful: every surface is a real
# solarized/osaka color and the 8 pitch channels ARE the solarized accent wheel
# (accent hex used verbatim, only the secondary channel and the primary note are
# mixed toward the page bg / base3).
SO_B = "#00141a"       # osaka bg
SO_ALT = "#00222b"     # osaka sub-alt
SO_02 = "#073642"      # base02
SO_3 = "#fdf6e3"       # base3 (light end of the note ladder)

SO_PITCH_BG = mix(SO_02, SO_B, 0.5)
SO_PITCH_DIM = mix(SO_ALT, SO_B, 0.6)

SOLARIZED_OSAKA = dict(
	name="solarized osaka",
	comment="monkeytype 'solarized_osaka' — solarized dark wheel on the osaka near-black teal page",
	vars=dict(
		page_margin="#002b36", editor_background=SO_B,           # base03 frame, osaka canvas
		hover_preview="#93a1a1", playhead="rgba(238, 232, 213, 0.8)",  # base1, osaka text
		primary_text="#eee8d5", secondary_text="#839496", inverted_text="#002b36",  # base2/base0/base03
		error_text="#dc322f", text_selection="rgba(7, 54, 66, 0.92)",  # red, base02 selection
		box_selection_fill="rgba(38, 139, 210, 0.25)",
		loop_accent="#2aa198", link_accent="#268bd2",            # cyan, blue
		ui_widget_background=SO_ALT, ui_widget_focus=SO_02,
		pitch_background="#002b36", tonic=mix("#b58900", SO_B, 0.4), fifth_note=mix("#268bd2", SO_B, 0.45),
		white_piano_key="#eee8d5", black_piano_key=SO_02,
		scrollbar_background=SO_ALT, scrollbar_color="#2aa198",
		track_editor_bg_pitch=SO_PITCH_BG, track_editor_bg_pitch_dim=SO_PITCH_DIM,
		track_editor_bg_noise=mix(SO_PITCH_BG, "#859900", 0.07), track_editor_bg_noise_dim=mix(SO_PITCH_DIM, "#859900", 0.06),
		track_editor_bg_mod=mix(SO_PITCH_BG, "#6c71c4", 0.11), track_editor_bg_mod_dim=mix(SO_PITCH_DIM, "#6c71c4", 0.09),
		multiplicative_mod_slider="#268bd2", overwriting_mod_slider="#cb4b16",
		indicator_primary="#2aa198", indicator_secondary="#b58900",
		select2_opt_group=SO_ALT, input_box_outline=SO_B,
		mute_button_normal="#b58900", comment_marker="var(--mute-button-normal)",  # caret yellow
		mute_button_mod="#d33682",                                # colorfulError magenta
		note_flash="#ffffff", note_flash_secondary="rgba(255, 255, 255, 0.6)",
		oscilloscope_line_L="#eee8d5", oscilloscope_line_R="#2aa198",
		pitch_channel_limit=8, noise_channel_limit=5, mod_channel_limit=4,
		disabled_note_primary="#586e75", disabled_note_secondary="#073642",  # base01, base02
	).items(),
	# the solarized accent wheel: main, sub, blue, violet, magenta, red, orange, caret
	pitch=["#859900", "#2aa198", "#268bd2", "#6c71c4", "#d33682", "#dc322f", "#cb4b16", "#b58900"],
	# the solarized greys (base00 -> base1), plus base00 shifted warm / cool for the
	# last two (base01 #586e75 is too dim to read as a channel tab on its own)
	noise=["#657b83", "#839496", "#93a1a1", mix("#657b83", "#b58900", 0.35), mix("#657b83", "#268bd2", 0.4)],
	mod=["#6c71c4", "#268bd2", "#2aa198", "#d33682"],
	accents=dict(dark_to=SO_B, dark_t=0.42, light_to=SO_3, light_t=0.5),
)

# ---------------------------------------------------------------- gruvbox dark
# monkeytype "gruvbox_dark" / gruvbox palette: warm dark greys + dim/bright accents.
GRUVBOX_DARK = dict(
	name="gruvbox dark",
	comment="monkeytype 'gruvbox_dark' — warm grey bgs, gruvbox bright accents",
	vars=dict(
		page_margin="#1d2021", editor_background="#282828",
		hover_preview="#bdae93", playhead="rgba(235, 219, 178, 0.65)",
		primary_text="#ebdbb2", secondary_text="#a89984", inverted_text="#282828",
		error_text="#fb4934", text_selection="rgba(180, 142, 73, 0.55)",
		box_selection_fill="rgba(235, 219, 178, 0.16)",
		loop_accent="#fabd2f", link_accent="#83a598",
		ui_widget_background="#3c3836", ui_widget_focus="#504945",
		pitch_background="#32302f", tonic="#6b5a2c", fifth_note="#4c5a4a",
		white_piano_key="#ebdbb2", black_piano_key="#665c54",
		scrollbar_background="#282828", scrollbar_color="#665c54",
		track_editor_bg_pitch="#32302f", track_editor_bg_pitch_dim="#282623",
		track_editor_bg_noise="#36332f", track_editor_bg_noise_dim="#2c2a26",
		track_editor_bg_mod="#2f3334", track_editor_bg_mod_dim="#25292a",
		multiplicative_mod_slider="#83a598", overwriting_mod_slider="#af3a03",
		indicator_primary="#fabd2f", indicator_secondary="#d79921",
		select2_opt_group="#3c3836", input_box_outline="#1d2021",
		mute_button_normal="#fe8019", comment_marker="var(--mute-button-normal)",
		mute_button_mod="#d38696",
		note_flash="#ffffff", note_flash_secondary="rgba(255, 255, 255, 0.6)",
		oscilloscope_line_L="#ebdbb2", oscilloscope_line_R="#fabd2f",
		pitch_channel_limit=8, noise_channel_limit=5, mod_channel_limit=4,
		disabled_note_primary="#7c6f64", disabled_note_secondary="#5a524c",
	).items(),
	# red, orange, yellow, green, aqua, blue, purple, sand
	pitch=[(4, 72), (25, 85), (41, 88), (61, 55), (104, 38), (166, 21), (338, 42), (45, 40)],
	noise=[(45, 18), (25, 16), (200, 12), (335, 12), (90, 12)],
	mod=[(166, 24), (41, 55), (338, 30), (61, 35)],
)

# ------------------------------------------------------------------ watermelon
# monkeytype "watermelon": deep rind green page, melon-red caret/main, cream text.
WATERMELON = dict(
	name="watermelon",
	comment="monkeytype 'watermelon' — rind green page, melon red/pink channels",
	vars=dict(
		page_margin="#163026", editor_background="#1f4437",
		hover_preview="#b7d0c3", playhead="rgba(205, 198, 188, 0.65)",
		primary_text="#cdc6bc", secondary_text="#8fb3a3", inverted_text="#1f4437",
		error_text="#f0545c", text_selection="rgba(214, 104, 111, 0.5)",
		box_selection_fill="rgba(214, 104, 111, 0.20)",
		loop_accent="#e08088", link_accent="#f0908f",
		ui_widget_background="#244d3f", ui_widget_focus="#3e7a65",
		pitch_background="#2a5445", tonic="#8a555b", fifth_note="#4f8a72",
		white_piano_key="#f2ece0", black_piano_key="#3e7a65",
		scrollbar_background="#244d3f", scrollbar_color="#d6686f",
		track_editor_bg_pitch="#265140", track_editor_bg_pitch_dim="#1f4234",
		track_editor_bg_noise="#2d5746", track_editor_bg_noise_dim="#25483b",
		track_editor_bg_mod="#27505b", track_editor_bg_mod_dim="#1f414c",
		multiplicative_mod_slider="#6fb3a0", overwriting_mod_slider="#d6686f",
		indicator_primary="#d6686f", indicator_secondary="#3e7a65",
		select2_opt_group="#244d3f", input_box_outline="#163026",
		mute_button_normal="#e88f72", comment_marker="var(--mute-button-normal)",
		mute_button_mod="#9fd0c5",
		note_flash="#ffffff", note_flash_secondary="rgba(255, 255, 255, 0.6)",
		oscilloscope_line_L="#cdc6bc", oscilloscope_line_R="#d6686f",
		pitch_channel_limit=8, noise_channel_limit=5, mod_channel_limit=4,
		disabled_note_primary="#6f8478", disabled_note_secondary="#4f6259",
	).items(),
	# channels are lifted ~4 lightness vs the other themes: the rind-green row
	# backgrounds are lighter than the other themes', so dark melon reds sink in.
	# melon red, pink, deep red, rind green, lime, yellow-green, orange, berry
	pitch=[(356, 55), (355, 65), (0, 50), (140, 35), (90, 40), (70, 45), (25, 55), (330, 40)],
	noise=[(35, 14), (150, 12), (0, 10), (200, 12), (95, 10)],
	mod=[(175, 30), (210, 32), (140, 26), (330, 28)],
	ladder=(32, 70, 50, 84),
)

if __name__ == "__main__":
    import sys
    out = "".join(theme(**t) for t in (VIRIDESCENT, SOLARIZED_OSAKA, GRUVBOX_DARK, WATERMELON))
    if "--splice" in sys.argv:
        # rewrite the codbox region in place: from the first generated theme up to
        # (but not including) the theme that follows it in the themes object.
        path = "editor/ColorConfig.ts"
        src = open(path).read()
        first = f'\t\t"{VIRIDESCENT["name"]}": `'
        anchor = '        "dark competition": `'
        start, end = src.index(first), src.index(anchor)
        open(path, "w").write(src[:start] + out + src[end:])
        print(f"spliced {len(out)} chars into {path}")
    else:
        sys.stdout.write(out)
