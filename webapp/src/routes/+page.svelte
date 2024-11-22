<script lang="ts">
  import {
    SentenceStatus,
    SubDataSet,
    type Dataset,
    type Sentence,
    type SentenceID,
    type SentenceResponse,
  } from "$lib/types/sentence";

  import AudioPlayer from "$lib/components/AudioPlayer.svelte";
  import ConfirmationBox from "$lib/components/ConfirmationBox.svelte";
  import DropDown from "$lib/components/DropDown.svelte";
  import FileUploder from "$lib/components/FileUploder.svelte";
  import Pagination from "$lib/components/Pagination.svelte";
  import Subset from "$lib/components/Subset.svelte";
  import { sentencesStore } from "$lib/stores/store";
  let BACKEND = import.meta.env.VITE_BACKEND || "";

  // Reactive subscription to the store
  $: sentences = $sentencesStore;

  let deletionselectedValues: number[] = [];
  let selectedSentence: Sentence | null = null;
  let dataset: Dataset;
  let subDataset: SubDataSet | null = null;
  let showConfirmationBox = false;
  let mediaRecorder!: MediaRecorder;
  let audioChunks: BlobPart[] = [];
  let currentPage: number = 1;
  let pageSize: number = 10;
  let firstLoad = true;
  let currentSentenceStatus = SentenceStatus.ALL;
  let newSentance = "";
  $: currentPage, firePagination();

  function firePagination() {
    if (firstLoad) return;
    getSentences(currentSentenceStatus);
  }

  function getSentences(sentenceStatus: SentenceStatus) {
    currentSentenceStatus = sentenceStatus;

    fetch(
      `${BACKEND}/get_sentences/${sentenceStatus}/${currentPage}/${pageSize}/${dataset.id}/${subDataset}`
    )
      .then((response) => response.json())
      .then((sentenceResponse: SentenceResponse) => {
        sentencesStore.set(sentenceResponse);
        firstLoad = false;
      });
  }

  function startRecording(sentence: any) {
    try {
      sentencesStore.update((sentenceResponse) => ({
        ...sentenceResponse,
        sentence: sentenceResponse.sentence.map((_sentence: Sentence) =>
          _sentence.id === sentence.id
            ? { ..._sentence, isRecording: true }
            : _sentence
        ),
      }));
      navigator.mediaDevices
        .getUserMedia({
          audio: true,
        })
        .then((stream) => {
          mediaRecorder = new MediaRecorder(stream);

          mediaRecorder.ondataavailable = (event) => {
            audioChunks.push(event.data);
          };

          mediaRecorder.onstop = () => {
            const audioBlob = new Blob(audioChunks, { type: "audio/wav" });
            uploadRecording(audioBlob, sentence);
            audioChunks = [];
          };

          mediaRecorder.start();
        });
    } catch (error) {
      console.error("Microphone access denied:", error);
      alert("Please allow access to the microphone.");
    }
  }

  function showAll() {
    currentPage = 1;
    getSentences(SentenceStatus.ALL);
  }

  function showRecorded() {
    currentPage = 1;
    getSentences(SentenceStatus.RECORDED);
  }

  function showPending() {
    currentPage = 1;
    getSentences(SentenceStatus.PENDIND);
  }

  function stopRecording() {
    if (mediaRecorder && mediaRecorder.state !== "inactive") {
      mediaRecorder.stop();
    }
  }

  function rejectRemoveRecording() {
    showConfirmationBox = false;
    selectedSentence = null;
    deletionselectedValues = [];
  }

  function confirmRemoveRecording(
    sentence: Sentence | SentenceID[] | SentenceStatus
  ) {
    showConfirmationBox = true;
    if (typeof sentence === "object" && !Array.isArray(sentence)) {
      deletionselectedValues = [];
      selectedSentence = sentence;
    } else if (Array.isArray(sentence)) {
      deletionselectedValues = [...sentence];
      selectedSentence = null;
    } else {
      selectedSentence = null;
    }
  }

  function deletionConfirmed() {
    showConfirmationBox = false;
    if (deletionselectedValues.length > 0) {
      deleteSelection();
      return;
    }
    removeRecording();
  }

  function removeRecording() {
    if (!selectedSentence) {
      return;
    }
    const formData = new FormData();
    formData.append("id", selectedSentence.id.toString());
    formData.append("file", selectedSentence.file);
    formData.append("dataset", dataset.name);
    formData.append("subset", subDataset ?? "");

    fetch(`${BACKEND}/removeRecording`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (!selectedSentence) {
          return;
        }
        if (result.status === "success") {
          selectedSentence.recorded = false;
        } else {
          alert("Failed to save the recording.");
        }
        selectedSentence.isRecording = false;
        sentencesStore.update((sentences) => ({
          ...sentences,
          sentence: sentences.sentence.map((_sentence: Sentence) =>
            _sentence.id === (selectedSentence?.id ?? -1)
              ? { ..._sentence, isRecording: false }
              : _sentence
          ),
        }));
        selectedSentence = null;
      });
  }
  function deleteSelection() {
    if (deletionselectedValues.length === 0) {
      return;
    }

    const formData = new FormData();
    formData.append("transcription", deletionselectedValues.join(","));
    formData.append("dataset", dataset.name);
    formData.append("subset", subDataset ?? "");

    fetch(`${BACKEND}/delete_transcriptions`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status === "success") {
          getSentences(currentSentenceStatus);
          deletionselectedValues = [];
        } else {
          alert("Failed to save the recording.");
        }
      });
  }

  function uploadRecording(audioBlob: Blob, sentence: any) {
    const formData = new FormData();
    formData.append("audio", audioBlob);
    formData.append("id", sentence.id.toString());
    formData.append("file", sentence.file);
    formData.append("dataset", dataset.name);
    formData.append("subset", subDataset ?? "");

    fetch(`${BACKEND}/upload_audio`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status === "success") {
          sentence.recorded = true;
        } else {
          alert("Failed to save the recording.");
        }

        sentencesStore.update((sentences) => ({
          ...sentences,
          sentence: sentences.sentence.map((_sentence: Sentence) =>
            _sentence.id === (sentence?.id ?? -1)
              ? { ..._sentence, isRecording: false, recorded: true }
              : _sentence
          ),
        }));
      });
  }

  function setCurrentDataset(_dataset: Dataset) {
    subDataset = null;
    dataset = _dataset;
    sentencesStore.set({ count: 0, sentence: [] });
  }

  function setCurrentSubset(_subDataset: SubDataSet) {
    subDataset = _subDataset;
    getSentences(SentenceStatus.ALL);
  }

  function addSentance() {
    let jsonOutput = [
      {
        transcription: newSentance.trim(),
      },
    ];
    let transcription = JSON.stringify(jsonOutput, null, 2);
    const formData = new FormData();
    formData.append("transcription", transcription);
    formData.append("sub_dataset", subDataset ?? "");
    formData.append("dataset", dataset.id.toString());

    fetch(`${BACKEND}/import_transcriptions`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status === "success") {
          getSentences(currentSentenceStatus);
        } else {
          alert("Failed to save the recording.");
        }
      });
    newSentance = "";
  }

  function exportDataset() {
    const formData = new FormData();
    formData.append("datasetId", dataset.id.toString());
    formData.append("subDataset", subDataset ?? "");
    formData.append("datasetName", dataset.name);

    fetch(`${BACKEND}/export_dataset`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status === "success") {
          getSentences(currentSentenceStatus);
        } else {
          alert("Failed to save the recording.");
        }
      });
    newSentance = "";
  }
