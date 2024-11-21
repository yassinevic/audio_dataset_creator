<script lang="ts">
  let audio: HTMLAudioElement | null = null;
  let isPlaying = false;
  let isPaused = false;
  export let src = ''; // Pass the file name like 'file.wav'
  
  function playAudio() {
    if (!audio) {
      audio = new Audio(src);  // Load the audio file when play is clicked
      audio.onended = () => {
        isPlaying = false;
        isPaused = false;
      };
    }
    audio.play();
    isPlaying = true;
    isPaused = false;
  }
  
  function pauseAudio() {
    if (audio) {
      audio.pause();
      isPlaying = false;
      isPaused = true;
    }
  }
  
  function stopAudio() {
    if (audio) {
      audio.pause();
      audio.currentTime = 0; // Reset the audio to the beginning
      isPlaying = false;
      isPaused = false;
    }
  }
</script>

<style>
  button {
    background-color: transparent;
    border: none;
    cursor: pointer;
    padding: 10px;
  }
  svg {
    width: 24px;
    height: 24px;
    fill: #000;
  }
</style>

<div>
  <button
    on:click={playAudio}
    disabled={isPlaying || isPaused}
    aria-label="Play Audio"
  >
    <svg class=" w-5 h-5">
      <use href="icons.svg#icon-play"></use>
    </svg>
  </button>
  <button on:click={pauseAudio} disabled={!isPlaying} aria-label="Pause Audio">
    <svg class=" w-5 h-5">
      <use href="icons.svg#icon-pause"></use>
    </svg>
  </button>
  <button on:click={stopAudio} disabled={!isPlaying} aria-label="Stop Audio">
    <svg class=" w-5 h-5">
      <use href="icons.svg#icon-stop"></use>
    </svg>
  </button>
</div>
