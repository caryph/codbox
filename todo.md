# todo

## Feature: block comments (track view) — done
- [x] Song.comments storage, serialization (tag Y, conditional v5/v6), JSON path
- [x] ChangeComment, CommentPrompt (T key / Edit menu), track-view marker
- [x] Excel-style amber corner triangle + hover tooltip (geometry-based visibility, container-relative positioning)
- [x] Comment marker now theme-driven: `--comment-marker` (was hardcoded `#ffaa00` in style.ts); ColorConfig.setTheme injects `--comment-marker: var(--link-accent)` fallback for every theme lacking it; cod overrides to `var(--mute-button-normal)` (ochre)
- [ ] Bar insert/delete does NOT shift comments yet (stale comments possible) — hook ChangeInsertBars/ChangeDeleteBars/ChangeBarCount later
- [ ] No touch/mobile entry point besides Edit menu item (T is keyboard-only)
- [ ] Triangle overlaps up/down pattern arrows on the selected+hovered cell (cosmetic)

## Feature: persistent song storage — done
- [x] IndexedDB library, debounced autosave, flush on pagehide/beforeunload/visibilitychange
- [x] Content-match adoption at load, Song Library modal (⇧O / File menu)
- [x] Migration from SongRecovery localStorage snapshots
- [x] Library v2 UI: card grid with track-view thumbnails (canvas, theme-aware colors, loop marker, 4-bar gridlines), name+date+size, hover actions (✎ ↗ 🔗 ⧉ 🗑), pagination (12/page), filter, current-song chip, inline rename
- Known limits: last-write-wins across tabs; diverged history URLs become new entries; thumbnails re-parse song per card (fine for dozens of songs)

## Bugs found & fixed along the way
- SongStorage.withStore returned IDBRequest instead of request.result → all reads failed silently
- imperative-html renders literal "null" for null children — spread-filter instead
- Global `.beepboxEditor canvas { position: absolute }` broke thumbnail layout — override with position: relative
- TrackEditor _mouseOver flickers (mouseover/out bubble from children) — tooltip uses geometry instead

## Feature: "cod" theme (default) — done
- [x] ColorConfig: new `"cod"` theme (dark beige surfaces #221f1a/#322d25, cream text, blue-purple accents #6f63b8/#9d8ff0), 8 pitch + 5 noise + 4 mod channel colors
- [x] defaultTheme switched "ultrabox dark" → "cod"; ThemePrompt "Cod" option at top of Default Themes
- [ ] Existing users keep their saved localStorage theme — default only affects fresh profiles (maybe want forced switch?)
- [x] v2 palette revision — v1 surfaces (#221f1a, tan noise channels) read as mud/brown
- [x] v3: "cod" is now a LIGHT genuine-beige theme with dark ink accents, light-theme convention: secondary = pale, primary = ink
- [x] v4: tone split — page frame pale beige #f4eede, editor canvas saturated sand #e6d3a8 (darker + noticeably more saturated); widgets lifted pale #f3ecd8 so controls sit above the sand; accents pushed electric (#4a2fd8 link, #5f43e0 loop, violet tonic #b08ff0 + cyan fifth #8ed8e0, hot-sand mutes #c9902f)
- [ ] Contrast check on saturated canvas: dark ink channel primaries (#1f5a9c etc.) vs #efe3c4 track bg — eyeball + maybe nudge track bg lighter if notes feel muddy
- [ ] Not eyeball-tested in browser yet (run `make dev`)

## Tooling: Makefile for local testing — done
- [x] `make check` (tsc --noEmit on all 3 configs), `make editor`, `make dev` (build+serve), `make watch` (poll loop, no entr/fswatch), `make debug` (debugify), `make player/synth/all/offline/clean/distclean`
- [x] `tools/serve.py` — static server for website/ with Cache-Control: no-store (avoids stale bundle confusion); editor at /, unminified page at /index_debug.html, player at /player/
- [x] `.build-stamp` gitignored
- [ ] `make check` green; bundle targets not run yet by me (run `make dev` to eyeball the cod theme)

## Later ideas
- Comment list panel (click → jump to bar)
- Library: work-time column, sort options, "copy URL without comments" (v5 compat)