</script>

<svelte:head>
  <title>Audio DataSet Manager</title>
</svelte:head>
<ConfirmationBox
  show={showConfirmationBox}
  onConfirmed={deletionConfirmed}
  onRejected={rejectRemoveRecording}
></ConfirmationBox>

<div class="flex w-full">
  <div class="sm:px-6 w-3/4">
    <!--- more free and premium Tailwind CSS components at https://tailwinduikit.com/ --->
    <div class="px-4 md:px-10 py-4 md:py-7">
      <div class="flex items-center justify-between">
        <div
          class="flex focus:outline-none text-base sm:text-lg md:text-xl lg:text-2xl font-bold leading-normal text-gray-800"
        >
          <div class="flex place-items-center">Dataset:</div>
          <div class="flex place-items-center pl-2">
            <DropDown onDatasetSelected={setCurrentDataset}></DropDown>
          </div>
          <div class="flex place-items-center pl-2">
            <button
              aria-label="Export the dataset"
              on:click={exportDataset}
              class:hidden={!subDataset}
              title="Export the dataset"
            >
              <svg class=" w-6 h-6 text-gray-600">
                <use href="icons.svg#icon-export"></use>
              </svg></button
            >
          </div>
        </div>
      </div>
    </div>

    <div class="bg-white py-4 md:py-7 px-4 md:px-8 xl:px-10">
      <div class="sm:flex items-center justify-between">
        <div class="flex items-center">
          <button
            on:click={showAll}
            class:bg-indigo-50={currentSentenceStatus === SentenceStatus.ALL}
            class:ring-indigo-800={currentSentenceStatus === SentenceStatus.ALL}
            class:ring-2={currentSentenceStatus === SentenceStatus.ALL}
            class:hidden={!subDataset}
            class="rounded-full focus:outline-none focus:ring-2 focus:bg-indigo-50 focus:ring-indigo-800 ml-4 sm:ml-8"
          >
            <div
              class="py-2 px-8 text-gray-600 hover:text-indigo-700 hover:bg-indigo-100 rounded-full"
            >
              <p>All</p>
            </div>
          </button>
          <button
            on:click={showRecorded}
            class:bg-indigo-50={currentSentenceStatus ===
              SentenceStatus.RECORDED}
            class:ring-indigo-800={currentSentenceStatus ===
              SentenceStatus.RECORDED}
            class:ring-2={currentSentenceStatus === SentenceStatus.RECORDED}
            class:hidden={!subDataset}
            class="rounded-full focus:outline-none focus:ring-2 focus:bg-indigo-50 focus:ring-indigo-800 ml-4 sm:ml-8"
          >
            <div
              class="py-2 px-8 text-gray-600 hover:text-indigo-700 hover:bg-indigo-100 rounded-full"
            >
              <p>Recoded</p>
            </div>
          </button>
          <button
            on:click={showPending}
            class:bg-indigo-50={currentSentenceStatus ===
              SentenceStatus.PENDIND}
            class:ring-indigo-800={currentSentenceStatus ===
              SentenceStatus.PENDIND}
            class:ring-2={currentSentenceStatus === SentenceStatus.PENDIND}
            class:hidden={!subDataset}
            class="rounded-full focus:outline-none focus:ring-2 focus:bg-indigo-50 focus:ring-indigo-800 ml-4 sm:ml-8"
          >
            <div
              class="py-2 px-8 text-gray-600 hover:text-indigo-700 hover:bg-indigo-100 rounded-full"
            >
              <p>Pending</p>
            </div>
          </button>
        </div>
        <div>
          <button
            disabled={deletionselectedValues.length === 0}
            class:hidden={!subDataset}
            on:click={(event) => confirmRemoveRecording(deletionselectedValues)}
            class="px-2 py-2 text-xs disabled:bg-gray-300 font-medium text-white bg-blue-500 rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            Delete selection
          </button>
        </div>
      </div>

      <div class="pt-6 pb-2" class:hidden={!subDataset}>
        <form class="max-w-sm mx-auto">
          <label
            for="nexwSentance"
            class="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
            >Add your sentence and hit enter</label
          >
          <input
            type="text"
            bind:value={newSentance}
            on:keydown={(event) => {
              if (event.key === "Enter") {
                addSentance();
              }
            }}
            id="newSentance"
            aria-describedby="helper-text-explanation"
            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
            placeholder="Your sentence here..."
          />
        </form>
      </div>

      <div class="mt-7 overflow-x-auto" class:hidden={!subDataset}>
        <div class="flex justify-end pb-2">
          <Pagination
            onNext={() => currentPage++}
            {currentPage}
            OnPrevious={() => currentPage--}
          ></Pagination>
        </div>

        <table class="w-full whitespace-nowrap">
          <tbody>
            {#each sentences?.sentence ?? [] as sentence (sentence.id)}
              <tr
                tabindex="0"
                class="focus:outline-none h-16 border border-gray-100 rounded"
              >
                <td>
                  <div class="ml-5">
                    <div
                      class="bg-gray-200 rounded-sm w-5 h-5 flex flex-shrink-0 justify-center items-center relative"
                    >
                      <input
                        placeholder="checkbox"
                        type="checkbox"
                        class="focus:opacity-100 checkbox opacity-0 absolute cursor-pointer w-full h-full"
                        value={sentence.id}
                        bind:group={deletionselectedValues}
                      />
                      <div
                        class="check-icon hidden bg-indigo-700 text-white rounded-sm"
                      >
                        <svg class=" w-4 h-4 text-gray-400">
                          <use href="icons.svg#icon-checked"></use>
                        </svg>
                      </div>
                    </div>
                  </div>
                </td>
                <td class="">
                  <div class="flex items-center pl-5">
                    <p
                      class="text-base font-medium leading-none text-gray-700 mr-2 p-4 focus:border
                       border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      contenteditable="true"
                    >
                      {sentence.transcription}
                    </p>

                    <button aria-labelledby="Update sentence">
                      <svg class=" w-4 h-4 text-gray-400">
                        <use href="icons.svg#icon-update-text"></use>
                      </svg>
                    </button>
                  </div>
                </td>
                <td>
                  {#if sentence.recorded}
                    <AudioPlayer src={BACKEND + "/" + sentence.file} />
                  {/if}
                </td>
                <td class="pl-5">
                  <button
                    class="py-3 px-3 text-sm focus:outline-none leading-none rounded"
                    class:bg-red-100={!sentence.recorded}
                    class:text-red-700={!sentence.recorded}
                    class:bg-green-100={sentence.recorded}
                    class:text-green-700={sentence.recorded}
                    >{sentence.recorded ? "Recoded" : "Pending"}
                  </button>
                </td>

                <td class="pl-4">
                  <button
                    class:hidden={sentence.isRecording}
                    on:click={(event) => startRecording(sentence)}
                    aria-label="Microphone"
                    title="Start recording"
                  >
                    <svg class=" w-6 h-6 text-gray-600">
                      <use href="icons.svg#icon-mic"></use>
                    </svg>
                  </button>

                  <button
                    class:hidden={!sentence.isRecording}
                    on:click={(event) => stopRecording()}
                    class="mic-button p-2"
                    aria-label="Microphone Disabled"
                    title="Stop recording"
                  >
                    <svg class=" w-6 h-6 text-red-700">
                      <use href="icons.svg#icon-mic"></use>
                    </svg>
                  </button>
                  <button
                    on:click={(event) => confirmRemoveRecording([sentence.id])}
                    aria-label="Delete the sentence"
                    title="Delete the sentence"
                  >
                    <svg class=" w-6 h-6 text-red-700">
                      <use href="icons.svg#icon-trash"></use>
                    </svg>
                  </button>
                  <button
                    class:hidden={!sentence.recorded}
                    on:click={(event) => confirmRemoveRecording(sentence)}
                    aria-labelledby="Delete audio only"
                    title="Delete audio only"
                  >
                    <svg class=" w-6 h-6 text-gray-700">
                      <use href="icons.svg#icon-wav"></use>
                    </svg>
                  </button>
                </td>
              </tr>
              <tr class="h-3"></tr>
            {/each}
          </tbody>
        </table>
      </div>
    </div>
  </div>
  <div class="w-1/4 px-4 blur-sm" class:blur-sm={!dataset?.id}>
    <div class="flex flex-col">
      <div class="flex justify-end"></div>
      <div class="flex-grow pt-10">
        <h4
          class="flex w-full justify-center text-lg font-semibold text-gray-800 dark:text-gray-300 pb-6"
        >
          Subsets Manager
        </h4>

        <div class="px-4">
          <Subset {dataset} onSubDatasetSelected={setCurrentSubset}></Subset>
        </div>
        {#if subDataset}
          <FileUploder
            {dataset}
            {subDataset}
            onFileUploded={(status) => {
              status && getSentences(currentSentenceStatus);
            }}
          ></FileUploder>
        {/if}
      </div>
    </div>
  </div>
</div>

<style>
  .checkbox:checked + .check-icon {
    display: flex;
  }
</style>
