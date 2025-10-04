// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', initResultPage);

function initResultPage() {
  loadOriginalAudio();
  setupCopyButtons();
  // Theme is already handled in the inline script in index-result.html
}

// Load the original audio from localStorage
function loadOriginalAudio() {
  const audioElement = document.querySelector('audio');
  if (!audioElement) return;

  // Get the audio URL from localStorage
  const audioUrl = localStorage.getItem('originalAudioUrl');
  if (!audioUrl) {
    console.error('No audio URL found in localStorage');
    return;
  }

  // Set the audio source
  const sourceElement = audioElement.querySelector('source');
  sourceElement.src = audioUrl;
  sourceElement.type = getAudioMimeType(localStorage.getItem('originalFilename') || '');

  // Load the audio
  audioElement.load();
}

// Determine MIME type based on file extension
function getAudioMimeType(filename) {
  const extension = filename.split('.').pop()?.toLowerCase();

  switch (extension) {
    case 'mp3':
      return 'audio/mpeg';
    case 'wav':
      return 'audio/wav';
    case 'm4a':
      return 'audio/mp4';
    default:
      return 'audio/mpeg'; // Default to MP3
  }
}

// Setup copy to clipboard functionality
function setupCopyButtons() {
  // Copy functionality is already handled in the inline script in index-result.html
}
