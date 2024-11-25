<script lang="ts">
  export let msg: string = "";
  export let success = false;
  export let show = false;
</script>

<div class=" fixed top-0 z-10 flex items-center justify-start w-full">
<div class="max-w-4xl mx-auto " hidden={!show}>
  <div
    class="bg-red-50 border-b-8 rounded"
    class:bg-red-50={!success}
    class:bg-green-50={success}
    class:border-red-900={!success}
    class:border-green-900={success}
  >
    <div class="flex items-center">
      <div class="p-2">
        <div class="flex items-center">
          <div class="ml-2">
            <svg
              class="h-8 w-8 mr-2 cursor-pointer"
              class:text-red-900={!success}
              class:text-green-900={success}
              xmlns="http://www.w3.org/2000/svg"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </div>
          <p
            class="px-6 py-4 font-semibold text-lg"
            class:text-red-900={!success}
            class:text-green-900={success}
          >
            {msg}
          </p>
        </div>
      </div>
    </div>
  </div>
</div>
</div>