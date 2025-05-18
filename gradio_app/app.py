
import os
import tempfile
import requests
import gradio as gr
import scipy.io.wavfile
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('voice_chatbot_frontend')

API_URL = "http://localhost:8000/voice-chat"
REQUEST_TIMEOUT = 300  # Timeout in seconds

# Voice chat function with improved error handling
def voice_chat(audio, progress=gr.Progress()):
    if audio is None:
        return None, "⚠️ Rekaman suara diperlukan"
    
    # Update timestamp
    logger.info(f"Processing voice request")
    
    # Add progress updates
    progress(0, desc="Mengolah rekaman...")
    
    try:
        sr, audio_data = audio
        
        # Log audio details for debugging
        logger.info(f"Audio sample rate: {sr}, shape: {audio_data.shape}")
        
        # Save as .wav with unique filename
        audio_filename = f"input_{int(time.time())}.wav"
        audio_path = os.path.join(tempfile.gettempdir(), audio_filename)
        
        scipy.io.wavfile.write(audio_path, sr, audio_data)
        logger.info(f"Saved input audio to: {audio_path}")
        
        if not os.path.exists(audio_path):
            logger.error(f"Failed to save audio file at {audio_path}")
            return None, "⚠️ Gagal menyimpan rekaman"
            
        progress(0.3, desc="Mengirim ke server...")
        
        # Send to FastAPI endpoint with timeout
        try:
            logger.info(f"Sending request to {API_URL}")
            with open(audio_path, "rb") as f:
                files = {"file": (audio_filename, f, "audio/wav")}
                response = requests.post(
                    API_URL,
                    files=files,
                    timeout=REQUEST_TIMEOUT
                )
            
            logger.info(f"Response status: {response.status_code}, Content length: {len(response.content) if response.content else 0}")
            
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
            error_msg = "🕒 Waktu habis. Server terlalu lama merespons."
            return None, error_msg
            
        except requests.exceptions.ConnectionError:
            logger.error("Connection error")
            error_msg = "🔌 Koneksi ke server gagal. Pastikan server aktif di http://localhost:8000"
            return None, error_msg
            
        except Exception as e:
            logger.error(f"Request error: {str(e)}")
            error_msg = f"🔴 Kesalahan: {str(e)}"
            return None, error_msg
        
        progress(0.7, desc="Menerima jawaban...")
        
        if response.status_code == 200:
            logger.info("Request successful, processing response")
            
            # Verify content type and length
            content_type = response.headers.get('Content-Type', '')
            logger.info(f"Response Content-Type: {content_type}")
            
            if not response.content:
                logger.error("Response content is empty")
                error_msg = "⚠️ Server mengembalikan respons kosong"
                return None, error_msg
            
            # Save response audio with unique timestamp to avoid caching issues
            output_audio_path = os.path.join(tempfile.gettempdir(), f"tts_output_{int(time.time())}.wav")
            
            try:
                with open(output_audio_path, "wb") as f:
                    f.write(response.content)
                logger.info(f"Saved response audio to: {output_audio_path}")
                
                # Verify if file exists and has content
                if not os.path.exists(output_audio_path) or os.path.getsize(output_audio_path) == 0:
                    logger.error(f"Output file doesn't exist or is empty: {output_audio_path}")
                    error_msg = "⚠️ File audio respons kosong atau tidak valid"
                    return None, error_msg
                
            except Exception as e:
                logger.error(f"Failed to save response audio: {e}")
                error_msg = f"⚠️ Gagal menyimpan file audio respons: {str(e)}"
                return None, error_msg
            
            progress(1.0, desc="Selesai!")
            return output_audio_path, "✅ Jawaban siap diputar"
        else:
            logger.error(f"Server returned error status: {response.status_code}")
            try:
                error_content = response.json() if response.content else {}
                error_detail = error_content.get('message', f"Kode status: {response.status_code}")
            except:
                error_detail = f"Kode status: {response.status_code}"
                
            error_msg = f"⚠️ Error Server: {error_detail}"
            return None, error_msg
            
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        error_msg = f"⚠️ Kesalahan sistem: {str(e)}"
        return None, error_msg

