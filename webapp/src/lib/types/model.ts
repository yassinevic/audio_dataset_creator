export interface Sentence {
  id: number;
  file: string;
  transcription: string;
  recorded: boolean;
  isRecording?: boolean;
  sub_dataset: SubDataSet;
  dataset: SentenceID;
  start_time: number;
  end_time: number;
  speaker: SpeakerID;
  speaker_name: SpeakerName;
  emotion: Emotion;
}

export type SpeakerID = Speaker["id"];
export type SpeakerName = Speaker["name"];
export type SentenceID = Sentence["id"];
export enum SentenceStatus {
  ALL = -1,
  PENDIND = 0,
  RECORDED = 1,
}

export interface SentenceResponse {
  count: number;
  subDataSet: SubDataSet;
  sentence: Sentence[];
}

export interface Dataset {
  id: number;
  name: string;
  transcription: string;
  creation_date: string;
}
export interface DatasetResponse {
  count: number;
  dataset: Dataset[];
}
export type DatasetID = Dataset["id"];

export enum SubDataSet {
  TRAIN = "train",
  TEST = "test",
  VALIDATION = "validation",
}

export enum Emotion {
  HAPPY = "happy",
  SAD = "sad",
  ANGRY = "angry",
  FEARFUL = "fearful",
  SURPRISED = "surprised",
  DISGUSTED = "disgusted",
  NEUTRAL = "neutral"
}

export interface Entity {
  value: number;
  label: string;
  icon: string;
}

export interface Speaker {
  id: number;
  name: string;
}

export interface TranscriptionFile {
  file: File;
  emotion: Emotion;
  speaker: SpeakerID;
}