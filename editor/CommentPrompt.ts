// Copyright (c) 2012-2022 John Nesky and contributing authors, distributed under the MIT license, see accompanying the LICENSE.md file.

import { HTML } from "imperative-html/dist/esm/elements-strict";
import { SongDocument } from "./SongDocument";
import { Prompt } from "./Prompt";
import { ChangeComment } from "./changes";
import { ColorConfig } from "./ColorConfig";

	const {button, div, h2, textarea, span} = HTML;

export class CommentPrompt implements Prompt {
		private readonly _channel: number;
		private readonly _bar: number;
		private readonly _commentTextArea: HTMLTextAreaElement = textarea({style: "width: 100%; height: 6em; box-sizing: border-box; resize: none;", maxlength: "250", placeholder: "e.g. todo: add bass line"});
		private readonly _deleteButton: HTMLButtonElement = button({class: "deleteButton", style: "visibility: hidden;"}, "Delete");
		private readonly _cancelButton: HTMLButtonElement = button({class: "cancelButton"});
		private readonly _okayButton: HTMLButtonElement = button({class: "okayButton", style: "width:45%;"}, "Okay");

		public readonly container: HTMLDivElement = div({class: "prompt noSelection", style: "width: 300px;"},
		h2("Bar Comment"),
			div({style: `display: flex; align-items: center; height: 2em; color: ${ColorConfig.secondaryText};`},
				"Channel:",
				span({style: "margin-left: 0.3em; margin-right: 1.5em;"}, ""),
				"Bar:",
				span({style: "margin-left: 0.3em;"}, ""),
			),
			this._commentTextArea,
			div({style: "display: flex; flex-direction: row-reverse; justify-content: space-between; margin-top: 0.75em;"},
				this._okayButton,
				this._deleteButton,
			),
		this._cancelButton,
	);

	constructor(private _doc: SongDocument) {
		this._channel = _doc.channel;
		this._bar = _doc.bar;

		const channelLabel: HTMLSpanElement = <HTMLSpanElement>this.container.querySelectorAll("span")[0];
		channelLabel.textContent = (this._channel + 1) + "";
		const barLabel: HTMLSpanElement = <HTMLSpanElement>this.container.querySelectorAll("span")[1];
		barLabel.textContent = (this._bar + 1) + "";

		const existingComment: string | null = this._doc.song.getComment(this._channel, this._bar);
		if (existingComment != null) {
			this._commentTextArea.value = existingComment;
			this._deleteButton.style.visibility = "visible";
		}

		this._commentTextArea.select();
			setTimeout(()=>this._commentTextArea.focus());

		this._okayButton.addEventListener("click", this._saveChanges);
		this._cancelButton.addEventListener("click", this._close);
		this._deleteButton.addEventListener("click", this._deleteComment);
		this._commentTextArea.addEventListener("keydown", this._whenTextAreaKeyPressed);
		this.container.addEventListener("keydown", this._whenKeyPressed);
	}

		private _close = (): void => {
		this._doc.undo();
	}

	public cleanUp = (): void => {
		this._okayButton.removeEventListener("click", this._saveChanges);
		this._cancelButton.removeEventListener("click", this._close);
		this._deleteButton.removeEventListener("click", this._deleteComment);
		this._commentTextArea.removeEventListener("keydown", this._whenTextAreaKeyPressed);
		this.container.removeEventListener("keydown", this._whenKeyPressed);
	}

	private _whenKeyPressed = (event: KeyboardEvent): void => {
		if ((<Element> event.target).tagName != "TEXTAREA" && event.keyCode == 13) { // Enter key
			this._saveChanges();
		}
	}

	private _whenTextAreaKeyPressed = (event: KeyboardEvent): void => {
		if (event.keyCode == 13 && !event.shiftKey) { // Enter key (without shift) saves; shift+enter makes a new line.
			event.preventDefault();
			this._saveChanges();
		}
	}

	private _saveChanges = (): void => {
		this._doc.prompt = null;
		this._doc.record(new ChangeComment(this._doc, this._channel, this._bar, this._commentTextArea.value), true);
	}

	private _deleteComment = (): void => {
		this._doc.prompt = null;
		this._doc.record(new ChangeComment(this._doc, this._channel, this._bar, ""), true);
	}
}
