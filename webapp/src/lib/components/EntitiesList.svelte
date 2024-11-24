<script lang="ts">
  import { Emotion } from "$lib/types/model";
  import { onMount } from "svelte";
  let showMenu = false;
  export let entities: any[] = [];
  export let disabled: boolean = false;
  export let title: string = "";
  export let icon: string = "";
  export let iconClass: string = "w-6 h-6 text-gray-400";
  export let buttonClass: string = "pt-1";
  
  export let onEntitySelected: (emotion: Emotion) => void;
  let container: HTMLDivElement; // Reference to the component's DOM element

  function selectEntitiy(selectedEntery: any) {
    onEntitySelected(selectedEntery);
    showMenu = false;
  }

  function handleOutsideClick(event: Event) {
    if (!container.contains(event.target as Node | null)) {
      showMenu = false; // Close if clicked outside the component
    }
  }

  // Add the global click listener on mount
  onMount(() => {
    document.addEventListener("click", handleOutsideClick);

    return () => {
      document.removeEventListener("click", handleOutsideClick);
    };
  });
</script>

<div
  class="flex flex-col"
  on:blur={() => (showMenu = false)}
  bind:this={container}
>
  <div class="relative flex items-center">
    <button
      {disabled}
      {title}
      aria-label="Open dataset list"
      class="{buttonClass}"
      on:click={() => (showMenu = !showMenu)}
    >
      <svg class="{iconClass}" class:hidden={!icon}>
        <use href="icons.svg#icon-{icon}"></use>
      </svg>
    </button>
  </div>
  <div>
    <div
      class:hidden={!showMenu}
      id="dataset-list"
      class="absolute z-10 bg-white border border-gray-300 rounded-lg mt-1 overflow-y-auto hidden"
    >
      {#each entities as entity, index}
        <div class="flex">
          <button
            role="menuitem"
            class="cursor-pointer text-slate-800 flex w-full text-sm items-center rounded-md p-3 transition-all hover:bg-slate-100 focus:bg-slate-100 active:bg-slate-100"
            on:click={() => selectEntitiy(entity)}
          >
            <svg class=" w-4 h-4 text-gray-400">
              <use href="icons.svg#icon-{entity.icon}"></use>
            </svg>

            <div class="flex flex-col gap-1 ml-4 items-start">
              <p class="text-slate-800 font-medium">{entity.label}</p>
            </div>
          </button>
        </div>
      {/each}
    </div>
  </div>
</div>
