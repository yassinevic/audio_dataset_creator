<script lang="ts">
  import { sentencesStore } from "../stores/store";
  import {
    SubDataSet,
    SentenceStatus,
    type SentenceResponse,
    type Dataset,
  } from "../types/sentence";

  let BACKEND = import.meta.env.VITE_BACKEND || "";
  export let onSubDatasetSelected: (subDataset: SubDataSet) => void;
  export let dataset!: Dataset;
  let subDataset!: SubDataSet;

  let trainCount: number = 0;
  let testCount: number = 0;
  let validationCount: number = 0;

  function setCurrentSubset(_subDataset: SubDataSet) {
    subDataset = _subDataset;
    onSubDatasetSelected(subDataset);
  }

  $: if (dataset !== undefined) {
    getSubDatasetCount(SubDataSet.TRAIN).then(
      (sentenceResponse: SentenceResponse) => {
        trainCount = sentenceResponse.count ?? 0;
      }
    );
    getSubDatasetCount(SubDataSet.TEST).then(
      (sentenceResponse: SentenceResponse) => {
        testCount = sentenceResponse.count ?? 0;
      }
    );
    getSubDatasetCount(SubDataSet.VALIDATION).then(
      (sentenceResponse: SentenceResponse) => {
        validationCount = sentenceResponse.count ?? 0;
      }
    );
  }
  function getSubDatasetCount(subDataSet: SubDataSet) {
    return fetch(
      `${BACKEND}/get_sentences/${SentenceStatus.ALL}/1/1/${dataset.id}/${subDataSet}`
    ).then((response) => response.json());
  }


  $: trainCount = $sentencesStore?.sentence.find(
    (sentence) => sentence.sub_dataset === SubDataSet.TRAIN
  )
    ? ($sentencesStore?.count ?? 0)
    : trainCount;
    
  $: testCount = $sentencesStore?.sentence.find(
    (sentence) => sentence.sub_dataset === SubDataSet.TEST
  )
    ? ($sentencesStore?.count ?? 0)
    : testCount;
  $: validationCount = $sentencesStore?.sentence.find(
    (sentence) => sentence.sub_dataset === SubDataSet.VALIDATION
  )
    ? ($sentencesStore?.count ?? 0)
    : validationCount;
</script>

<div class="space-y-4">
  <!-- Train -->
  <button
    on:click={() => setCurrentSubset(SubDataSet.TRAIN)}
    class:bg-blue-50={subDataset === SubDataSet.TRAIN}
    class="flex items-center w-full space-x-4 p-4 border rounded-lg cursor-pointer peer-checked:bg-blue-100"
  >
    <!-- Icon -->
    <div class="text-blue-600">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M3 10h11m4 4h3m-4 4h3m-7-8h3m-6 0a3 3 0 100-6 3 3 0 000 6zM21 10h-6"
        />
      </svg>
    </div>
    <!-- Text -->
    <div class="flex-grow justify-start flex">Train</div>
    <!-- Badge -->
    <div
      class="bg-gray-200 text-gray-800 text-sm font-semibold rounded-full px-3 py-1"
    >
      {trainCount}
    </div>
  </button>

  <!-- Test -->
  <button
    on:click={() => setCurrentSubset(SubDataSet.TEST)}
    class:bg-blue-50={subDataset === SubDataSet.TEST}
    class="flex w-full items-center space-x-4 p-4 border rounded-lg cursor-pointer peer-checked:bg-green-100"
  >
    <!-- Icon -->
    <div class="text-green-600">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M4 6h16M4 10h16M4 14h16M4 18h16"
        />
      </svg>
    </div>
    <!-- Text -->
    <div class="flex-grow justify-start flex">Test</div>
    <!-- Badge -->
    <div
      class="bg-gray-200 text-gray-800 text-sm font-semibold rounded-full px-3 py-1"
    >
      {testCount}
    </div>
  </button>

  <!-- Validation -->
  <button
    on:click={() => setCurrentSubset(SubDataSet.VALIDATION)}
    class:bg-blue-50={subDataset === SubDataSet.VALIDATION}
    class="flex w-full space-x-4 p-4 border rounded-lg cursor-pointer peer-checked:bg-red-100"
  >
    <!-- Icon -->
    <div class="text-red-600">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-6 w-6"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 12h6m-6 4h6m-6-8h6m6 4H6"
        />
      </svg>
    </div>
    <!-- Text -->
    <div class="flex-grow justify-start flex">Validation</div>
    <!-- Badge -->
    <div
      class="bg-gray-200 text-gray-800 text-sm font-semibold rounded-full px-3 py-1"
    >
      {validationCount}
    </div>
  </button>
</div>
