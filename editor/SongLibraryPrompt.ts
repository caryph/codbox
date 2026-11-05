// Copyright (c) 2012-2022 John Nesky and contributing authors, distributed under the MIT license, see accompanying the LICENSE.md file.

import { Song } from "../synth/synth";
import { HTML } from "imperative-html/dist/esm/elements-strict";
import { SongDocument } from "./SongDocument";
import { Prompt } from "./Prompt";
import { generateUid } from "./SongRecovery";
import { ChangeSongTitle } from "./changes";
import { StoredSong, getAllSongs, saveSong, deleteSong, flushAutosave } from "./SongStorage";
import { ColorConfig } from "./ColorConfig";

	const {button, div, h2, p, input, span} = HTML;

const pageSize: number = 12;
const thumbWidth: number = 320;
const thumbHeight: number = 64;

export class SongLibraryPrompt implements Prompt {
	private readonly _filterInput: HTMLInputElement = input({type: "text", style: "width: 100%; box-sizing: border-box;", placeholder: "Filter by name..."});
	private readonly _countLabel: HTMLParagraphElement = p();
	private readonly _grid: HTMLDivElement = div({class: "songLibraryGrid"});
	private readonly _gridScroller: HTMLDivElement = div({style: "max-height: 420px; overflow-y: auto; padding: 2px;"}, this._grid);
	private readonly _pagerPrev: HTMLButtonElement = button({class: "songLibraryPagerButton", title: "Previous page"}, "‹");
	private readonly _pagerNext: HTMLButtonElement = button({class: "songLibraryPagerButton", title: "Next page"}, "›");
	private readonly _pagerLabel: HTMLSpanElement = span({style: "font-size: smaller; color: var(--secondary-text, #999);"});
	private readonly _pager: HTMLDivElement = div({class: "songLibraryPager", style: "display: none;"}, this._pagerPrev, this._pagerLabel, this._pagerNext);
	private readonly _cancelButton: HTMLButtonElement = button({class: "cancelButton"});

	private _songs: StoredSong[] = [];
	private _filter: string = "";
	private _page: number = 0;

	public readonly container: HTMLDivElement = div({class: "prompt noSelection", style: "width: 620px; max-width: 95vw;"},
		div({class: "songLibraryHeader"},
			h2("Song Library"),
			this._countLabel,
		),
		p("Songs are auto-saved in this browser as you edit them. Click a song to open it."),
		div({style: "margin-bottom: 8px;"}, this._filterInput),
		this._gridScroller,
		this._pager,
		this._cancelButton,
	);

	constructor(private _doc: SongDocument) {
		this._cancelButton.addEventListener("click", this._close);
		this._filterInput.addEventListener("input", this._whenFilterChanged);
		this._pagerPrev.addEventListener("click", () => { this._setPage(this._page - 1); });
		this._pagerNext.addEventListener("click", () => { this._setPage(this._page + 1); });
		this._refresh();
	}

	public cleanUp = (): void => {
		this._cancelButton.removeEventListener("click", this._close);
		this._filterInput.removeEventListener("input", this._whenFilterChanged);
	}

	private _close = (): void => {
		this._doc.undo();
	}

	private _whenFilterChanged = (): void => {
		this._filter = this._filterInput.value.trim().toLowerCase();
		this._setPage(0);
	}

	private _setPage(page: number): void {
		this._page = page;
		this._renderList();
	}

	private _refresh(): void {
		getAllSongs().then(songs => {
			this._songs = songs;
			this._renderList();
		});
	}

	private _filteredSongs(): StoredSong[] {
		if (this._filter == "") return this._songs;
		return this._songs.filter(song => song.name.toLowerCase().indexOf(this._filter) != -1);
	}

	private _renderList(): void {
		const songs: StoredSong[] = this._filteredSongs();
		const pageCount: number = Math.max(1, Math.ceil(songs.length / pageSize));
		this._page = Math.max(0, Math.min(pageCount - 1, this._page));

		this._countLabel.textContent = songs.length + (songs.length == 1 ? " song" : " songs");
		this._grid.innerHTML = "";
		this._pager.style.display = pageCount > 1 ? "" : "none";
		this._pagerLabel.textContent = (this._page + 1) + " / " + pageCount;
		this._pagerPrev.disabled = this._page <= 0;
		this._pagerNext.disabled = this._page >= pageCount - 1;

		if (songs.length == 0) {
			this._grid.style.display = "block";
			this._grid.appendChild(p(this._songs.length == 0
				? "There are no saved songs yet. Songs are saved automatically as you edit them."
				: "No songs match this filter."));
			return;
		}

		this._grid.style.display = "grid";
		const start: number = this._page * pageSize;
		for (const song of songs.slice(start, start + pageSize)) {
			this._grid.appendChild(this._buildCard(song));
		}
	}

