document.addEventListener('DOMContentLoaded', () => {
    const videoUpload = document.getElementById('videoUpload');
    const videoPlaceholder = document.getElementById('videoPlaceholder');
    const dropText = videoPlaceholder.querySelector('.drop-text');
    const videoThumbnail = document.getElementById('videoThumbnail');
    const chatInput = document.getElementById('chatInput'); // Usar id
    const sendButton = document.getElementById('sendButton'); // Usar id

    // Si no tienes un div con id="chatContainer", lo crea:
    let chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) {
        chatContainer = document.createElement('div');
        chatContainer.id = 'chatContainer';
        chatContainer.className = 'chat-container';
        document.querySelector('main').appendChild(chatContainer);
    }

    let videoFile = null;
    let videoId = null; // Almacena el ID del vídeo tras subirlo

    // --- Manejo de carga de vídeo ---
    videoPlaceholder.addEventListener('click', () => {
        videoUpload.click();
    });

    videoPlaceholder.addEventListener('dragover', (event) => {
        event.preventDefault();
        videoPlaceholder.style.borderColor = 'var(--accent-color)';
        videoPlaceholder.style.backgroundColor = '#d1e7ff';
    });

    videoPlaceholder.addEventListener('dragleave', () => {
        videoPlaceholder.style.borderColor = 'var(--border-color)';
        videoPlaceholder.style.backgroundColor = '#e9ecef';
    });

    videoPlaceholder.addEventListener('drop', (event) => {
        event.preventDefault();
        videoPlaceholder.style.borderColor = 'var(--border-color)';
        videoPlaceholder.style.backgroundColor = '#e9ecef';
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('video/')) {
                handleVideoFile(file);
            }
        }
    });

    videoUpload.addEventListener('change', (event) => {
        const files = event.target.files;
        if (files.length > 0) {
            const file = files[0];
            if (file.type.startsWith('video/')) {
                handleVideoFile(file);
            } else {
                videoUpload.value = '';
            }
        }
    });

    function handleVideoFile(file) {
        videoFile = file;
        dropText.classList.add('hidden');
        videoThumbnail.classList.remove('hidden');
        generateVideoThumbnail(file, (thumbnailUrl) => {
            videoThumbnail.src = thumbnailUrl;
            videoThumbnail.onload = () => URL.revokeObjectURL(thumbnailUrl);
            enableChat();
        });
        uploadVideoToBackend(file);
    }

    function generateVideoThumbnail(file, callback) {
        const video = document.createElement('video');
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        video.addEventListener('loadeddata', () => {
            const aspectRatio = video.videoWidth / video.videoHeight;
            const thumbWidth = 320;
            const thumbHeight = thumbWidth / aspectRatio;
            canvas.width = thumbWidth;
            canvas.height = thumbHeight;
            video.currentTime = 1;
        });
        video.addEventListener('seeked', () => {
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            callback(canvas.toDataURL('image/jpeg'));
            URL.revokeObjectURL(video.src);
        });
        video.src = URL.createObjectURL(file);
        video.load();
    }

    function uploadVideoToBackend(file) {
        addMessageToChat('⏳ Subiendo vídeo y procesando…', 'llm-message thinking');
        const formData = new FormData();
        formData.append('file', file);
        fetch('http://127.0.0.1:8000/upload', {
            method: 'POST',
            body: formData
        })
        .then(async (response) => {
            // SIEMPRE mostrar la respuesta completa
            const data = await response.json();
            videoId = data.video_id;
            removeThinkingMessages();
            addMessageToChat('✅ Respuesta JSON de /upload:', 'llm-message');
            addMessageToChat(JSON.stringify(data, null, 2), 'llm-message');
        });
    }

    function enableChat() {
        chatInput.disabled = false;
        sendButton.disabled = false;
        chatInput.placeholder = "Vídeo cargado. Escribe tu mensaje...";
    }

    // --- Chat ---

    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });

    function sendMessage() {
        const messageText = chatInput.value.trim();
        if (messageText === '') return;
        if (!videoId) {
            addMessageToChat('Primero sube un vídeo antes de preguntar.', 'llm-message');
            return;
        }

        addMessageToChat(messageText, 'user-message');
        chatInput.value = '';
        chatInput.disabled = true;
        sendButton.disabled = true;
        addMessageToChat("Procesando tu petición...", 'llm-message thinking');

        fetch('http://127.0.0.1:8000/ask', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                video_id: videoId,
                question: messageText,
                top_k: 1
            })
        })
        .then(async (response) => {
            removeThinkingMessages();
            const data = await response.json();
            addMessageToChat('✅ Respuesta JSON de /ask:', 'llm-message');
            addMessageToChat(JSON.stringify(data, null, 2), 'llm-message');
        })
        .finally(() => {
            chatInput.disabled = false;
            sendButton.disabled = false;
            chatInput.focus();
        });
    }

    function addMessageToChat(text, type) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', type);
        messageElement.textContent = text;
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function removeThinkingMessages() {
        // Elimina todos los mensajes temporales tipo "thinking"
        chatContainer.querySelectorAll('.thinking').forEach(el => el.remove());
    }

    // Altura automática para el input (opcional, si usas un textarea)
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        let newHeight = chatInput.scrollHeight;
        const maxHeight = 150;
        if (newHeight > maxHeight) {
            newHeight = maxHeight;
            chatInput.style.overflowY = 'auto';
        } else {
            chatInput.style.overflowY = 'hidden';
        }
        chatInput.style.height = `${newHeight}px`;
    });
});