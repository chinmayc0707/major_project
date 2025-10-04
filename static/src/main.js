// DOM Elements
const uploadContainer = document.getElementById('upload-container');
const fileInput = document.getElementById('file-input');
const browseButton = document.querySelector('.browse-button');
const videoInput = document.getElementById('video-input');
const videoBrowseButton = document.querySelector('.video-browse-button');
const videoFilename = document.getElementById('video-filename');
const convertButton = document.getElementById('convert-button');
const conversionProgress = document.getElementById('conversion-progress');
const conversionProgressFill = document.getElementById('conversion-progress-fill');
const conversionPercentage = document.getElementById('conversion-percentage');
const processingSection = document.getElementById('processing-section');
const progressFill = document.getElementById('progress-fill');
const progressPercentage = document.getElementById('progress-percentage');
const timeRemaining = document.getElementById('time-remaining');
const highContrastToggle = document.getElementById('high-contrast-toggle');
const faqItems = document.querySelectorAll('.faq-item');
const urlInput = document.getElementById('url-input');
const urlFetchButton = document.getElementById('url-fetch-button');
const urlStatusElement = document.getElementById('url-status');
const audioImportTabs = document.querySelectorAll('.audio-import-tab');
const tabContents = document.querySelectorAll('.tab-content');

// Theme preferences
let darkMode = localStorage.getItem('darkMode') === 'true';

// Initialize the page
function initPage() {
  setupEventListeners();
  setupThemeToggle();
  setupFaqToggle();
  setupTabsSwitching();
  updateTheme(); // Apply theme on page load
}

// Setup all event listeners
function setupEventListeners() {
  // Audio file upload via browse button
if (browseButton) {
  browseButton.addEventListener('click', (e) => {
    e.stopPropagation(); // Prevent event bubbling
    fileInput.click();
  });
}

  // Audio file upload via file input change
  if (fileInput) {
    fileInput.addEventListener('change', handleFileUpload);
  }

  // Drag and drop for audio upload
  if (uploadContainer) {
    uploadContainer.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadContainer.classList.add('dragover');
    });

    uploadContainer.addEventListener('dragleave', () => {
      uploadContainer.classList.remove('dragover');
    });

    uploadContainer.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadContainer.classList.remove('dragover');

      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleFileUpload();
      }
    });

    uploadContainer.addEventListener('click', () => {
      fileInput.click();
    });
  }

  // URL audio import
  if (urlInput) {
    urlInput.addEventListener('input', () => {
      validateURL();
      // Auto-enable fetch button if valid
      urlFetchButton.disabled = !isValidAudioURL(urlInput.value.trim());
    });
  }


  if (urlFetchButton) {
    urlFetchButton.addEventListener('click', handleURLFetch);
  }

  // Video to audio conversion
  if (videoBrowseButton) {
    videoBrowseButton.addEventListener('click', () => {
      videoInput.click();
    });
  }

  if (videoInput) {
    videoInput.addEventListener('change', handleVideoSelection);
  }

  if (convertButton) {
    convertButton.addEventListener('click', handleVideoConversion);
  }
}

// Set up tabs switching
// Update setupTabsSwitching function
function setupTabsSwitching() {
  audioImportTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      audioImportTabs.forEach(t => t.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      
      tab.classList.add('active');
      const targetId = tab.getAttribute('data-target');
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add('active');
      }
    });
  });
}

// Validate URL
function validateURL() {
  const url = urlInput.value.trim();
  const isValid = isValidAudioURL(url); 

  urlFetchButton.disabled = !isValid;

  // Update status message
  if (url === '') {
    urlStatusElement.textContent = '';
    urlStatusElement.className = 'url-status';
  } else if (isValid) {
    const isYouTube = url.includes('youtube') || url.includes('youtu.be');
    urlStatusElement.textContent = isYouTube 
      ? 'Valid YouTube URL' 
      : 'Valid audio/video URL';
    urlStatusElement.className = 'url-status success';
  } else {
    urlStatusElement.textContent = 'Invalid URL or unsupported audio format';
    urlStatusElement.className = 'url-status error';
  }
}


// Check if URL is a valid audio URL
function isValidAudioURL(url) {
  if (!url) return false;

  try {
    const parsedUrl = new URL(url);
    const hostname = parsedUrl.hostname.replace('www.', '');
    
    // Allow YouTube URLs
    if (hostname === 'youtube.com' || hostname === 'youtu.be') return true;
    
    // Allow direct video/audio files
    const pathname = parsedUrl.pathname.toLowerCase();
    const validExtensions = [
      '.mp3', '.wav', '.m4a', '.ogg', '.aac', '.flac',
      '.mp4', '.mov', '.avi', '.mkv', '.webm'
    ];
    
    return validExtensions.some(ext => pathname.endsWith(ext));
  } catch (e) {
    return false;
  }
}

