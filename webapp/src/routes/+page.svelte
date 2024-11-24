<script lang="ts">
  import {
    Emotion,
    SentenceStatus,
    SubDataSet,
    type Dataset,
    type Entity,
    type Sentence,
    type SentenceID,
    type SentenceResponse,
    type Speaker,
  } from "$lib/types/model";

  import AudioPlayer from "$lib/components/AudioPlayer.svelte";
  import ConfirmationBox from "$lib/components/ConfirmationBox.svelte";
  import DropDown from "$lib/components/DropDown.svelte";
  import FileUploder from "$lib/components/FileUploder.svelte";
  import Pagination from "$lib/components/Pagination.svelte";
  import Subset from "$lib/components/Subset.svelte";
  import { sentencesStore } from "$lib/stores/store";
  import EntitiesList from "$lib/components/EntitiesList.svelte";
  import { onMount } from "svelte";
  let BACKEND = import.meta.env.VITE_BACKEND || "";

  // Reactive subscription to the store
  $: sentences = $sentencesStore;

  let selectedSentences: Sentence[] = [];
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

  onMount(() => {
    {
      getSpeaker();
    }
  });

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
            const audioBlob = new Blob(audioChunks, { type: "audio/webm" });

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
    selectedSentences = [];
  }

  function confirmRemoveRecording(
    sentence: Sentence | Sentence[] | SentenceStatus
  ) {
    showConfirmationBox = true;
    if (typeof sentence === "object" && !Array.isArray(sentence)) {
      selectedSentences = [];
      selectedSentence = sentence;
    } else if (Array.isArray(sentence)) {
      selectedSentences = [...sentence];
      selectedSentence = null;
    } else {
      selectedSentence = null;
    }
  }

  function deletionConfirmed() {
    showConfirmationBox = false;
    if (selectedSentences.length > 0) {
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
    if (selectedSentences.length === 0) {
      return;
    }

    let ids = selectedSentences.map((sentence) => sentence.id);
    const formData = new FormData();
    formData.append("transcription", ids.join(","));
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
          selectedSentences = [];
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
          getSentences(currentSentenceStatus);
        } else {
          alert("Failed to save the recording.");
        }
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
        emotion: Emotion.NEUTRAL,
        speaker: speakers[0].value ?? 1,
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

  let emotions = Object.entries(Emotion).map((emotion) => {
    return {
      value: emotion[1],
      label: emotion[1],
      icon: emotion[1],
    };
  });
  let speakers: Entity[] =[];
  function getSpeaker() {
    fetch(`${BACKEND}/get_speakers`)
      .then((response) => response.json())
      .then((_speakers: Speaker[]) => {
        speakers = _speakers.map((speaker: Speaker) => {
          return {
            value: speaker.id,
            label: speaker.name,
            icon: "speaker",
          };
        });
      });
  }

  function updateSentance(sentence: Sentence) {
    const formData = new FormData();
    formData.append("speaker", sentence.speaker.toString());
    formData.append("emotion", sentence.emotion);
    formData.append("transcription", sentence.transcription);
    formData.append("id", sentence.id.toString());

    fetch(`${BACKEND}/update_sentance`, {
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

    <div class="pt-6 pb-4" class:hidden={!subDataset}>
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
        <div class="flex justify-end gap-4" class:hidden={!subDataset}>
          <EntitiesList
            title="Set selection speaker"
            icon="speaker"
            disabled={selectedSentences.length === 0}
            iconClass="w-4 h-4 text-white disabled:text-gray-400"
            buttonClass="px-2 py-2 text-xs disabled:bg-gray-300 font-medium text-white bg-blue-500 rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400"
            entities={speakers}
            onEntitySelected={(entity: any) => {
              selectedSentences.forEach((sentence: Sentence) => {
                sentence.speaker = entity.value;
                updateSentance(sentence);
              });
            }}
          ></EntitiesList>

          <EntitiesList
            title="Set selection emotion"
            disabled={selectedSentences.length === 0}
            icon={Emotion.NEUTRAL}
            iconClass="w-4 h-4 text-white disabled:text-gray-400"
            buttonClass="px-2 py-2 text-xs disabled:bg-gray-300 font-medium text-white bg-blue-500 rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400"
            entities={emotions}
            onEntitySelected={(entity: any) => {
              selectedSentences.forEach((sentence: Sentence) => {
                sentence.emotion = entity.value;
                updateSentance(sentence);
              });
            }}
          ></EntitiesList>

          <button
            aria-labelledby="Delete Selection"
            title="Delete Selection"
            disabled={selectedSentences.length === 0}
            class:hidden={!subDataset}
            on:click={(event) => confirmRemoveRecording(selectedSentences)}
            class="px-2 py-2 text-xs disabled:bg-gray-300 font-medium text-white bg-blue-500 rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            <svg class=" w-4 h-4 text-white disabled:text-gray-400">
              <use href="icons.svg#icon-trash"></use>
            </svg>
          </button>
        </div>
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
                        value={sentence}
                        bind:group={selectedSentences}
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
                      on:click={(event) => {
                        (event.target as HTMLElement)?.setAttribute(
                          "contenteditable",
                          "true"
                        );
                      }}
                      contenteditable="true"
                      on:keydown={(event) => {
                        if (event.key === "Enter") {
                          event.preventDefault();
                          const target = event.target as HTMLInputElement;
                          target.setAttribute("contenteditable", "false");

                          if (
                            sentence.transcription.trim() !==
                            target.textContent?.trim()
                          ) {
                            sentence.transcription = target.textContent;
                            updateSentance(sentence);
                          }
                        }
                      }}
                      on:blur={(event) => {
                        const target = event.target as HTMLInputElement;
                        if (
                          sentence.transcription.trim() !==
                          target.textContent?.trim()
                        ) {
                          sentence.transcription = target.textContent;
                          updateSentance(sentence);
                        }
                      }}
                    >
                      {sentence.transcription}
                    </p>

          
                  </div>
                </td>
                <td>
                  {#if sentence.recorded}
                    <AudioPlayer src={BACKEND + "/" + dataset.name+ "/" + subDataset + "/audio/" + sentence.file} />
                  {/if}
                </td>

                <td class="">
                  <div class="flex items-center pl-5 gap-2">
                    <EntitiesList
                      icon="speaker"
                      entities={speakers}
                      onEntitySelected={(entity: any) => {
                        sentence.speaker_name = entity.label;
                        sentence.speaker = entity.value;

                        updateSentance(sentence);
                      }}
                    ></EntitiesList>

                    <p class="text-gray-700 capitalize">
                      {sentence.speaker_name}
                    </p>
                  </div>
                </td>

                <td class="">
                  <div class="flex items-center pl-5 gap-2">
                    <EntitiesList
                      icon={sentence.emotion}
                      entities={emotions}
                      onEntitySelected={(entity: any) => {
                        sentence.emotion = entity.value;
                        updateSentance(sentence);
                      }}
                    ></EntitiesList>
                    <p class="text-gray-700 capitalize">
                      {sentence.emotion}
                    </p>
                  </div>
                </td>

 

                <td class="pl-5">
                  <div class:hidden={!sentence.recorded} class="text-sm text-gray-600 flex items-center gap-1">
                    <svg class=" text-gray-600 w-4 h-4">
                      <use href="icons.svg#icon-clock"></use>
                    </svg>
                    {sentence.end_time}s
                
                  </div>
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
                    on:click={(event) => confirmRemoveRecording([sentence])}
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
            speakers={speakers}
            emotions={emotions}
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
