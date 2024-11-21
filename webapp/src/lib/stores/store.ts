import { writable } from 'svelte/store';
import type {  SentenceResponse } from '../../types/sentence';

// A writable store to track the array
export const sentencesStore = writable<SentenceResponse>();
