<script lang="ts">
  import { sentencesStore } from "$lib/stores/store";
  import {
    SentenceStatus,
    SubDataSet,
    type Dataset,
    type Sentence,
    type SentenceResponse,
  } from "../types/model";

  import ConfirmationBox from "./ConfirmationBox.svelte";

  let BACKEND = import.meta.env.VITE_BACKEND || "";
  export let onSubDatasetSelected: (subDataset: SubDataSet) => void;
  export let dataset!: Dataset;
  let subDataset!: SubDataSet;
  let subDataSetEntries = Object.entries(SubDataSet);
  let colors = ["text-blue-600", "text-green-600", "text-red-600"];

  let showConfirmationBox = false;
  let subDataSetToDelete: SubDataSet | null = null;

  let counts = {
    [SubDataSet.TRAIN]: 0,
    [SubDataSet.TEST]: 0,
    [SubDataSet.VALIDATION]: 0,
  };
  function setCurrentSubset(_subDataset: SubDataSet) {
    subDataset = _subDataset;
    onSubDatasetSelected(subDataset);
  }

  $: if (dataset !== undefined) {
    for (const [key, value] of subDataSetEntries) {
      getSubDatasetCount(value).then((sentenceResponse: SentenceResponse) => {
        counts[value] = sentenceResponse.count ?? 0;
      });
    }
  }

  function getSubDatasetCount(subDataSet: SubDataSet) {
    return fetch(
      `${BACKEND}/get_sentences/${SentenceStatus.ALL}/1/1/${dataset.id}/${subDataSet}`
    ).then((response) => response.json());
  }

  sentencesStore.subscribe((sentenceResponse) => {
    if (!sentenceResponse) {
      return;
    }

    let part: SubDataSet = sentenceResponse.subDataSet;
    counts[part] = sentenceResponse?.count ?? 0;
    counts = {
      ...counts,
    };
  });

  function rejectRemoveRecording() {
    showConfirmationBox = false;
    subDataSetToDelete = null;
  }

  function deleteSubDataset(sub_dataset: SubDataSet) {
    const formData = new FormData();
    formData.append("dataset", dataset.id.toString());
    formData.append("sub_dataset", sub_dataset);

    fetch(`${BACKEND}/delete_sub_dataset`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status === "success") {
          sentencesStore.set({ count: 0, sentence: [] });
          counts[sub_dataset] = 0;
        } else {
          alert("Failed to save the recording.");
        }
      });
  }

  function deletionConfirmed() {
    showConfirmationBox = false;
    if (subDataSetToDelete === null) {
      return;
    }
    deleteSubDataset(subDataSetToDelete);
    subDataSetToDelete = null;
  }
</script>

<ConfirmationBox
  show={showConfirmationBox}
  onConfirmed={deletionConfirmed}
  onRejected={rejectRemoveRecording}
></ConfirmationBox>

<div class="space-y-4">
  {#each subDataSetEntries as [key, value], index}
    <div
      class:bg-blue-50={subDataset === value}
      class="flex items-center w-full px-4 space-x-4 border rounded-lg cursor-pointer peer-checked:bg-blue-100"
    >
      <button
        on:click={() => setCurrentSubset(value)}
        class="flex items-center w-full space-x-4 h-12"
        >
        <!-- Icon -->
        <div class={colors[index]}>
          <svg class="w-6 h-6">
            <use href="icons.svg#icon-{value}"></use>
          </svg>
        </div>
        <!-- Text -->
        <div class="flex-grow justify-start flex capitalize">{value}</div>
        <!-- Badge -->
        <div
          class="bg-gray-200 text-gray-800 text-sm font-semibold rounded-full px-3 py-1"
        >
          {counts[value]}
        </div>
      </button>
      <button
        on:click={() => {
          subDataSetToDelete = value;
          showConfirmationBox = true;
        }}
        aria-label="Delete this sub dataset"
        class="pr-2"
                title="Delete this sub dataset"
      >
        <svg class=" w-5 h-5 text-red-700">
          <use href="icons.svg#icon-trash"></use>
        </svg>
      </button>
    </div>
  {/each}
</div>
