// Copyright (c) 2012-2022 John Nesky and contributing authors, distributed under the MIT license, see accompanying the LICENSE.md file.

// Persistent song storage backed by IndexedDB. Every song modification is
// auto-saved (debounced) into a local song library, keyed by a stable lineage
// id. See SongDocument._updateHistoryState and SongLibraryPrompt.

export interface StoredSong {
	// Stable identity for a song lineage. Reuses the document's recovery uid,
	// which persists in browser history state across tab reloads.
	uid: string;
	name: string;
	data: string; // The song's base64 representation, same as the URL hash.
	createdAt: number;
	updatedAt: number;
}

const dbName: string = "ultraaboxSongs";
const storeName: string = "songs";

let dbPromise: Promise<IDBDatabase> | null = null;

function openDatabase(): Promise<IDBDatabase> {
	if (dbPromise == null) {
		dbPromise = new Promise((resolve, reject) => {
			const request: IDBOpenDBRequest = indexedDB.open(dbName, 1);
			request.onupgradeneeded = () => {
				const db: IDBDatabase = request.result;
				if (!db.objectStoreNames.contains(storeName)) {
					const store: IDBObjectStore = db.createObjectStore(storeName, { keyPath: "uid" });
					store.createIndex("updatedAt", "updatedAt");
				}
			};
			request.onsuccess = () => { resolve(request.result); };
			request.onerror = () => { reject(request.error); };
		});
	}
	return dbPromise;
}

async function withStore<T>(mode: IDBTransactionMode, callback: (store: IDBObjectStore) => IDBRequest<any>): Promise<T> {
	const db: IDBDatabase = await openDatabase();
	const transaction: IDBTransaction = db.transaction(storeName, mode);
	const store: IDBObjectStore = transaction.objectStore(storeName);
	const result: any = callback(store);
	// Wait for the transaction to complete so that it is not prematurely garbage collected.
	await new Promise<void>((resolve, reject) => {
		transaction.oncomplete = () => { resolve(); };
		transaction.onerror = () => { reject(transaction.error); };
		transaction.onabort = () => { reject(transaction.error); };
	});
	// For read requests, unwrap the value from the IDBRequest.
	return (result instanceof IDBRequest) ? result.result : result;
}

// Saves a song, preserving createdAt if the song already exists. Resolves when
// the song is durably written.
export async function saveSong(song: StoredSong): Promise<void> {
	try {
		await withStore("readwrite", store => store.put(song));
	} catch (error) {
		console.warn("Could not save song to library:", error);
	}
}

export async function getSong(uid: string): Promise<StoredSong | undefined> {
	try {
		return await withStore<StoredSong | undefined>("readonly", store => store.get(uid));
	} catch (error) {
		console.warn("Could not read song from library:", error);
		return undefined;
	}
}

export async function getAllSongs(): Promise<StoredSong[]> {
	try {
		const songs: StoredSong[] = await withStore<StoredSong[]>("readonly", store => store.getAll());
		songs.sort((a, b) => b.updatedAt - a.updatedAt);
		return songs;
	} catch (error) {
		console.warn("Could not list songs in library:", error);
		return [];
	}
}

export async function deleteSong(uid: string): Promise<void> {
	try {
		await withStore("readwrite", store => store.delete(uid));
	} catch (error) {
		console.warn("Could not delete song from library:", error);
	}
}

// If the library already contains a song whose data exactly matches the given
// song data, returns its uid (so that the caller can continue that song's
// lineage instead of creating a duplicate library entry). Returns null if
// there is no match.
export async function findSongUidByData(data: string): Promise<string | null> {
	try {
		const songs: StoredSong[] = await withStore<StoredSong[]>("readonly", store => store.getAll());
		for (const song of songs) {
			if (song.data == data) return song.uid;
		}
	} catch (error) {
		console.warn("Could not search song library:", error);
	}
	return null;
}

const autosaveDelay: number = 500;

let autosaveRecord: StoredSong | null = null;
let autosaveTimeoutHandle: ReturnType<typeof setTimeout> | null = null;

// Schedules a debounced auto-save. Multiple calls replace the pending record;
// only the most recent song state is written.
export function scheduleAutosave(uid: string, name: string, data: string): void {
	if (autosaveRecord == null || autosaveRecord.uid != uid) {
		const now: number = Date.now();
		autosaveRecord = { uid: uid, name: name, data: data, createdAt: now, updatedAt: now };
	} else {
		autosaveRecord.name = name;
		autosaveRecord.data = data;
		autosaveRecord.updatedAt = Date.now();
	}
	if (autosaveTimeoutHandle == null) {
		autosaveTimeoutHandle = setTimeout(flushAutosave, autosaveDelay);
	}
}

// Immediately writes any pending auto-save. Used when the page is hidden or
// closed so that no work is lost.
export function flushAutosave(): Promise<void> {
	if (autosaveTimeoutHandle != null) {
		clearTimeout(autosaveTimeoutHandle);
		autosaveTimeoutHandle = null;
	}
	if (autosaveRecord != null) {
		const record: StoredSong = autosaveRecord;
		autosaveRecord = null;
		// Preserve the original creation time if this song is already saved.
		return getSong(record.uid).then(existing => {
			if (existing != null) record.createdAt = existing.createdAt;
			return saveSong(record);
		}).catch(error => {
			console.warn("Could not auto-save song:", error);
		});
	}
	return Promise.resolve();
}

// One-time migration: copies the old SongRecovery localStorage snapshots into
// the library so that nothing is lost. The recovery data itself is left alone.
export async function migrateRecoverySongs(): Promise<void> {
	if (window.localStorage.getItem("songLibraryMigrated") != null) return;
	try {
		const prefix: string = "songVersion: ";
		const existing: StoredSong[] = await getAllSongs();
		const existingUids: Set<string> = new Set(existing.map(song => song.uid));
		for (let i: number = 0; i < window.localStorage.length; i++) {
			const key: string = window.localStorage.key(i)!;
			if (key.indexOf(prefix) != 0) continue;
			const version: any = JSON.parse(key.substring(prefix.length));
			const data: string | null = window.localStorage.getItem(key);
			if (version.uid == undefined || version.name == undefined || data == null) continue;
			if (existingUids.has(version.uid)) continue;
			const time: number = version.time != undefined ? version.time : Date.now();
			await saveSong({ uid: version.uid, name: version.name, data: data, createdAt: time, updatedAt: time });
		}
		window.localStorage.setItem("songLibraryMigrated", "true");
	} catch (error) {
		console.warn("Could not migrate recovered songs:", error);
	}
}
