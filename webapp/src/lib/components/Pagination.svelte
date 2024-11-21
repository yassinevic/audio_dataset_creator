<script lang="ts">
  import { sentencesStore } from "$lib/stores/store";

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

    <svg class=" w-4 h-4 text-gray-400">
      <use href="icons.svg#icon-previous"></use>
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

    <svg class=" w-4 h-4 text-gray-400">
      <use href="icons.svg#icon-next"></use>
    </svg>

  </button>
</div>
