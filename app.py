import streamlit as st
import streamlit.components.v1 as components
import base64
import tempfile
import whisper
import os

# Page config
st.set_page_config(page_title="🎙️ Real-Time Voice Transcription", layout="centered")
st.markdown(
    """
    <style>
    body { background-color: #f5f7fa; }
    .card {
        max-width: 500px;
        margin: auto;
        padding: 2rem;
        background: white;
        border-radius: 12px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    .mic-btn {
        font-size: 24px;
        padding: 1rem 2rem;
        border-radius: 50px;
        border: none;
        cursor: pointer;
        margin: 0.5rem;
    }
    .mic-start { background-color: #ff4b5c; color: white; }
    .mic-stop { background-color: #6c757d; color: white; }
    .status {
        font-weight: bold;
        margin-top: 1rem;
    }
    .status.recording { color: red; }
    .status.idle { color: grey; }
    @media (max-width: 600px) {
        .mic-btn { font-size: 18px; padding: 0.8rem 1.5rem; }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Recorder HTML/JS
record_html = """
<div class="card">
  <h2>🎤 Real-Time Voice Recorder</h2>
  <audio id="rec" controls></audio><br>
  <button id="start" class="mic-btn mic-start">Start Recording ⏺</button>
  <button id="stop" class="mic-btn mic-stop">Stop Recording ⏹</button>
  <p id="status" class="status idle">Status: Idle</p>
</div>

<script>
let mediaRecorder;
let audioChunks = [];
const startBtn = document.getElementById("start");
const stopBtn = document.getElementById("stop");
const statusText = document.getElementById("status");
const rec = document.getElementById("rec");

startBtn.onclick = async () => {
  const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
  mediaRecorder = new MediaRecorder(stream);
  mediaRecorder.ondataavailable = e => audioChunks.push(e.data);
  mediaRecorder.onstop = () => {
    const blob = new Blob(audioChunks, { type: 'audio/webm' });
    audioChunks = [];
    const reader = new FileReader();
    reader.readAsDataURL(blob);
    reader.onloadend = () => {
      const base64data = reader.result;
      window.parent.postMessage({ audio: base64data }, "*");
    };
    rec.src = URL.createObjectURL(blob);
  };
  mediaRecorder.start();
  statusText.textContent = "Status: Recording...";
  statusText.className = "status recording";
};

stopBtn.onclick = () => {
  mediaRecorder.stop();
  statusText.textContent = "Status: Idle";
  statusText.className = "status idle";
};
</script>
"""

components.html(record_html, height=350)

# Handle audio from frontend
audio_params = st.experimental_get_query_params().get("audio")
if audio_params:
    header, data = audio_params[0].split(",", 1)
    audio_bytes = base64.b64decode(data)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
        temp_audio.write(audio_bytes)
        temp_path = temp_audio.name

    # Whisper transcription
    model = whisper.load_model("base")
    result = model.transcribe(temp_path)

    st.subheader("📝 Live Transcription")
    st.write(result["text"])

    os.remove(temp_path)
