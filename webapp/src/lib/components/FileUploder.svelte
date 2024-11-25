<script lang="ts">
  import { showAlertStore } from "$lib/stores/store";
  import {
    type Dataset,
    SubDataSet,
    type Entity,
    type TranscriptionFile,
    Emotion,
  } from "$lib/types/model";
  import EntitiesList from "./EntitiesList.svelte";

  let BACKEND = import.meta.env.VITE_BACKEND || "";
  export let dataset!: Dataset;
  export let subDataset!: SubDataSet;
  export let onFileUploded: (status: boolean) => void;
  export let speakers: Entity[] = [];
  export let emotions: any[] = [];

  let transcriptionFiles: TranscriptionFile[] = [];
  let dragOver = false;
  // Handle file drop
  function handleDrop(event: DragEvent) {
    event.preventDefault();
    dragOver = false;

    // Get the dropped files
    let files = Array.from(event?.dataTransfer?.files ?? []);

    let _transcriptionFiles = files.map((file: File) => {
      return {
        file: file,
        emotion: Emotion.NEUTRAL,
        speaker: speakers[0]?.value ?? 1,
      };
    });

    transcriptionFiles = [...transcriptionFiles, ..._transcriptionFiles];
  }

  function startUpload() {
    const textFiles = transcriptionFiles.filter(
      (transcriptionFile: TranscriptionFile) =>
        transcriptionFile.file.type === "text/plain"
    );
    let text_lines = "";

    // Read the contents of each text file
    textFiles.forEach((transcriptionFile: TranscriptionFile, index: number) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        let file_value = e.target?.result as string; // Assign the file content to file_value
        text_lines += file_value + "\n";

        if (index === textFiles.length - 1) {
          transcriptionFiles = [];
          let json = toJson(
            text_lines.split("\n"),
            transcriptionFile.emotion,
            transcriptionFile.speaker
          );
          json = json.trim();
          if (json != "") {
            saveFile(json, subDataset, dataset);
          }
        }
      };
      reader.readAsText(transcriptionFile.file);
    });
  }

  function handleFileInput(event: Event) {
    const selectedFiles = Array.from(
      (event.target as HTMLInputElement).files ?? []
    );

    let _transcriptionFiles = selectedFiles.map((file: File) => {
      return {
        file: file,
        emotion: Emotion.NEUTRAL,
        speaker: speakers[0].value,
      };
    });

    transcriptionFiles = [...transcriptionFiles, ..._transcriptionFiles];
  }

  // Handle drag over
  function handleDragOver(event: DragEvent) {
    event.preventDefault();
    dragOver = true;
  }

  // Handle drag leave
  function handleDragLeave() {
    dragOver = false;
  }

  // Handle file removal
  function removeFile(index: number) {
    transcriptionFiles.splice(index, 1);
    transcriptionFiles = [...transcriptionFiles];
  }

  function toJson(transcriptions: string[], emotion: Emotion, speaker: number) {
    const jsonOutput = transcriptions
      .filter((transcription) => transcription.trim() !== "")
      .map((transcription, index) => ({
        transcription: transcription.trim(),
        emotion: emotion,
        speaker: speaker,
      }));
    return JSON.stringify(jsonOutput, null, 2);
  }

  function saveFile(
    fileContent: string,
    subDataset: SubDataSet,
    dataset: Dataset
  ) {
    const formData = new FormData();
    formData.append("transcription", fileContent);
    formData.append("sub_dataset", subDataset.toString());
    formData.append("dataset", dataset.id.toString());

    fetch(`${BACKEND}/import_transcriptions`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status !== "success") {
          onFileUploded(false);
          return;
        }
        onFileUploded(true);
        transcriptionFiles = [];
        showAlertStore.set({
          msg: "File imported.",
          success: true,
        });
      });
  }
</script>

<div class=" flex flex-col items-center justify-center p-4">
  <div
    role="button"
    tabindex="0"
    class={`w-full py-4 text-center flex flex-col items-center justify-center border-2 border-dashed rounded-lg ${dragOver ? "border-blue-500" : "border-gray-300"}`}
    on:drop={handleDrop}
    on:dragover={handleDragOver}
    on:dragleave={handleDragLeave}
  >
    <svg class="h-10 w-10 text-gray-400">
      <use href="icons.svg#icon-uploader"></use>
    </svg>

    <button
      class="text-gray-400 font-semibold text-sm"
      on:click={() => document.getElementById("file-input")?.click()}
    >
      Drag & Drop or <span class="text-[#007bff]">Choose file</span> to upload
    </button>
    <input
      id="file-input"
      type="file"
      class="hidden"
      multiple
      on:change={handleFileInput}
    />
    <p class="text-xs text-gray-400 mt-2">Only text files are Allowed.</p>
  </div>

  {#if transcriptionFiles.length > 0}
    <div class="mt-4 space-y-2 w-full">
      <ul>
        {#each transcriptionFiles as transcriptionFile, index}
          <li class="flex justify-between items-center border-b py-2">
            <div class="flex items-center gap-1">
              <EntitiesList
                title="({speakers.find(
                  (_speaker) =>
                    _speaker.value === (transcriptionFile.speaker ?? 0)
                )?.label})Set selection speaker"
                icon="speaker"
                entities={speakers}
                onEntitySelected={(entity: any) => {
                  transcriptionFile.speaker = entity.value;
                }}
              ></EntitiesList>

              <EntitiesList
                title="Set selection emotion"
                icon={transcriptionFile.emotion}
                entities={emotions}
                onEntitySelected={(entity: any) => {
                  transcriptionFile.emotion = entity.value;
                }}
              ></EntitiesList>

              <span class="text-sm text-gray-700"
                >{transcriptionFile.file.name}</span
              >
            </div>
            <button
              on:click={() => removeFile(index)}
              aria-labelledby="Remove Audio File"
            >
              <svg class=" w-5 h-5 text-red-700">
                <use href="icons.svg#icon-trash"></use>
              </svg>
            </button>
          </li>
        {/each}
      </ul>
    </div>
  {/if}
</div>
<div class="flex gap-4 px-4">
  <button
    type="button"
    class="w-full px-4 py-2 rounded-lg text-gray-800 text-sm border-none outline-none tracking-wide bg-gray-200 hover:bg-gray-300 active:bg-gray-200"
    >Cancel</button
  >
  <button
    type="button"
    on:click={startUpload}
    class="w-full px-4 py-2 rounded-lg text-white text-sm border-none outline-none tracking-wide bg-blue-600 hover:bg-blue-700 active:bg-blue-600"
    >Import</button
  >
</div>

<style>
</style>
