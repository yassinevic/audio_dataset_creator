  export interface Sentence {
    id: number;
    file: string;
    transcription: string;
    recorded: boolean;
    isRecording?: boolean;
    sub_dataset: SubDataSet;
    dataset: SentenceID;
  }

  export type SentenceID = Sentence["id"];
  export enum SentenceStatus {
    ALL = -1,
    PENDIND = 0,
    RECORDED = 1,
  }

  export interface SentenceResponse {
    count: number;
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