	private _buildCard(song: StoredSong): HTMLElement {
		const isCurrent: boolean = (song.uid == this._doc.libraryUid);

		const thumbnail: HTMLCanvasElement = HTML.canvas({class: "songLibraryThumb", width: thumbWidth * 2, height: thumbHeight * 2, style: `height: ${thumbHeight}px;`});
		this._drawThumbnail(song, thumbnail);

		const actions: HTMLDivElement = div({class: "songLibraryActions"},
			this._actionButton("Rename", "✎", () => this._beginRename(song, infoRow)),
			this._actionButton("Open in New Tab", "↗", () => this._openSong(song, true)),
			this._actionButton("Copy Link", "🔗", () => this._copySongUrl(song)),
			this._actionButton("Duplicate", "⧉", () => this._duplicateSong(song)),
			this._actionButton("Delete", "🗑", () => this._deleteSong(song), "dangerButton"),
		);

		const name: HTMLSpanElement = span({class: "songLibraryName"}, song.name);
		const meta: HTMLSpanElement = span({class: "songLibraryMeta"},
			new Date(song.updatedAt).toLocaleString(undefined, {month: "short", day: "numeric", hour: "numeric", minute: "2-digit"})
			+ " · " + this._formatSize(song.data.length));
		const infoRow: HTMLDivElement = div({class: "songLibraryInfo"},
			div({class: "songLibraryNameRow"},
				name,
				...(isCurrent ? [span({class: "songLibraryCurrentChip"}, "current")] : []),
			),
			meta,
		);

		const card: HTMLDivElement = div({class: "songLibraryCard" + (isCurrent ? " currentSong" : "")},
			div({class: "songLibraryThumbRow"},
				thumbnail,
				actions,
			),
			infoRow,
		);
		card.addEventListener("click", () => { this._openSong(song, false); });
		return card;
	}

	private _actionButton(title: string, label: string, onclick: () => void, extraClass: string = ""): HTMLButtonElement {
		const buttonElement: HTMLButtonElement = button({class: "songLibraryButton " + extraClass, title: title}, label);
		buttonElement.addEventListener("click", (event: MouseEvent) => {
			event.stopPropagation();
			onclick();
		});
		return buttonElement;
	}

	private _formatSize(length: number): string {
		return length >= 1024 ? (length / 1024).toFixed(1) + " KB" : length + " B";
	}

	private _drawThumbnail(song: StoredSong, canvas: HTMLCanvasElement): void {
		const scale: number = 2;
		canvas.width = thumbWidth * scale;
		canvas.height = thumbHeight * scale;
		const ctx: CanvasRenderingContext2D | null = canvas.getContext("2d");
		if (ctx == null) return;
		ctx.scale(scale, scale);

		let parsed: Song;
		try {
			parsed = new Song(song.data);
		} catch (error) {
			ctx.fillStyle = ColorConfig.getComputed("--track-editor-bg-pitch-dim");
			ctx.fillRect(0, 0, thumbWidth, thumbHeight);
			return;
		}

		const channelCount: number = parsed.getChannelCount();
		const rowHeight: number = Math.max(3, Math.min(14, Math.floor((thumbHeight - 6) / channelCount)));
		const gridHeight: number = rowHeight * channelCount;
		const top: number = Math.floor((thumbHeight - gridHeight) / 2);
		const barWidth: number = thumbWidth / parsed.barCount;

		for (let channel: number = 0; channel < channelCount; channel++) {
			// Dim background for this channel's row.
			if (channel < parsed.pitchChannelCount) {
				ctx.fillStyle = ColorConfig.getComputed("--track-editor-bg-pitch-dim");
			} else if (channel < parsed.pitchChannelCount + parsed.noiseChannelCount) {
				ctx.fillStyle = ColorConfig.getComputed("--track-editor-bg-noise-dim");
			} else {
				ctx.fillStyle = ColorConfig.getComputed("--track-editor-bg-mod-dim");
			}
			ctx.fillRect(0, top + channel * rowHeight, thumbWidth, rowHeight);

			const colors = ColorConfig.getComputedChannelColor(parsed, channel);
			for (let bar: number = 0; bar < parsed.barCount; bar++) {
				const pattern = parsed.getPattern(channel, bar);
				if (pattern == null) continue;
				ctx.fillStyle = (pattern.notes.length > 0) ? colors.primaryChannel : colors.secondaryChannel;
				ctx.fillRect(Math.ceil(bar * barWidth), top + channel * rowHeight, Math.max(1, Math.floor(barWidth) - 1), rowHeight);
			}
		}

		// Faint bar lines every four bars, like the bar numbers row in the track view.
		if (barWidth >= 6) {
			ctx.globalAlpha = 0.3;
			ctx.fillStyle = ColorConfig.getComputed("--editor-background");
			for (let bar: number = 4; bar < parsed.barCount; bar += 4) {
				ctx.fillRect(Math.floor(bar * barWidth), top, 1, gridHeight);
			}
			ctx.globalAlpha = 1;
		}

		// Loop region marker along the top edge.
		if (parsed.loopLength > 0 && parsed.loopLength < parsed.barCount) {
			ctx.fillStyle = ColorConfig.getComputed("--loop-accent");
			ctx.fillRect(parsed.loopStart * barWidth, top - 2, parsed.loopLength * barWidth, 2);
		}
	}

