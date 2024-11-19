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
  <button on:click={playAudio} disabled={isPlaying || isPaused}  aria-label="Play Audio">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M8 5v14l11-7z"/>
    </svg>
  </button>
  <button on:click={pauseAudio} disabled={!isPlaying}  aria-label="Pause Audio">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M6 6h4v12H6zm8 0h4v12h-4z"/>
    </svg>
  </button>
  <button on:click={stopAudio} disabled={!isPlaying}  aria-label="Stop Audio">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path d="M6 6h12v12H6z"/>
    </svg>
  </button>
</div>
