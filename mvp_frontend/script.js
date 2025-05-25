let lastVideoId = null;
let lastUploadedFile = null;
let lastClipParams = null;

document.getElementById('uploadBtn').onclick = async function() {
    const fileInput = document.getElementById('videoInput');
    const uploadResult = document.getElementById('uploadResult');
    uploadResult.textContent = 'Processing...';
    document.getElementById('downloadClipBtn').style.display = "none";

    if (!fileInput.files.length) {
        uploadResult.textContent = 'Select a video file.';
        return;
    }
    const file = fileInput.files[0];
    lastUploadedFile = file;
    lastClipParams = null;
    const formData = new FormData();
    formData.append('file', file);

    const resp = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData
    });
    let data;
    try {
        data = await resp.json();
    } catch {
        data = await resp.text();
    }

    let toShow = (typeof data === "object") ? JSON.stringify(data, null, 2) : data;
    uploadResult.textContent = toShow;

    if (typeof data === "object" && data.video_id) {
        lastVideoId = data.video_id;
        document.getElementById('videoId').value = lastVideoId;
    }
};

document.getElementById('askBtn').onclick = async function() {
    const videoId = document.getElementById('videoId').value.trim();
    const pregunta = document.getElementById('questionInput').value.trim();
    const respuestaDiv = document.getElementById('respuesta');
    const videoResultDiv = document.getElementById('videoResult');
    const downloadClipBtn = document.getElementById('downloadClipBtn');
    videoResultDiv.innerHTML = "";
    downloadClipBtn.style.display = "none";

    if (!videoId || !pregunta) {
        respuestaDiv.textContent = 'Enter the video ID and a question.';
        return;
    }
    respuestaDiv.textContent = 'Buscando respuesta...';

    const resp = await fetch('http://127.0.0.1:8000/ask', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            video_id: videoId,
            question: pregunta,
            top_k: 1
        })
    });
    let data;
    try {
        data = await resp.json();
    } catch {
        data = await resp.text();
    }

    let toShow = (typeof data === "object") ? JSON.stringify(data, null, 2) : data;
    respuestaDiv.textContent = toShow;

    if (typeof data === "object" && data.results && data.results.length > 0 && lastUploadedFile) {
        const res = data.results[0];
        if (res.start != null && res.end != null) {
            const videoUrl = URL.createObjectURL(lastUploadedFile);
            videoResultDiv.innerHTML = `
                <video id="segmentPlayer" width="100%" controls>
                    <source src="${videoUrl}" type="${lastUploadedFile.type}">
                    Your browser does not support the video element.
                </video>
                <div style="margin-top:5px; font-size:0.95em;">
                    <b>Fragmento:</b> desde <b>${res.start.toFixed(1)}s</b> hasta <b>${res.end.toFixed(1)}s</b>
                </div>
            `;
            const player = document.getElementById('segmentPlayer');
            player.currentTime = res.start;
            player.ontimeupdate = () => {
                if (player.currentTime > res.end) {
                    player.pause();
                }
            };
            player.onloadedmetadata = () => {
                player.currentTime = res.start;
            };

            downloadClipBtn.style.display = "inline-block";
            downloadClipBtn.onclick = function(e) {
                e.preventDefault();

                const start = res.start;
                const end = res.end;

                const url = `http://127.0.0.1:8000/download_clip?video_id=${encodeURIComponent(videoId)}&start=${start}&end=${end}`;
                downloadClipBtn.href = url;
                downloadClipBtn.setAttribute("download", `${videoId}_clip_${Math.floor(start)}_${Math.floor(end)}.mp4`);

                window.open(url, "_blank");
            };
        }
    }
};