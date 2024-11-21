<script lang="ts">
  import type { Dataset, SubDataSet } from "../types/sentence";


  let BACKEND = import.meta.env.VITE_BACKEND || "";
  export let dataset!: Dataset;
  export let subDataset!: SubDataSet;
  export let onFileUploded: (status: boolean) => void;

  let files: File[] = [];
  let dragOver = false;
  // Handle file drop
  function handleDrop(event: DragEvent) {
    event.preventDefault();
    dragOver = false;

    // Get the dropped files
    files = Array.from(event?.dataTransfer?.files ?? []);
    files = [...files];
  }

  function startUpload() {
    const textFiles = files.filter((file) => file.type === "text/plain");
    let text_lines = "";
    // Read the contents of each text file
    textFiles.forEach((file, index) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        let file_value = e.target?.result as string; // Assign the file content to file_value
        text_lines += file_value + "\n";

        if (index === textFiles.length - 1) {
          files = [];
          let json = toJson(text_lines.split("\n"));
          json = json.trim();
          if (json != "") {
            saveFile(json , subDataset, dataset);
          }
          
        }
      };
      reader.readAsText(file);
    });
  }

  // Handle file selection
  // Handle file selection
  function handleFileInput(event: Event) {
    const selectedFiles = Array.from(
      (event.target as HTMLInputElement).files ?? []
    );
    files = [...files, ...selectedFiles];
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
    files.splice(index, 1);
    files = [...files];
  }

  function toJson(transcriptions: string[]) {
    const jsonOutput = transcriptions.filter((transcription) => transcription.trim() !== "").map((transcription, index) => ({
      transcription: transcription.trim(),
    }));
    return JSON.stringify(jsonOutput, null, 2);
  }

  function saveFile(fileContent: string, subDataset:SubDataSet, dataset:Dataset) {

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
        files = [];
        alert("Saved");
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

    <p class="text-gray-400 font-semibold text-sm">
      Drag & Drop or <span class="text-[#007bff]">Choose file</span> to upload
    </p>
    <input
      id="file-input"
      type="file"
      class="hidden"
      multiple
      on:change={handleFileInput}
    />
    <p class="text-xs text-gray-400 mt-2">Only text files are Allowed.</p>
  </div>

  {#if files.length > 0}
    <div class="mt-4 space-y-2 w-full">
      <ul>
        {#each files as file, index (file.name)}
          <li class="flex justify-between items-center border-b py-2">
            <span class="text-sm text-gray-700">{file.name}</span>

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
