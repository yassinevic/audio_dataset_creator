<script lang="ts">
  import { onMount } from "svelte";
  import AudioPlayer from "../components/AudioPlayer.svelte";
  import ConfirmationBox from "../components/ConfirmationBox.svelte";
  import FileUploder from "../components/FileUploder.svelte";
  import {
    SentenceStatus,
    SubDataSet,
    type Dataset,
    type Sentence,
    type SentenceID,
    type SentenceResponse,
  } from "../types/sentence";
  import Pagination from "../components/Pagination.svelte";
  import DropDown from "../components/DropDown.svelte";
  import Subset from "../components/Subset.svelte";
  import { sentencesStore } from "../stores/store";
  let BACKEND = import.meta.env.VITE_BACKEND || "";

  // Declare a variable to store the sentences
  // let sentences: Sentence[] = [];
  //$: sentences: Sentence[] = sentencesStore;
  //$: sentences: Sentence[] = sentencesStore;

  // Reactive subscription to the store
  $: sentences = $sentencesStore;

  let deletionselectedValues: number[] = [];
  let selectedSentence: Sentence | null = null;
  let dataset: Dataset;
  let subDataset: SubDataSet | null = null;
  let showConfirmationBox = false;
  let deleteAll = false;
  let mediaRecorder!: MediaRecorder;
  let audioChunks: BlobPart[] = [];
  let currentPage: number = 1;
  let pageSize: number = 10;
  let firstLoad = true;
  let currentSentenceStatus = SentenceStatus.ALL;
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
        //sentences = [...sentenceResponse.sentence];
        sentencesStore.set(sentenceResponse);
        firstLoad = false;
      });
  }

  function startRecording(sentence: any) {
    try {
      //sentence.isRecording = true;
      //sentences = [...sentences]; // Reassign array to trigger reactivity
      sentencesStore.update((sentenceResponse) => ({
        ...sentenceResponse,
        sentence: sentenceResponse.sentence.map((_sentence) =>
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
    deleteAll = false;
    if (typeof sentence === "object" && !Array.isArray(sentence)) {
      deletionselectedValues = [];
      selectedSentence = sentence;
    } else if (Array.isArray(sentence)) {
      deletionselectedValues = [...sentence];
      selectedSentence = null;
    } else if (sentence === SentenceStatus.ALL) {
      selectedSentence = null;
      deleteAll = true;
    } else {
      selectedSentence = null;
    }
  }

  function deletionConfirmed() {
    showConfirmationBox = false;
    if (deletionselectedValues.length > 0) {
      deleteSelection();
      return;
    } else if (deleteAll) {
      deleteDataset();
    }
    removeRecording();
  }

  function deleteDataset() {
    deleteAll = false;
    const formData = new FormData();
    formData.append("datasetId", dataset.id.toString());
    formData.append("datasetName", dataset.name);
    formData.append("subset", subDataset ?? "");

    fetch(`${BACKEND}/deleteDataset`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status === "success") {
          //sentences = [];
          sentencesStore.set({ count: 0, sentence: [] });
        } else {
          alert("Failed to save the recording.");
        }
      });
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
        //sentences = [...sentences]; // Reassign array to trigger reactivity
        sentencesStore.update((sentences) => ({
          ...sentences,
          sentence: sentences.sentence.map((_sentence) =>
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
      alert();
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
          //sentence.recorded = true;
          getSentences(currentSentenceStatus);
          deletionselectedValues = [];
        } else {
          alert("Failed to save the recording.");
        }
        //sentence.isRecording = false;
        //sentences = [...sentences]; // Reassign array to trigger reactivity
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
        //sentence.isRecording = false;
        //sentences = [...sentences]; // Reassign array to trigger reactivity
        sentencesStore.update((sentences) => ({
          ...sentences,
          sentence: sentences.sentence.map((_sentence) =>
            _sentence.id === (sentence?.id ?? -1)
              ? { ..._sentence, isRecording: false , recorded: true}
              : _sentence
          ),
        }));
      });
  }

  function setCurrentDataset(_dataset: Dataset) {
    subDataset = null;
    dataset = _dataset;
    //sentences = [];
    sentencesStore.set({ count: 0, sentence: [] });
  }

  function setCurrentSubset(_subDataset: SubDataSet) {
    subDataset = _subDataset;
    getSentences(SentenceStatus.ALL);
  }

  function handleFileUploded(status: boolean) {
    if (status) {
      getSentences(currentSentenceStatus);
    }
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
        </div>
      </div>
    </div>

    <div
      class="bg-white py-4 md:py-7 px-4 md:px-8 xl:px-10"
      
    >
      <div class="sm:flex items-center justify-between">
        <div class="flex items-center">
          <button
            on:click={showAll}
            class:bg-indigo-50={currentSentenceStatus === SentenceStatus.ALL}
            class:ring-indigo-800={currentSentenceStatus === SentenceStatus.ALL}
            class:ring-2={currentSentenceStatus === SentenceStatus.ALL}
            class:hidden={(sentences?.sentence ?? []).length === 0}
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
            class:hidden={(sentences?.sentence ?? []).length === 0}
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
            class:hidden={(sentences?.sentence ?? []).length === 0}
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
            class="focus:ring-2 focus:ring-offset-2 focus:ring-indigo-600 mt-4 sm:mt-0 inline-flex items-start justify-start px-6 py-3 bg-indigo-700 hover:bg-indigo-600 focus:outline-none rounded"
          >
            <p class="text-sm font-medium leading-none text-white">
              Add Sentence
            </p>
          </button>
          <button
            on:click={(event) => confirmRemoveRecording(deletionselectedValues)}
            class:hidden={(sentences?.sentence ?? []).length === 0}
            class="focus:ring-2 focus:ring-offset-2 focus:ring-indigo-600 mt-4 sm:mt-0 inline-flex items-start justify-start px-6 py-3 bg-indigo-700 hover:bg-indigo-600 focus:outline-none rounded"
          >
            <p class="text-sm font-medium leading-none text-white">
              Delete selection
            </p>
          </button>
          <button
            on:click={(event) => confirmRemoveRecording(SentenceStatus.ALL)}
            class:hidden={(sentences?.sentence ?? []).length === 0}
            class="focus:ring-2 focus:ring-offset-2 focus:ring-indigo-600 mt-4 sm:mt-0 inline-flex items-start justify-start px-6 py-3 bg-indigo-700 hover:bg-indigo-600 focus:outline-none rounded"
          >
            <p class="text-sm font-medium leading-none text-white">
              Delete All
            </p>
          </button>
        </div>
      </div>
      <div class="mt-7 overflow-x-auto" class:blur-sm={(sentences?.sentence ?? []).length === 0}>
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
                        <svg
                          class="icon icon-tabler icon-tabler-check"
                          xmlns="http://www.w3.org/2000/svg"
                          width="20"
                          height="20"
                          viewBox="0 0 24 24"
                          stroke-width="1.5"
                          stroke="currentColor"
                          fill="none"
                          stroke-linecap="round"
                          stroke-linejoin="round"
                        >
                          <path stroke="none" d="M0 0h24v24H0z"></path>
                          <path d="M5 12l5 5l10 -10"></path>
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
                      {sentence.id}
                      {sentence.transcription}
                    </p>

                    <button aria-labelledby="Update sentence">
                      <svg
                        width="18"
                        height="18"
                        viewBox="0 0 24 24"
                        version="1.1"
                        xmlns="http://www.w3.org/2000/svg"
                        xmlns:xlink="http://www.w3.org/1999/xlink"
                      >
                        <!-- Uploaded to: SVG Repo, www.svgrepo.com, Generator: SVG Repo Mixer Tools -->
                        <title>ic_fluent_phone_update_24_regular</title>
                        <desc>Created with Sketch.</desc>
                        <g
                          id="🔍-Product-Icons"
                          stroke="none"
                          stroke-width="1"
                          fill="none"
                          fill-rule="evenodd"
                        >
                          <g
                            id="ic_fluent_phone_update_24_regular"
                            fill="#212121"
                            fill-rule="nonzero"
                          >
                            <path
                              d="M15.75,2 C16.9926407,2 18,3.00735931 18,4.25 L18,19.75 C18,20.9926407 16.9926407,22 15.75,22 L8.25,22 C7.00735931,22 6,20.9926407 6,19.75 L6,4.25 C6,3.00735931 7.00735931,2 8.25,2 L15.75,2 Z M15.75,3.5 L8.25,3.5 C7.83578644,3.5 7.5,3.83578644 7.5,4.25 L7.5,19.75 C7.5,20.1642136 7.83578644,20.5 8.25,20.5 L15.75,20.5 C16.1642136,20.5 16.5,20.1642136 16.5,19.75 L16.5,4.25 C16.5,3.83578644 16.1642136,3.5 15.75,3.5 Z M12,7.03091032 C12.3796958,7.03091032 12.693491,7.3130642 12.7431534,7.67913976 L12.75,7.78091032 L12.7493326,14.4919103 L13.7113373,13.5308062 C13.9776038,13.2645396 14.3942675,13.2403335 14.687879,13.458188 L14.7719974,13.5308062 C15.038264,13.7970727 15.0624701,14.2137364 14.8446156,14.5073479 L14.7719974,14.5914663 L12.5303301,16.8331337 L12.4921384,16.8687687 L12.4296295,16.9177078 L12.3630989,16.9592071 L12.3025771,16.989272 L12.2018763,17.0253178 L12.1392767,17.0398316 L12.0467865,17.0513519 L11.9532009,17.0513519 L11.8614701,17.0400358 L11.7651467,17.0152982 L11.6535357,16.9682062 L11.576687,16.9220073 L11.4696699,16.8331337 L11.4696699,16.8331337 L9.22800255,14.5914663 C8.93510933,14.2985731 8.93510933,13.8236994 9.22800255,13.5308062 C9.49426911,13.2645396 9.9109328,13.2403335 10.2045443,13.458188 L10.2886627,13.5308062 L11.2493326,14.4919103 L11.25,7.78091032 C11.25,7.43573235 11.483185,7.14501766 11.8006203,7.05770104 L11.8982294,7.03775694 L12,7.03091032 Z"
                              id="🎨Color"
                            >
                            </path>
                          </g>
                        </g>
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
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                      width="24"
                      height="24"
                      class="text-gray-600"
                    >
                      <title>Start recording</title>
                      <path
                        d="M12 14a3 3 0 003-3V5a3 3 0 00-6 0v6a3 3 0 003 3zm5-3a5 5 0 01-10 0H5a7 7 0 0014 0h-2zm-5 6v3h4v2H8v-2h4v-3h2z"
                      />
                    </svg>
                  </button>

                  <button
                    class:hidden={!sentence.isRecording}
                    on:click={(event) => stopRecording()}
                    class="mic-button p-2"
                    aria-label="Microphone Disabled"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                      width="24"
                      height="24"
                      class="text-red-700"
                    >
                      <title>Stop recording</title>
                      <path
                        d="M12 14a3 3 0 003-3V5a3 3 0 00-6 0v6a3 3 0 003 3zm5-3a5 5 0 01-10 0H5a7 7 0 0014 0h-2zm-5 6v3h4v2H8v-2h4v-3h2z"
                      />
                      <!-- Slash Line for Disabled State -->
                      <line
                        x1="4"
                        y1="20"
                        x2="20"
                        y2="4"
                        stroke="currentColor"
                        stroke-width="2"
                        stroke-linecap="round"
                      />
                    </svg>
                  </button>
                  <button
                    on:click={(event) => confirmRemoveRecording([sentence.id])}
                    aria-label="Delete the sentence"
                  >
                    <svg
                      xmlns="http://www.w3.org/2000/svg"
                      fill="currentColor"
                      viewBox="0 0 24 24"
                      width="24"
                      height="24"
                      class="text-red-700"
                    >
                      <title>Delete the sentence</title>
                      <!-- Trash Can Icon -->
                      <path
                        d="M9 3V4H4V6H5V20C5 21.1 5.9 22 7 22H17C18.1 22 19 21.1 19 20V6H20V4H15V3H9ZM17 6V20H7V6H17ZM9 9H11V17H9V9ZM13 9H15V17H13V9Z"
                      />
                    </svg>
                  </button>
                  <button
                    class:hidden={!sentence.recorded}
                    on:click={(event) => confirmRemoveRecording(sentence)}
                  >
                    <svg
                      width="24"
                      height="24"
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 122.88 90.44"
                      ><defs
                        ><style>
                          .cls-1 {
                            fill: #212121;
                          }
                          .cls-2 {
                            fill: #f44336;
                          }
                        </style></defs
                      ><title>Remove the audio</title><path
                        class="cls-1"
                        d="M90.14,21.81a5.14,5.14,0,0,1,8.78-3.64h0a5.16,5.16,0,0,1,1.51,3.64v44L90.14,55.62V21.81ZM0,16.61A5.13,5.13,0,0,1,1.51,13h0a5.15,5.15,0,0,1,8.78,3.64V72.23a5.13,5.13,0,0,1-1.51,3.63h0A5.15,5.15,0,0,1,0,72.23V16.61Zm32.87,16.5V85.29a5.13,5.13,0,0,1-8.77,3.64h0a5.11,5.11,0,0,1-1.5-3.63V23L32.87,33.11Zm34.77-.78a5.15,5.15,0,0,1,1.5-3.64h0a5.13,5.13,0,0,1,7.26,0h0a5.11,5.11,0,0,1,1.5,3.63V43.59L67.64,33.45V32.33ZM46.76,12.89a5.14,5.14,0,0,1,8.66,3.75v4.78l-8.66-8.53Zm8.66,42.43V72.25a5.16,5.16,0,0,1-1.51,3.64h0a5.15,5.15,0,0,1-8.78-3.64V45.19L55.42,55.32ZM112.7,10.43a5.14,5.14,0,0,1,1.49-3.62l.11-.1a5,5,0,0,1,7.1.1,5.15,5.15,0,0,1,1.48,3.62v68a5.13,5.13,0,0,1-1.48,3.62l-.11.1a5.08,5.08,0,0,1-7.83-1,12.76,12.76,0,0,0-.73-2.13,5.12,5.12,0,0,1,0-.56v-68Z"
                      /><path
                        class="cls-2"
                        d="M17.94,8.27a4.83,4.83,0,1,1,6.77-6.88l80.37,79.17a4.83,4.83,0,1,1-6.77,6.88L17.94,8.27Z"
                      /></svg
                    >
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
