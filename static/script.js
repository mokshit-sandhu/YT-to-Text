document.getElementById('transcription-form').onsubmit = async function(event) {
    event.preventDefault(); // Prevent the default form submission

    const youtubeUrl = document.getElementById('youtube_url').value;
    const transcriptionText = document.getElementById('transcription-text');
    transcriptionText.textContent = 'Processing...';

    const response = await fetch('/transcribe', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ youtube_url: youtubeUrl })
    });

    const result = await response.json();
    transcriptionText.textContent = result.transcription;
};
