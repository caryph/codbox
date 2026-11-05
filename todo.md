# todo

## Feature: block comments (track view) — done
- [x] Song.comments storage, serialization (tag Y, conditional v5/v6), JSON path
- [x] ChangeComment, CommentPrompt (T key / Edit menu), track-view marker
- [x] Excel-style amber corner triangle + hover tooltip (geometry-based visibility, container-relative positioning)
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

## Later ideas
- Comment list panel (click → jump to bar)
- Library: work-time column, sort options, "copy URL without comments" (v5 compat)
