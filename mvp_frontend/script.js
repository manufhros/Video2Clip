document.addEventListener('DOMContentLoaded', () => {
    const videoUpload = document.getElementById('videoUpload');
    const videoPlaceholder = document.getElementById('videoPlaceholder');
    const dropText = videoPlaceholder.querySelector('.drop-text');
    const videoThumbnail = document.getElementById('videoThumbnail');
    // const videoPlayer = document.getElementById('videoPlayer'); // Descomentar si quieres reproducir el vídeo también

    const chatInput = document.getElementById('chatInput');
    const sendButton = document.getElementById('sendButton');
    const chatContainer = document.getElementById('chatContainer');

    let videoFile = null;

    // --- Manejo de carga de vídeo ---

    videoPlaceholder.addEventListener('click', () => {
        videoUpload.click();
    });

    videoPlaceholder.addEventListener('dragover', (event) => {
        event.preventDefault();
        videoPlaceholder.style.borderColor = 'var(--accent-color)';
        videoPlaceholder.style.backgroundColor = '#d1e7ff'; // Un azul más claro al arrastrar
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
            } else {
                alert('Por favor, selecciona un archivo de vídeo válido.');
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
                alert('Por favor, selecciona un archivo de vídeo válido.');
                videoUpload.value = ''; // Resetea el input
            }
        }
    });

    function handleVideoFile(file) {
        videoFile = file;
        // Oculta el texto "Arrastra y suelta" y muestra la miniatura
        dropText.classList.add('hidden');
        videoThumbnail.classList.remove('hidden');
        // videoPlayer.classList.add('hidden'); // Mantenemos el reproductor oculto por ahora

        // Generar miniatura (esto es una simulación, para una miniatura real se necesita un canvas o una librería)
        // Para una miniatura real, podrías cargar el vídeo en un elemento <video> oculto,
        // esperar al evento 'loadeddata', y luego dibujar un frame en un <canvas>,
        // y luego convertir el canvas a una URL de datos para el src de la imagen.
        // Por simplicidad, usamos un placeholder o el propio video si fuera visible.

        const reader = new FileReader();
        reader.onload = (e) => {
            // En un escenario real, para generar una miniatura más fiel:
            // 1. Crear un elemento de vídeo temporal.
            // 2. Asignar e.target.result (o URL.createObjectURL(file)) como src.
            // 3. Escuchar el evento 'loadedmetadata' o 'seeked'.
            // 4. Dibujar el frame actual del vídeo en un canvas.
            // 5. Convertir el canvas a dataURL y asignarlo a videoThumbnail.src.
            // Por simplicidad para este MVP, si el navegador puede mostrar una miniatura por defecto para `<img>` con un `objectURL` del video, funcionará.
            // Si no, considera una imagen placeholder o una implementación más compleja de miniaturas.

            // Simulación sencilla: usamos un object URL para la miniatura si el navegador lo soporta.
            // En algunos navegadores, esto podría no mostrar una miniatura real sino un icono.
            // videoThumbnail.src = URL.createObjectURL(file);

            // Opción más robusta para la miniatura:
            generateVideoThumbnail(file, (thumbnailUrl) => {
                videoThumbnail.src = thumbnailUrl;
                videoThumbnail.onload = () => URL.revokeObjectURL(thumbnailUrl); // Liberar memoria
                enableChat();
            });


            // Si quisieras mostrar el reproductor de video en lugar de solo la miniatura:
            // videoPlaceholder.classList.add('hidden'); // Ocultar el placeholder
            // videoPlayer.classList.remove('hidden');
            // videoPlayer.src = URL.createObjectURL(file);
        };
        reader.readAsDataURL(file); // Esto es más para datos, pero para la simulación simple o para enviar al backend está bien
    }

    function generateVideoThumbnail(file, callback) {
        const video = document.createElement('video');
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        video.addEventListener('loadeddata', () => {
            // Ajustar el tamaño del canvas al del video o a un tamaño fijo de miniatura
            const aspectRatio = video.videoWidth / video.videoHeight;
            const thumbWidth = 320; // Ancho deseado para la miniatura
            const thumbHeight = thumbWidth / aspectRatio;

            canvas.width = thumbWidth;
            canvas.height = thumbHeight;

            // Ir a un punto específico del vídeo para la miniatura (ej. 1 segundo)
            video.currentTime = 1;
        });

        video.addEventListener('seeked', () => {
            // Dibujar el frame actual del video en el canvas
            context.drawImage(video, 0, 0, canvas.width, canvas.height);
            // Convertir el canvas a una URL de datos
            callback(canvas.toDataURL('image/jpeg'));
            // Limpiar
            URL.revokeObjectURL(video.src);
        });

        video.src = URL.createObjectURL(file);
        video.load(); // Importante para que se dispare 'loadeddata'
    }


    function enableChat() {
        chatInput.disabled = false;
        sendButton.disabled = false;
        chatInput.placeholder = "Vídeo cargado. Escribe tu mensaje...";
        // Opcional: añadir un mensaje inicial del sistema al chat
        // addMessageToChat("Sistema: Vídeo cargado. Ya puedes interactuar.", 'llm-message');
    }

    // --- Manejo del chat ---

    sendButton.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault(); // Evita el salto de línea en el textarea
            sendMessage();
        }
    });

    function sendMessage() {
        const messageText = chatInput.value.trim();
        if (messageText === '') return;

        addMessageToChat(messageText, 'user-message');
        chatInput.value = '';
        chatInput.style.height = 'auto'; // Resetear altura
        chatInput.style.height = `${chatInput.scrollHeight}px`; // Ajustar a contenido

        // Simulación de respuesta del LLM (aquí iría la llamada a tu backend Python)
        sendButton.disabled = true;
        chatInput.disabled = true;
        addMessageToChat("Procesando tu petición...", 'llm-message thinking'); // Mensaje temporal

        setTimeout(() => {
            // Eliminar el mensaje "Procesando..."
            const thinkingMessage = chatContainer.querySelector('.thinking');
            if (thinkingMessage) {
                thinkingMessage.remove();
            }

            const llmResponse = `Respuesta simulada del LLM para: "${messageText}". En un sistema real, esta respuesta vendría del backend procesando el vídeo y tu texto.`;
            addMessageToChat(llmResponse, 'llm-message');
            sendButton.disabled = false;
            chatInput.disabled = false;
            chatInput.focus();
        }, 1500 + Math.random() * 1000); // Simula un tiempo de respuesta variable
    }

    function addMessageToChat(text, type) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', type);
        messageElement.textContent = text;
        chatContainer.appendChild(messageElement);
        chatContainer.scrollTop = chatContainer.scrollHeight; // Auto-scroll al último mensaje
    }

    // Ajuste dinámico de la altura del textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto'; // Primero resetea para obtener el scrollHeight correcto
        let newHeight = chatInput.scrollHeight;
        const maxHeight = 150; // Altura máxima para el textarea (aprox 5-6 líneas)
        if (newHeight > maxHeight) {
            newHeight = maxHeight;
            chatInput.style.overflowY = 'auto'; // Mostrar scroll si supera el máximo
        } else {
            chatInput.style.overflowY = 'hidden'; // Ocultar scroll si no supera
        }
        chatInput.style.height = `${newHeight}px`;
    });
});