<script lang="ts">
  import type { Speaker } from "$lib/types/model";
  let BACKEND = import.meta.env.VITE_BACKEND || "";

  import { onMount } from "svelte";
  import ConfirmationBox from "./ConfirmationBox.svelte";
  import { speakersStore } from "$lib/stores/store";

  let newSpeaker: string = "";
  let showConfirmationBox = false;
  let selectedSpeaker: Speaker | null = null;


  onMount(() => {
    getSpeaker();
  });

  let speakers: Speaker[] = [];
  function getSpeaker() {
    fetch(`${BACKEND}/get_speakers`)
      .then((response) => response.json())
      .then((_speakers: Speaker[]) => {
        speakers = _speakers;
        speakersStore.set(speakers);
      });
  }

  function addSpeaker() {
    if (!newSpeaker) {
      return;
    }
    const formData = new FormData();
    formData.append("speaker", newSpeaker);

    fetch(`${BACKEND}/add_speaker`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status === "success") {
          newSpeaker = "";
          getSpeaker();
        } else {
          alert("Failed to save the speaker.");
        }
      });
  }

  function deleteSpeaker(speaker: Speaker) {
    const formData = new FormData();
    formData.append("id", speaker.id.toString());

    fetch(`${BACKEND}/delete_speaker`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((result) => {
        if (result.status === "success") {
          selectedSpeaker = null;
          getSpeaker();
        } else {
          alert("Failed to delete the speaker.");
        }
      });
  }

  function deletionConfirmed() {
    showConfirmationBox = false;
    if (!selectedSpeaker) {
      return;
    }
    deleteSpeaker(selectedSpeaker);
  }
  function deletionRejected() {
    showConfirmationBox = false;
    selectedSpeaker = null;
  }
</script>

<ConfirmationBox
  show={showConfirmationBox}
  onConfirmed={deletionConfirmed}
  onRejected={deletionRejected}
></ConfirmationBox>

<form class="max-w-sm mx-auto">
  <input
    type="text"
    bind:value={newSpeaker}
    on:keydown={(event) => {
      if (event.key === "Enter") {
        addSpeaker();
      }
    }}
    id="newSpaker"
    aria-describedby="helper-text-explanation"
    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
    placeholder="Add spaker and hit enter..."
  />
</form>
<div class="space-y-4 px-4 py-4">
  {#each speakers as speaker}
    <div class="flex w-full px-4 space-x-4 border rounded-lg h-12 items-center">
      <p class="text-gray-700 capitalize flex-grow">{speaker.name}</p>
      <div>
        <button
          class="text-red-700 disabled:text-gray-400"
          disabled={speaker.id === 1}
          aria-labelledby="Remove Speaker"
          title="Remove Speaker"
          on:click={(event) => {
            selectedSpeaker = speaker;
            showConfirmationBox = true;
          }}
        >
          <svg class=" w-6 h-6">
            <use href="icons.svg#icon-trash"></use>
          </svg>
        </button>
      </div>
    </div>
  {/each}
</div>