# Completely new CSS design
custom_css = """
body {
    font-family: 'Poppins', 'Nunito Sans', sans-serif;
    background-color: #121f3d;
    color: #e8ebf2;
    margin: 0;
    padding: 0;
    line-height: 1.6;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Cg fill-rule='evenodd'%3E%3Cg fill='%232a3f6a' fill-opacity='0.2'%3E%3Cpath opacity='.5' d='M96 95h4v1h-4v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4h-9v4h-1v-4H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15v-9H0v-1h15V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h9V0h1v15h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9h4v1h-4v9zm-1 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm9-10v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm9-10v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm9-10v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-10 0v-9h-9v9h9zm-9-10h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9zm10 0h9v-9h-9v9z'/%3E%3Cpath d='M6 5V0H5v5H0v1h5v94h1V6h94V5H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
    background-attachment: fixed;
}

.gradio-container {
    max-width: 1200px !important;
    margin: 0 auto;
}

/* New Header Style */
.app-header {
    background: linear-gradient(135deg, #2c3e50, #4a69bd);
    padding: 25px 15px;
    border-radius: 0 0 30px 30px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    margin-bottom: 25px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.app-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100" viewBox="0 0 100 100"><rect fill="none" width="100" height="100"/><path fill="rgba(255,255,255,0.05)" d="M30,20 Q50,5 70,20 T100,40 T70,60 T30,80 T0,60 T30,40 T60,20"/></svg>');
    background-size: 150px;
    opacity: 0.3;
}

.app-logo {
    font-size: 3rem;
    font-weight: 800;
    margin: 0;
    color: #ffffff;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    letter-spacing: 2px;
    background: linear-gradient(135deg, #4a69bd, #89b9ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: glow 3s ease-in-out infinite alternate;
}

@keyframes glow {
    0% { text-shadow: 0 0 10px rgba(74, 105, 189, 0.2); }
    100% { text-shadow: 0 0 20px rgba(74, 105, 189, 0.8), 0 0 30px rgba(74, 105, 189, 0.4); }
}

.app-tagline {
    color: rgba(255, 255, 255, 0.85);
    font-size: 1.1rem;
    margin-top: 5px;
    font-weight: 400;
}

/* Card styling */
.card {
    background-color: #1e2a45;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
    border: 1px solid rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    position: relative;
    z-index: 1;
    overflow: hidden;
    height: 100%;
    min-height: 360px;
    display: flex;
    flex-direction: column;
}

.card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: linear-gradient(135deg, rgba(74, 105, 189, 0.1) 0%, rgba(74, 105, 189, 0) 70%);
    z-index: -1;
    pointer-events: none;
}

.card-header {
    display: flex;
    align-items: center;
    margin-bottom: 15px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    padding-bottom: 12px;
}

.card-icon {
    margin-right: 12px;
    font-size: 1.4rem;
    background: rgba(255, 255, 255, 0.1);
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 50%;
}

.card-title {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: #e8ebf2;
}

/* Audio player styling */
.audio-output-card {
    min-height: 360px;
}

.improved-audio-player {
    margin-top: 10px;
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.improved-audio-player audio {
    width: 100% !important;
    min-height: 50px;
    border-radius: 8px;
    background-color: rgba(0, 0, 0, 0.2);
}

/* Fix for audio controls */
audio::-webkit-media-controls-panel {
    background-color: rgba(74, 105, 189, 0.3);
}

audio::-webkit-media-controls-time-remaining-display,
audio::-webkit-media-controls-current-time-display {
    color: #e8ebf2;
}

/* Make sure audio element is fully visible */
#voice-output {
    display: block !important;
    margin-bottom: 10px;
    padding: 10px;
    min-height: 80px;
}

/* Processing indicator styling */
.processing-indicator {
    margin-top: 15px;
}

.progress-bar {
    width: 100%;
    margin-top: 10px;
}

.progress-status {
    display: flex;
    align-items: center;
    margin-bottom: 8px;
}

.progress-icon {
    margin-right: 10px;
    animation: spin 2s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.progress-text {
    color: #8bd8bd;
    font-weight: 500;
}

.progress-track {
    height: 8px;
    width: 100%;
    background-color: rgba(255, 255, 255, 0.1);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    width: 30%;
    background-color: #4a69bd;
    border-radius: 4px;
    animation: progress 1.5s infinite ease-in-out;
}

@keyframes progress {
    0% { width: 0%; }
    50% { width: 50%; }
    100% { width: 100%; }
}

/* Status container positioning */
.status-container {
    margin-top: auto;
}

/* Input card specific styling */
.input-card {
    position: relative;
}

/* Submit button styling */
.submit-button {
    width: 100%;
    margin-top: 15px;
    padding: 12px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 1.1rem !important;
    background: linear-gradient(135deg, #4a69bd, #3a6ea5) !important;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2) !important;
    transition: all 0.3s ease !important;
}

.submit-button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 15px rgba(0, 0, 0, 0.3) !important;
    background: linear-gradient(135deg, #5579cd, #4a7eb5) !important;
}

/* Recording UI */
.recording-status {
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 12px;
    padding: 12px;
    margin: 15px 0;
    display: flex;
    align-items: center;
    justify-content: center;
}

.ready-to-record {
    color: #8bd8bd;
    font-weight: 500;
    display: flex;
    align-items: center;
}

.now-recording {
    color: #ff6b6b;
    font-weight: 600;
    display: flex;
    align-items: center;
    animation: pulse 1.5s infinite;
}

.status-icon {
    margin-right: 10px;
    font-size: 1.2rem;
}

@keyframes pulse {
    0% { opacity: 1; }
    50% { opacity: 0.6; }
    100% { opacity: 1; }
}

/* Status message */
.status-box {
    margin-top: 15px;
    padding: 12px;
    border-radius: 12px;
    text-align: center;
    font-weight: 500;
    font-size: 0.95rem;
}

.status-error {
    background-color: rgba(220, 53, 69, 0.2);
    color: #ff8a8a;
    border-left: 3px solid #dc3545;
}

.status-success {
    background-color: rgba(25, 135, 84, 0.2);
    color: #8bd8bd;
    border-left: 3px solid #198754;
}

.status-warning {
    background-color: rgba(255, 193, 7, 0.2);
    color: #ffd166;
    border-left: 3px solid #ffc107;
}

/* Footer */
.app-footer {
    text-align: center;
    margin-top: 30px;
    padding: 20px 15px;
    color: rgba(255, 255, 255, 0.6);
    background-color: rgba(0, 0, 0, 0.2);
    border-radius: 20px 20px 0 0;
}

/* Button styling */
.button-container {
    display: flex;
    gap: 10px;
}

/* Responsive */
@media (max-width: 768px) {
    .app-logo {
        font-size: 2rem;
    }
    
    .card {
        padding: 15px;
    }
}
"""

