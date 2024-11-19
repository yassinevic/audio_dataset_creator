<script lang="ts">
  import { onMount } from "svelte";
  import type { Dataset, DatasetResponse } from "../types/sentence";
  import { sentencesStore } from "../stores/store";

  let BACKEND = import.meta.env.VITE_BACKEND || "";
  let showMenu = false;
  let datasets: Dataset[] = [];
  let currentDataset: Dataset;
  export let onDatasetSelected: (dataset: Dataset) => void;
  onMount(() => {
    {
      fetch(`${BACKEND}/get_datasets`)
        .then((response) => response.json())
        .then((datasetsResponse: DatasetResponse) => {
            datasets = datasetsResponse.dataset ?? [];
        });
    }
  });


  function setCurrentProject(dataset: Dataset) {
    currentDataset = dataset;
    showMenu = false;
    onDatasetSelected(currentDataset);
  }


</script>

<div class="flex flex-col " on:blur={() => (showMenu = false)}>
  <div class="relative flex items-center">
    <span class="text-gray-400 pr-4">{currentDataset?.name ?? "Select a Dataset"}</span>

    <button
      class="pt-1"
      aria-label="dropdown"
      on:click={() => (showMenu = true)}
    >
      <svg
        class="text-gray-500"
        fill="currentColor"
        width="24"
        height="24"
        viewBox="0 0 14 14"
        role="img"
        focusable="false"
        aria-hidden="true"
        xmlns="http://www.w3.org/2000/svg"
        ><path
          d="m 1.0000123,6.99975 0,-4.7134 5.8088699,0 c 4.1431298,0 5.8462998,0.017 5.9393898,0.06 0.0718,0.033 0.15728,0.1182 0.189991,0.19 0.0823,0.1807 0.0823,3.6053 0,3.786 -0.105991,0.2326 -0.2305,0.2494 -1.84448,0.2494 l -1.5239708,0 0,2.571 0,2.5709 -4.2849,0 -4.2849,0 0,-4.7135 z m 7.71282,1.714 0,-2.1425 -3.4279201,0 -3.42792,0 0,2.1425 0,2.1424 3.42792,0 3.4279201,0 0,-2.1424 z m -5.99886,0.857 0,-0.4285 2.5709399,0 2.57094,0 0,0.4285 0,0.4284 -2.57094,0 -2.5709399,0 0,-0.4284 z m 0,-1.714 0,-0.4285 2.5709399,0 2.57094,0 0,0.4285 0,0.4285 -2.57094,0 -2.5709399,0 0,-0.4285 z m 5.99886,-3.4279 0,-1.2855 -3.4279201,0 -3.42792,0 0,1.2855 0,1.2854 3.42792,0 3.4279201,0 0,-1.2854 z m 2.2910807,1.0846 c 0.192459,-0.1687 1.35108,-1.6577 1.35108,-1.7364 0,-0.1911 -0.1034,-0.2052 -1.49971,-0.2052 -1.3963208,0 -1.4997208,0.014 -1.4997208,0.2052 0,0.042 0.27994,0.4291 0.62208,0.8597 0.6085808,0.766 0.7934798,0.9704 0.8776398,0.9704 0.0229,0 0.0898,-0.042 0.148631,-0.094 z"
        /></svg
      ></button
    >
  </div>
  <div>
    <div
      class:hidden={!showMenu}
      id="dataset-list"
      class="absolute z-10 bg-white border border-gray-300 rounded-lg mt-1 overflow-y-auto hidden"
    >
      <div class="border-b">
        <input
          type="text"
          placeholder="Search datasets..."
          class="w-full px-4 py-2 text-sm text-gray-300 focus:outline-none"
        />
      </div>

      {#each datasets as dataset}
        <button
          role="menuitem"
          class="cursor-pointer text-slate-800 flex w-full text-sm items-center rounded-md p-3 transition-all hover:bg-slate-100 focus:bg-slate-100 active:bg-slate-100"
          on:click={() => setCurrentProject(dataset)}
        >
          <svg
            width="20"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M4 18V6"
              stroke="#1C274C"
              stroke-width="1.5"
              stroke-linecap="round"
            />
            <path
              d="M20 6V18"
              stroke="#1C274C"
              stroke-width="1.5"
              stroke-linecap="round"
            />
            <path
              d="M12 10C16.4183 10 20 8.20914 20 6C20 3.79086 16.4183 2 12 2C7.58172 2 4 3.79086 4 6C4 8.20914 7.58172 10 12 10Z"
              stroke="#1C274C"
              stroke-width="1.5"
            />
            <path
              d="M20 12C20 14.2091 16.4183 16 12 16C7.58172 16 4 14.2091 4 12"
              stroke="#1C274C"
              stroke-width="1.5"
            />
            <path
              d="M20 18C20 20.2091 16.4183 22 12 22C7.58172 22 4 20.2091 4 18"
              stroke="#1C274C"
              stroke-width="1.5"
            />
          </svg>
          <div class="flex flex-col gap-1 ml-4 items-start">
            <p class="text-slate-800 font-medium">{dataset.name}</p>
            <p class="text-slate-500 text-sm flex items-center">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                class="w-4 h-4 mr-1 text-slate-400"
              >
                <path
                  fill-rule="evenodd"
                  d="M10 18a8 8 0 1 0 0-16 8 8 0 0 0 0 16Zm.75-13a.75.75 0 0 0-1.5 0v5c0 .414.336.75.75.75h4a.75.75 0 0 0 0-1.5h-3.25V5Z"
                  clip-rule="evenodd"
                />
              </svg>
              {dataset.creation_date}
            </p>
          </div>
        </button>
      {/each}
    </div>
  </div>
</div>