// Updated handleURLFetch function to send the URL to the backend
function handleURLFetch() {
  const url = urlInput.value.trim();
  if (!isValidAudioURL(url)) {
    urlStatusElement.textContent = 'Invalid audio/video URL';
    urlStatusElement.className = 'url-status error';
    return;
  }

  urlFetchButton.disabled = true;
  urlStatusElement.textContent = 'Processing URL...';
  urlStatusElement.className = 'url-status';

  const formData = new FormData();
  formData.append('urlInput', url);

  fetch('/process-url', {
    method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(html => {
    // Replace current document with the response HTML from the backend
    document.open();
    document.write(html);
    document.close();
  })
  .catch(error => {
    console.error('Error processing URL:', error);
    urlStatusElement.textContent = 'Error processing URL';
    urlStatusElement.className = 'url-status error';
    urlFetchButton.disabled = false;
  });
}

// Create a mock file object from a URL
function createMockFileFromURL(url) {
  const parsedUrl = new URL(url);
  let filename = 'converted-audio.mp3';
  
  // Handle YouTube URLs
  if (parsedUrl.hostname.includes('youtube') || parsedUrl.hostname === 'youtu.be') {
    const videoId = parsedUrl.searchParams.get('v') || parsedUrl.pathname.split('/').pop();
    filename = `youtube-${videoId}.mp3`;
  }
  // Handle direct files
  else {
    filename = url.split('/').pop() || 'audio.mp3';
  }

  return new File(
    [new ArrayBuffer(1000)],
    filename,
    { type: 'audio/mpeg' }
  );
}

// Get MIME type from filename
function getMimeTypeFromFilename(filename) {
  const ext = filename.split('.').pop().toLowerCase();
  const mimeTypes = {
    'mp3': 'audio/mpeg',
    'wav': 'audio/wav',
    'ogg': 'audio/ogg',
    'm4a': 'audio/mp4',
    'aac': 'audio/aac',
    'flac': 'audio/flac'
  };

  return mimeTypes[ext] || 'audio/mpeg';
}

// Handle file upload
function handleFileUpload() {
  if (fileInput.files.length === 0) {
    return;
  }

  const file = fileInput.files[0];
  const fileType = file.type;

  // Validate file type
  if (!fileType.includes('audio/')) {
    alert('Please upload a valid audio file (MP3, WAV, or M4A)');
    return;
  }

  // Show processing section and hide upload section
  startProcessing(file);
}

// Show processing animation and simulate progress
function startProcessing(file) {
  // Hide upload container and show processing section
  uploadContainer.parentElement.classList.add('hidden');
  processingSection.classList.remove('hidden');

  // Simulate processing progress
  simulateProcessing(file);
}

// Simulate progress and redirect to results page
function simulateProcessing(file) {
  let progress = 0;
  const maxTime = 5; // Seconds for simulation
  const updateInterval = 100; // Update every 100ms
  const totalUpdates = (maxTime * 1000) / updateInterval;
  const increment = 100 / totalUpdates;

  const updateProgress = () => {
    progress += increment;
    const roundedProgress = Math.min(Math.round(progress), 100);

    progressFill.style.width = `${roundedProgress}%`;
    progressPercentage.textContent = roundedProgress;

    const remainingSeconds = Math.ceil((100 - roundedProgress) * maxTime / 100);
    timeRemaining.textContent = remainingSeconds <= 0 ? 'almost done...' : `${remainingSeconds} seconds`;

    if (roundedProgress < 100) {
      setTimeout(updateProgress, updateInterval);
    } else {
      // Processing complete, navigate to results page
      setTimeout(() => {
        // Create a form data object to pass the file to the result page
        const formData = new FormData();
        formData.append('audioFile', file);

        // In a real app, we would send the form data to a server
        // For this demo, we simulate the submission and redirect
        redirectToResultsPage(file);
      }, 1000);
    }
  };

  updateProgress();
}

// Updated redirectToResultsPage function to accept a field name
function redirectToResultsPage(file, fieldName = 'audioFile') {
    const formData = new FormData();
    // Append the file using the provided field name.
    formData.append(fieldName, file);

    fetch('/index-result.html', {
        method: 'POST',
        body: formData
    })
    .then(response => response.text())
    .then(html => {
        // Replace the current document with the response from the POST request.
        document.open();
        document.write(html);
        document.close();
    })
    .catch(error => {
        console.error('Error posting file:', error);
    });
}

// Handle video file selection
function handleVideoSelection() {
  if (videoInput.files.length === 0) {
    videoFilename.textContent = '';
    convertButton.disabled = true;
    return;
  }

  const file = videoInput.files[0];
  videoFilename.textContent = file.name;
  convertButton.disabled = false;
}

// Updated handleVideoConversion function to directly upload the video file without conversion
function handleVideoConversion() {
  if (videoInput.files.length === 0) return;

  const file = videoInput.files[0];
  convertButton.disabled = true;
  conversionProgress.classList.remove('hidden');

  // Optionally, simulate progress (if you want to show conversion progress)
  simulateVideoConversion().then(() => {
    // Directly send the original video file without converting to audio.
    // Using the field name "videoFile" so Flask can access it via request.files["videoFile"]
    redirectToResultsPage(file, 'videoFile');
  });
}

// Simulate video to audio conversion
function simulateVideoConversion() {
  return new Promise((resolve) => {
    let progress = 0;
    const updateInterval = 100;
    const totalTime = 3000;
    const totalSteps = totalTime / updateInterval;
    const increment = 100 / totalSteps;
    let timeLeft = 30;

    const timer = setInterval(() => {
      timeLeft = Math.max(0, timeLeft - 1);
      document.getElementById('conversion-time').textContent = `${timeLeft}s`;
    }, 1000);

    const updateConversionProgress = () => {
      progress += increment;
      const roundedProgress = Math.min(Math.round(progress), 100);

      conversionProgressFill.style.width = `${roundedProgress}%`;
      conversionPercentage.textContent = roundedProgress;

      if (roundedProgress < 100) {
        setTimeout(updateConversionProgress, updateInterval);
      } else {
        clearInterval(timer);
        setTimeout(() => {
          conversionProgress.classList.add('hidden');
          convertButton.disabled = false;
          videoFilename.textContent = '';
          videoInput.value = '';
          resolve();
        }, 500);
      }
    };

    updateConversionProgress();
  });
}

// Setup theme toggle
function setupThemeToggle() {
  if (highContrastToggle) {
    updateThemeIcon();

    highContrastToggle.addEventListener('click', () => {
      darkMode = !darkMode;
      localStorage.setItem('darkMode', darkMode);
      updateTheme();
    });
  }
}

// Update theme based on preference
function updateTheme() {
  document.body.classList.toggle('dark-mode', darkMode);
  updateThemeIcon();
}

// Update theme toggle icon
function updateThemeIcon() {
  if (highContrastToggle) {
    highContrastToggle.innerHTML = darkMode
      ? '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path></svg>'
      :'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"></circle><line x1="12" y1="1" x2="12" y2="3"></line><line x1="12" y1="21" x2="12" y2="23"></line><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line><line x1="1" y1="12" x2="3" y2="12"></line><line x1="21" y1="12" x2="23" y2="12"></line><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line></svg>';
  }
}

// Setup FAQ toggle
function setupFaqToggle() {
  faqItems.forEach(item => {
    const question = item.querySelector('.faq-question');
    question.addEventListener('click', () => {
      item.classList.toggle('active');
    });
  });
}

// Initialize the page when DOM is loaded
document.addEventListener('DOMContentLoaded', initPage);



// Text Processing Functionality
const textInput = document.getElementById('text-input');
const textProcessButton = document.getElementById('text-process-button');

if (textInput && textProcessButton) {
  textInput.addEventListener('input', handleTextInput);
  textProcessButton.addEventListener('click', handleTextProcessing);
}

function handleTextInput() {
  const hasText = textInput.value.trim().length > 0;
  textProcessButton.disabled = !hasText;
}

function handleTextProcessing(e) {
  e.preventDefault();
  const text = textInput.value.trim();
  if (text.length === 0) return;

  textProcessButton.disabled = true;
  textProcessButton.innerHTML = 'Processing...';

  const formData = new FormData();
  formData.append('textInput', text);

  fetch('/process-text', {
    method: 'POST',
    body: formData
  })
  .then(response => response.text())
  .then(html => {
    // Replace current document with the response HTML from the backend.
    document.open();
    document.write(html);
    document.close();
  })
  .catch(error => {
    console.error('Error processing text:', error);
    textProcessButton.disabled = false;
  });
}

