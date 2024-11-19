<script lang="ts">
  import { sentencesStore } from "../stores/store";

  export let currentPage: number = 1;
  //export let pageCount: number = 0;
  export let onNext: any;
  export let OnPrevious: any;

  $: pageCount = Math.ceil(($sentencesStore?.count ?? 1) / 10);

  function next() {
    onNext();
  }

  function previous() {
    OnPrevious();
  }
</script>

<div class="inline-flex items-center justify-center gap-3">
  <button
    class:hidden={currentPage === 1}
    on:click={previous}
    class="inline-flex size-8 items-center justify-center rounded border border-gray-100 bg-white text-gray-900 rtl:rotate-180"
  >
    <span class="sr-only">Prev Page</span>
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="size-3"
      viewBox="0 0 20 20"
      fill="currentColor"
    >
      <path
        fill-rule="evenodd"
        d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z"
        clip-rule="evenodd"
      />
    </svg>
  </button>

  <p class="text-xs text-gray-900">
    {currentPage}
    <span class="mx-0.25">/</span>
    {pageCount}
  </p>

  <button
    class:hidden={currentPage >= pageCount}
    on:click={next}
    class="inline-flex size-8 items-center justify-center rounded border border-gray-100 bg-white text-gray-900 rtl:rotate-180"
  >
    <span class="sr-only">Next Page</span>
    <svg
      xmlns="http://www.w3.org/2000/svg"
      class="size-3"
      viewBox="0 0 20 20"
      fill="currentColor"
    >
      <path
        fill-rule="evenodd"
        d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
        clip-rule="evenodd"
      />
    </svg>
  </button>
</div>