	private _beginRename(song: StoredSong, infoRow: HTMLDivElement): void {
		const nameSpan: Element | null = infoRow.querySelector(".songLibraryName");
		if (nameSpan == null) return;
		const nameInput: HTMLInputElement = input({value: song.name, maxlength: "30", style: "flex-grow: 1; min-width: 6em;"});
		nameSpan.replaceWith(nameInput);
		nameInput.select();
		nameInput.focus();
		let done: boolean = false;
		const commit = (): void => {
			if (done) return;
			done = true;
			this._renameSong(song, nameInput.value);
		};
		nameInput.addEventListener("keydown", (event: KeyboardEvent) => {
			if (event.keyCode == 13) { // Enter
				event.preventDefault();
				commit();
			} else if (event.keyCode == 27) { // Escape
				done = true;
				this._renderList();
			}
			event.stopPropagation();
		});
		nameInput.addEventListener("click", (event: MouseEvent) => { event.stopPropagation(); });
		nameInput.addEventListener("blur", commit);
	}

	private _renameSong(song: StoredSong, newName: string): void {
		newName = newName.trim();
		if (newName == "" || newName == song.name) {
			this._refresh();
			return;
		}
		if (song.uid == this._doc.libraryUid) {
			// Renaming the currently open song: change its title normally so that
			// the song data and the library stay in sync.
			this._doc.record(new ChangeSongTitle(this._doc, song.name, newName), true);
			flushAutosave().then(() => { this._refresh(); });
			return;
		} else {
			// Renaming a song that isn't open: rewrite its title in the song data.
			try {
				const parsed: Song = new Song(song.data);
				parsed.title = newName;
				song.data = parsed.toBase64String();
			} catch (error) {
				console.warn("Could not rename song:", error);
			}
			song.name = newName;
			song.updatedAt = Date.now();
			saveSong(song);
		}
		this._refresh();
	}

	private _openSong(song: StoredSong, newTab: boolean): void {
		const url: string = new URL("#" + song.data, location.href).href;
		if (newTab) {
			window.open(url, "_blank");
		} else {
			this._doc.prompt = null;
			location.hash = "#" + song.data;
		}
	}

	private _copySongUrl(song: StoredSong): void {
		const url: string = new URL("#" + song.data, location.href).href;
		if (navigator.clipboard != undefined) {
			navigator.clipboard.writeText(url).catch(() => { window.prompt("Copy song link:", url); });
		} else {
			window.prompt("Copy song link:", url);
		}
	}

	private _duplicateSong(song: StoredSong): void {
		const now: number = Date.now();
		saveSong({ uid: generateUid(), name: song.name + " (copy)", data: song.data, createdAt: now, updatedAt: now });
		this._refresh();
	}

	private _deleteSong(song: StoredSong): void {
		if (!window.confirm("Delete \"" + song.name + "\" from the library? This cannot be undone.")) return;
		deleteSong(song.uid);
		this._refresh();
	}
}
