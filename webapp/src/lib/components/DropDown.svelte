<script lang="ts">
  import { onMount } from "svelte";
  import ConfirmationBox from "./ConfirmationBox.svelte";
  import type { Dataset, DatasetResponse } from "../types/sentence";
  import { sentencesStore } from "$lib/stores/store";

  let BACKEND = import.meta.env.VITE_BACKEND || "";
  let showMenu = false;
  let datasets: Dataset[] = [];
  let currentDataset: Dataset;
  let dataSetToDelete: Dataset | null;

  let newDatasetName: string = "";
  export let onDatasetSelected: (dataset: Dataset) => void;
  onMount(() => {
    {
      getDatasets();
    }
  });

  function getDatasets() {
    fetch(`${BACKEND}/get_datasets`)
      .then((response) => response.json())
      .then((datasetsResponse: DatasetResponse) => {
        datasets = datasetsResponse.dataset ?? [];
        datasets = [...datasets].reverse();
      });
  }

  function setCurrentDataset(dataset: Dataset) {
    currentDataset = dataset;
    showMenu = false;
    onDatasetSelected(currentDataset);
  }
  function addDataset() {
    if (!newDatasetName) {
      return;
    }
    const formData = new FormData();
    formData.append("dataset", newDatasetName);

    fetch(`${BACKEND}/add_dataset`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status === "success") {
          newDatasetName = "";
          getDatasets();
        } else {
          alert("Failed to save the recording.");
        }
      });
  }

  function deleteDataset(dataset: Dataset) {
    const formData = new FormData();
    formData.append("datasetId", dataset.id.toString());
    formData.append("datasetName", dataset.name);

    fetch(`${BACKEND}/delete_dataset`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status === "success") {
          sentencesStore.set({ count: 0, sentence: [] });
          getDatasets();
        } else {
          alert("Failed to save the recording.");
        }
      });
  }
  let showConfirmationBox = false;
  function rejectRemoveRecording() {
    showConfirmationBox = false;
    dataSetToDelete = null;
  }

  function deletionConfirmed() {
    showConfirmationBox = false;
    if (dataSetToDelete === null) {
      return;
    }
    deleteDataset(dataSetToDelete);
    dataSetToDelete = null;
  }
</script>

<ConfirmationBox
  show={showConfirmationBox}
  onConfirmed={deletionConfirmed}
  onRejected={rejectRemoveRecording}
></ConfirmationBox>

<div class="flex flex-col" on:blur={() => (showMenu = false)}>
  <div class="relative flex items-center">
    <span class="text-gray-400 pr-4"
      >{currentDataset?.name ?? "Select a Dataset"}</span
    >

    <button
      class="pt-1"
      title="Open dataset list"
      aria-label="Open dataset list"
      on:click={() => (showMenu = !showMenu)}
    >
      <svg class="h-6 w-6 text-gray-500">
        <use href="icons.svg#icon-drop-down"></use>
      </svg>
    </button>
  </div>
  <div>
    <div
      class:hidden={!showMenu}
      id="dataset-list"
      class="absolute z-10 bg-white border border-gray-300 rounded-lg mt-1 overflow-y-auto hidden"
    >
      <div class="flex items-center border-b p-2 bg-white w-64">
        <!-- Input -->
        <input
          type="text"
          placeholder="Search or add dataset..."
          bind:value={newDatasetName}
          class="w-full px-4 py-2 text-sm text-gray-600 focus:outline-none"
        />

        <!-- Icon -->
        <button
          class="text-gray-400"
          on:click={addDataset}
          aria-labelledby="Add dataset"
          title="Add dataset"
        >
          <svg class="h-5 w-5 text-gray-400">
            <use href="icons.svg#icon-plus"></use>
          </svg>
        </button>
      </div>

      {#each datasets as dataset}
        <div class="flex">
          <button
            role="menuitem"
            class="cursor-pointer text-slate-800 flex w-full text-sm items-center rounded-md p-3 transition-all hover:bg-slate-100 focus:bg-slate-100 active:bg-slate-100"
            on:click={() => setCurrentDataset(dataset)}
          >
            <svg class=" w-4 h-4 text-gray-400">
              <use href="icons.svg#icon-dataset"></use>
            </svg>

            <div class="flex flex-col gap-1 ml-4 items-start">
              <p class="text-slate-800 font-medium">{dataset.name}</p>
              <p class="text-slate-500 text-sm flex items-center">
                <svg class=" w-4 h-4 text-gray-400">
                  <use href="icons.svg#icon-clock"></use>
                </svg>

                {dataset.creation_date}
              </p>
            </div>
          </button>
          <button
            on:click={() => {
              dataSetToDelete = dataset;
              showConfirmationBox = true;
            }}
            aria-label="Delete this dataset"
            title="Delete this dataset"
            class="pr-2"
          >
            <svg class=" w-5 h-5 text-red-700">
              <use href="icons.svg#icon-trash"></use>
            </svg>
          </button>
        </div>
      {/each}
    </div>
  </div>
</div>
