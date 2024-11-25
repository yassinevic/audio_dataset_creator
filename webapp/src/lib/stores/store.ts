import type { SentenceResponse, Speaker } from '$lib/types/model';
import { writable } from 'svelte/store';

export const sentencesStore = writable<SentenceResponse>();
export const speakersStore = writable<Speaker[]>([]);