# Create a completely different theme
theme = gr.themes.Base().set(
    body_background_fill="#121f3d",
    body_text_color="#e8ebf2",
    block_background_fill="#1e2a45",
    block_border_color="rgba(255, 255, 255, 0.1)",
    input_background_fill="#2d3b56",
    button_primary_background_fill="#4a69bd",
    button_primary_background_fill_hover="#3a6ea5",
    button_primary_text_color="#FFFFFF",
    button_secondary_background_fill="#2d3b56",
    button_secondary_background_fill_hover="#3a4c6d",
    button_secondary_text_color="#e8ebf2"
)

# Recording indicator state function
def recording_state(recording=False):
    if recording:
        return gr.update(visible=True), gr.update(visible=False)
    else:
        return gr.update(visible=False), gr.update(visible=True)

# UI with Gradio Blocks - Completely Redesigned Version with side-by-side layout
with gr.Blocks(theme=theme, css=custom_css) as demo:
    # New Header
    gr.HTML("""
    <div class="app-header">
        <h1 class="app-logo">BICARA</h1>
        <p class="app-tagline">Asisten Pintar berbahasa Indonesia</p>
    </div>
    """)
    
    # Main content with two columns side by side
    with gr.Row(equal_height=True):
        # LEFT COLUMN - Voice input
        with gr.Column(scale=1):
            # Voice input card
            with gr.Group(elem_classes="card input-card"):
                gr.HTML("""
                <div class="card-header">
                    <div class="card-icon">🎙️</div>
                    <h2 class="card-title">Rekam Pesan Anda</h2>
                </div>
                """)
                
                # Audio input with microphone
                audio_input = gr.Audio(
                    sources="microphone",
                    type="numpy",
                    elem_id="voice-input",
                    streaming=False
                )
                
                # Recording indicators
                with gr.Group(elem_classes="recording-status"):
                    ready_indicator = gr.HTML("""
                    <div class="ready-to-record">
                        <span class="status-icon">⚪</span> Siap merekam suara Anda
                    </div>
                    """, visible=True)
                    
                    recording_active = gr.HTML("""
                    <div class="now-recording">
                        <span class="status-icon">⦿</span> Merekam suara...
                    </div>
                    """, visible=False)
                
                # Submit button
                submit_btn = gr.Button(
                    "📤 Kirim Pesan", 
                    variant="primary",
                    elem_classes="submit-button"
                )
                
                # Status message display in a separate container
                with gr.Group(elem_classes="status-container"):
                    status_msg = gr.HTML(
                        """<div class="status-box">Sistem siap menerima pesan suara</div>"""
                    )
                
                # Processing indicator that won't overlap
                with gr.Group(elem_classes="processing-indicator", visible=False) as processing_indicator:
                    gr.HTML("""
                    <div class="progress-bar">
                        <div class="progress-status">
                            <div class="progress-icon">⏳</div>
                            <div class="progress-text">Memproses permintaan...</div>
                        </div>
                        <div class="progress-track">
                            <div class="progress-fill"></div>
                        </div>
                    </div>
                    """)
        
        # RIGHT COLUMN - Voice output
        with gr.Column(scale=1):
            # Voice output card
            with gr.Group(elem_classes="card audio-output-card"):
                gr.HTML("""
                <div class="card-header">
                    <div class="card-icon">🔊</div>
                    <h2 class="card-title">Respon Asisten</h2>
                </div>
                """)
                
                # Audio output with improved styling
                audio_output = gr.Audio(
                    type="filepath",
                    elem_id="voice-output",
                    show_label=False,
                    autoplay=False,
                    container=True,
                    elem_classes="improved-audio-player"
                )
    
    # New Footer
    gr.HTML("""
    <div class="app-footer">
        <p>BICARA © 2025 | Teknologi Asisten Suara Cerdas Indonesia</p>
    </div>
    """)
    
    # Define event handlers
    def update_status(message, is_error=False, is_warning=False):
        if is_error:
            return f'<div class="status-box status-error">{message}</div>'
        elif is_warning:
            return f'<div class="status-box status-warning">{message}</div>'
        else:
            return f'<div class="status-box status-success">{message}</div>'
    
    # Processing indicator control functions
    def show_processing():
        return gr.update(visible=True)
        
    def hide_processing():
        return gr.update(visible=False)
    
    # Recording start event
    audio_input.start_recording(
        fn=lambda: recording_state(True),
        outputs=[recording_active, ready_indicator]
    )
    
    # Recording stop event
    audio_input.stop_recording(
        fn=lambda: recording_state(False),
        outputs=[recording_active, ready_indicator]
    )
    
    # Submit button click with processing indicator
    submit_btn.click(
        fn=show_processing,
        outputs=[processing_indicator]
    ).then(
        fn=voice_chat,
        inputs=[audio_input],
        outputs=[audio_output, status_msg]
    ).then(
        fn=hide_processing,
        outputs=[processing_indicator]
    )

# Launch the app
if __name__ == "__main__":
    logger.info("Starting Voice Chatbot Frontend")
    demo.launch()